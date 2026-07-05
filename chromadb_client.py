import os
# Silence Hugging Face Hub telemetry/progress warnings and tqdm output.
os.environ.setdefault('HUGGINGFACE_HUB_DISABLE_TELEMETRY', '1')
os.environ.setdefault('HF_HUB_DISABLE_PROGRESS_BARS', '1')
os.environ.setdefault('TRANSFORMERS_NO_ADVISORY_WARNINGS', '1')
os.environ.setdefault('TQDM_DISABLE', '1')

try:
    import chromadb
    from chromadb.config import Settings
    from chromadb.utils import embedding as chroma_embedding
    CHROMADB_AVAILABLE = True
except Exception:
    chromadb = None
    CHROMADB_AVAILABLE = False

from sentence_transformers import SentenceTransformer
import numpy as np

EMBED_MODEL = SentenceTransformer('all-MiniLM-L6-v2')


class ChromaFallback:
    def __init__(self):
        self.profiles = []
        self.embs = None

    def add_profiles(self, docs):
        self.profiles.extend(docs)
        texts = [d['text'] for d in self.profiles]
        self.embs = EMBED_MODEL.encode(texts, convert_to_numpy=True)

    def query(self, q, k=5):
        q_emb = EMBED_MODEL.encode([q], convert_to_numpy=True)[0]
        sims = (self.embs @ q_emb) / (
            (np.linalg.norm(self.embs, axis=1) * np.linalg.norm(q_emb)) + 1e-9
        )
        idx = np.argsort(-sims)[:k]
        results = []
        for i in idx:
            p = self.profiles[i].copy()
            p['score'] = float(sims[i])
            results.append(p)
        return results


class ChromaClient:
    def __init__(self, use_chroma=True):
        if CHROMADB_AVAILABLE and use_chroma:
            self.client = chromadb.Client(Settings())
            self.col = None
        else:
            self.client = None
            self.col = None
            self.fallback = ChromaFallback()

    def add_profiles(self, docs, collection_name='faculty'):
        if CHROMADB_AVAILABLE:
            if collection_name not in [c.name for c in self.client.list_collections()]:
                self.col = self.client.create_collection(name=collection_name)
            else:
                self.col = self.client.get_collection(collection_name)
            texts = [d['text'] for d in docs]
            ids = [d['id'] for d in docs]
            emb = EMBED_MODEL.encode(texts).tolist()
            self.col.add(ids=ids, documents=texts, metadatas=docs, embeddings=emb)
        else:
            self.fallback.add_profiles(docs)

    def query(self, q, k=5):
        if CHROMADB_AVAILABLE:
            res = self.col.query(query_texts=[q], n_results=k)
            results = []
            for ids, docs, scores in zip(res['ids'][0], res['metadatas'][0], res['distances'][0]):
                m = docs.copy()
                m['id'] = ids
                m['score'] = float(1.0 - scores)
                results.append(m)
            return results
        else:
            return self.fallback.query(q, k=k)
