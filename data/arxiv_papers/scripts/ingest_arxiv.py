
import os
from langchain.vectorstores import Chroma
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.docstore.document import Document

# --- NEW: Fetch real arXiv abstracts using the 'arxiv' package ---
try:
    import arxiv
except ImportError:
    raise ImportError("Please install the 'arxiv' package: pip install arxiv")

def fetch_arxiv_docs(query="quantum computing", max_results=5):
    search = arxiv.Search(query=query, max_results=max_results, sort_by=arxiv.SortCriterion.SubmittedDate)
    docs = []
    for result in search.results():
        abstract = result.summary
        title = result.title
        url = result.entry_id
        docs.append(Document(page_content=abstract, metadata={"title": title, "url": url}))
    return docs

# You can change the query and max_results as needed
docs = fetch_arxiv_docs(query="artificial intelligence", max_results=8)

embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
persist_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'arxiv_papers'))

os.makedirs(persist_dir, exist_ok=True)

db = Chroma.from_documents(docs, embedding_function=embeddings, persist_directory=persist_dir)
db.persist()

print(f"Vectorstore created at {persist_dir}")