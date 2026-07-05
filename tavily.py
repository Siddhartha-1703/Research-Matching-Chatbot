import requests

def web_search_tavily(query, limit=5):
    # Lightweight placeholder wrapper for Tavily; replace with real API integration.
    # For now, perform a simple web search via DuckDuckGo JSON.
    try:
        params = {'q': query, 'format': 'json'}
        r = requests.get('https://api.duckduckgo.com/', params=params, timeout=10)
        data = r.json()
        snippets = []
        if data.get('AbstractText'):
            snippets.append(data['AbstractText'])
        if data.get('Answer'):
            snippets.append(data['Answer'])
        if data.get('Definition'):
            snippets.append(data['Definition'])
        if data.get('Heading'):
            snippets.append(data['Heading'])

        for item in data.get('Results', [])[:limit]:
            if isinstance(item, dict):
                txt = item.get('Text') or item.get('Result')
                if txt:
                    snippets.append(txt)
        for item in data.get('RelatedTopics', [])[:limit]:
            if isinstance(item, dict):
                txt = item.get('Text') or item.get('Result')
                if txt:
                    snippets.append(txt)

        cleaned = [s for s in snippets if s]
        if cleaned:
            return cleaned[:limit]
        return [f'No live result for "{query}" (Tavily mock)']
    except Exception:
        return [f'No live result for "{query}" (Tavily mock)']
