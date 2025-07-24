import requests

def fetch_arxiv_papers(query, max_results=5):
    url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}"
    response = requests.get(url)
    # Parse XML response to extract titles/abstracts (use xml.etree.ElementTree)
    # Return a list of dicts: [{'title': ..., 'abstract': ...}, ...]
    return response.text  # For now, just return raw XML