import requests

def search_semantic_scholar(query, limit=5):
    # Placeholder: user should set SEMANTIC_SCHOLAR_API key and endpoint.
    # This mock returns static structure suitable for integration.
    # Replace with real API calls to Semantic Scholar when API key available.
    return [
        {'title': f'Mock paper about {query} #{i+1}', 'abstract': 'Abstract...', 'year':2024, 'citations': 10-i}
        for i in range(limit)
    ]
