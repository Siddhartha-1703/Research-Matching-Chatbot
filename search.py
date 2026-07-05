from chromadb_client import ChromaClient
from tavily import web_search_tavily
from semantic_scholar import search_semantic_scholar
import os
import re


def _parse_profile(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    name = lines[0] if lines else ''
    areas = ''
    workload = None
    pubs = []
    profile_lines = []
    in_pubs = False
    for L in lines[1:]:
        if L.startswith('Research Areas:'):
            areas = L.split(':', 1)[1].strip()
            continue
        if L.startswith('Selected Publications:'):
            in_pubs = True
            continue
        if in_pubs:
            if L.startswith('-'):
                pubs.append(L.lstrip('-').strip())
                continue
            else:
                in_pubs = False
        m = re.search(r'Workload:\s*(\d+)', L)
        if m:
            workload = int(m.group(1))
            continue
        profile_lines.append(L)

    return {
        'name': name,
        'areas': areas,
        'workload': workload if workload is not None else 0,
        'publications': pubs,
        'text': text
    }


class ResearchMatcher:
    def __init__(self, data_dir='data/faculty'):
        self.client = ChromaClient()
        self.profiles = {}
        self._load_profiles(data_dir)

    def _load_profiles(self, data_dir):
        docs = []
        if not os.path.exists(data_dir):
            return
        for fn in sorted(os.listdir(data_dir)):
            path = os.path.join(data_dir, fn)
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read().strip()
            meta = _parse_profile(text)
            doc = {'id': fn, 'text': text, 'name': meta['name'], 'areas': meta['areas'], 'workload': meta['workload'], 'publications': meta['publications']}
            docs.append(doc)
            self.profiles[fn] = doc
        if docs:
            self.client.add_profiles(docs)

    def find_faculty(self, query, k=5):
        results = self.client.query(query, k=k)
        cleaned = []
        for r in results:
            fid = r.get('id')
            meta = self.profiles.get(fid, {})
            cleaned.append({'id': fid, 'name': meta.get('name', fid), 'areas': meta.get('areas',''), 'score': r.get('score',0.0)})
        return cleaned

    def get_faculty_detail(self, faculty_id):
        if faculty_id in self.profiles:
            p = self.profiles[faculty_id]
            return {
                'id': faculty_id,
                'name': p.get('name'),
                'areas': p.get('areas'),
                'workload': p.get('workload'),
                'publications': p.get('publications'),
                'profile': p.get('text')
            }
        return {'error':'Faculty detail not found.'}

    def suggest_collaborators(self, faculty_id, k=3):
        if faculty_id not in self.profiles:
            return []
        target = self.profiles[faculty_id]
        # semantic search using profile text to find similar faculty
        candidates = self.client.query(target['text'], k=10)
        out = []
        for c in candidates:
            cid = c.get('id')
            if cid == faculty_id:
                continue
            meta = self.profiles.get(cid, {})
            # Simple availability adjustment: prefer lower workload
            workload = meta.get('workload', 0)
            avail_factor = max(0.0, 1.0 - (workload / 10.0))
            score = c.get('score', 0.0) * avail_factor
            out.append({'id': cid, 'name': meta.get('name', cid), 'areas': meta.get('areas',''), 'score': score, 'workload': workload})
        out = sorted(out, key=lambda x: -x['score'])[:k]
        return out

    def search_trends(self, query):
        return web_search_tavily(query, limit=5)

    def search_papers(self, query):
        return search_semantic_scholar(query, limit=5)
