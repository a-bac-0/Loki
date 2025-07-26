from langchain.chains import RetrievalQA
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.llms import Ollama  # or OpenAI, etc.
from langchain.vectorstores import Chroma


def generate_scientific_content(user_query):
    # Setup embeddings and vectorstore
    import os

    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    # Use absolute path for persist_directory
    persist_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "data", "arxiv_papers")
    )
    if not os.path.exists(persist_dir):
        raise FileNotFoundError(
            f"Vectorstore directory not found: {persist_dir}. Please run the ingestion script to create the vectorstore."
        )
    db = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
    retriever = db.as_retriever(search_kwargs={"k": 3})
    llm = Ollama(model="llama2")  # or your preferred LLM
    chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    result = chain.run(user_query)
    return result
