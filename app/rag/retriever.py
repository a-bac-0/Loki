from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.vectorstores import Chroma


def retrieve(query):
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    db = Chroma(persist_directory="arxiv_papers", embedding_function=embeddings)
    docs = db.similarity_search(query, k=3)
    return docs
