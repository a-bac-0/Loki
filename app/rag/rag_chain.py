from langchain.chains import RetrievalQA
from langchain.llms import Ollama  # or OpenAI, etc.
from .retriever import retrieve

def generate_scientific_content(user_query):
    docs = retrieve(user_query)
    llm = Ollama(model="llama2")  # or your preferred LLM
    chain = RetrievalQA.from_chain_type(llm=llm, retriever=docs)
    result = chain.run(user_query)
    return result