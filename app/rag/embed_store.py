from sentence_transformers import SentenceTransformer
import chromadb

def embed_and_store(papers):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    client = chromadb.Client()
    collection = client.create_collection("arxiv_papers")
    for paper in papers:
        embedding = model.encode(paper['abstract'])
        collection.add(
            embeddings=[embedding],
            documents=[paper['abstract']],
            metadatas=[{'title': paper['title']}]
        )