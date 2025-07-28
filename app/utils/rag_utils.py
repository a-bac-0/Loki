# utils/rag_utils.py

import os
import requests
from typing import List, Optional, Dict, Any
from langchain_ollama import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredWordDocumentLoader
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
import tempfile

def get_embeddings_model():
    """
    Obtiene el modelo de embeddings configurado.
    """
    try:
        # Verificar qué modelos están disponibles
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            available_models = response.json()
            model_names = [model['name'] for model in available_models.get('models', [])]
            
            # Lista de modelos de embeddings preferidos (en orden de preferencia)
            preferred_embedding_models = [
                'nomic-embed-text',
                'nomic-embed-text:latest',
                'all-minilm',
                'all-minilm:latest',
                'llama2',  # Fallback
                'llama3',  # Fallback
            ]
            
            # Buscar el primer modelo disponible
            selected_model = None
            for model in preferred_embedding_models:
                if model in model_names or f"{model}:latest" in model_names:
                    selected_model = model
                    break
            
            if not selected_model:
                # Si no hay modelos específicos de embeddings, usar el primer disponible
                selected_model = model_names[0] if model_names else 'llama2'
            
            print(f"✅ Usando modelo de embeddings: {selected_model}")
            
            return OllamaEmbeddings(
                model=selected_model,
                base_url="http://localhost:11434"
            )
        else:
            print("⚠️ No se pudo conectar con Ollama, usando modelo por defecto")
            return OllamaEmbeddings(
                model="llama2",
                base_url="http://localhost:11434"
            )
            
    except Exception as e:
        print(f"⚠️ Error obteniendo modelo de embeddings: {e}")
        print("Usando modelo por defecto: llama2")
        return OllamaEmbeddings(
            model="llama2",
            base_url="http://localhost:11434"
        )

def process_uploaded_file(uploaded_file) -> List[Document]:
    """
    Procesa un archivo subido y lo convierte en chunks de documentos.
    """
    try:
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        # Cargar documento según el tipo
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'pdf':
            loader = PyPDFLoader(tmp_file_path)
        elif file_extension == 'txt':
            loader = TextLoader(tmp_file_path, encoding='utf-8')
        elif file_extension in ['docx', 'doc']:
            loader = UnstructuredWordDocumentLoader(tmp_file_path)
        else:
            raise ValueError(f"Tipo de archivo no soportado: {file_extension}")
        
        # Cargar documento
        documents = loader.load()
        
        # Agregar metadatos
        for doc in documents:
            doc.metadata.update({
                'filename': uploaded_file.name,
                'file_type': file_extension
            })
        
        # Dividir en chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        chunks = text_splitter.split_documents(documents)
        
        # Limpiar archivo temporal
        os.unlink(tmp_file_path)
        
        print(f"✅ Archivo procesado: {len(chunks)} chunks generados")
        return chunks
        
    except Exception as e:
        print(f"❌ Error procesando archivo: {e}")
        # Limpiar archivo temporal si existe
        try:
            os.unlink(tmp_file_path)
        except:
            pass
        return []

def create_vector_store(chunks: List[Document]):
    """
    Crea un vector store a partir de los chunks de documentos.
    """
    try:
        if not chunks:
            print("⚠️ No hay chunks para procesar")
            return None
        
        # Obtener modelo de embeddings
        embeddings = get_embeddings_model()
        
        # Extraer textos y metadatos
        texts = [doc.page_content for doc in chunks]
        metadatas = [doc.metadata for doc in chunks]
        
        # Crear vector store
        vector_store = FAISS.from_texts(
            texts=texts,
            embedding=embeddings,
            metadatas=metadatas
        )
        
        print(f"✅ Vector store creado con {len(texts)} documentos")
        return vector_store
        
    except Exception as e:
        print(f"❌ Error creando vector store: {e}")
        return None

def search_documents(vector_store, query: str, k: int = 3) -> List[Document]:
    """
    Busca documentos relevantes en el vector store.
    """
    try:
        # Verificar que vector_store es un objeto FAISS válido
        if vector_store is None:
            print("⚠️ Vector store no está inicializado")
            return []
        
        if isinstance(vector_store, str):
            print("❌ Error: se pasó un string en lugar de un vector store")
            return []
        
        # Realizar búsqueda por similitud
        relevant_docs = vector_store.similarity_search(
            query=query,
            k=k
        )
        
        print(f"✅ Encontrados {len(relevant_docs)} documentos relevantes")
        return relevant_docs
        
    except Exception as e:
        print(f"❌ Error en búsqueda: {e}")
        return []

def format_context(relevant_docs: List[Document]) -> str:
    """
    Formatea los documentos relevantes en un contexto para el LLM.
    """
    if not relevant_docs:
        return ""
    
    context_parts = []
    for i, doc in enumerate(relevant_docs, 1):
        content = doc.page_content.strip()
        filename = doc.metadata.get('filename', 'Documento desconocido')
        
        context_parts.append(f"Documento {i} ({filename}):\n{content}")
    
    return "\n\n".join(context_parts)

def get_saved_documents() -> List[Dict]:
    """
    Obtiene la lista de documentos guardados en la carpeta docs.
    """
    try:
        docs_dir = os.path.join(os.path.dirname(__file__), "..", "docs")
        
        if not os.path.exists(docs_dir):
            os.makedirs(docs_dir)
            return []
        
        documents = []
        for filename in os.listdir(docs_dir):
            if filename.endswith(('.pdf', '.txt', '.docx', '.doc')):
                file_path = os.path.join(docs_dir, filename)
                file_stat = os.stat(file_path)
                
                documents.append({
                    'filename': filename,
                    'size': file_stat.st_size,
                    'modified': file_stat.st_mtime
                })
        
        return sorted(documents, key=lambda x: x['modified'], reverse=True)
        
    except Exception as e:
        print(f"❌ Error obteniendo documentos guardados: {e}")
        return []

def load_saved_document(filename: str) -> Optional[List[Document]]:
    """
    Carga un documento guardado desde la carpeta docs.
    """
    try:
        docs_dir = os.path.join(os.path.dirname(__file__), "..", "docs")
        file_path = os.path.join(docs_dir, filename)
        
        if not os.path.exists(file_path):
            print(f"❌ Archivo no encontrado: {filename}")
            return None
        
        # Simular uploaded_file para reutilizar process_uploaded_file
        class MockUploadedFile:
            def __init__(self, path):
                self.name = os.path.basename(path)
                with open(path, 'rb') as f:
                    self._content = f.read()
            
            def getvalue(self):
                return self._content
        
        mock_file = MockUploadedFile(file_path)
        return process_uploaded_file(mock_file)
        
    except Exception as e:
        print(f"❌ Error cargando documento guardado: {e}")
        return None

def delete_saved_document(filename: str) -> bool:
    """
    Elimina un documento guardado de la carpeta docs.
    """
    try:
        docs_dir = os.path.join(os.path.dirname(__file__), "..", "docs")
        file_path = os.path.join(docs_dir, filename)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"✅ Documento eliminado: {filename}")
            return True
        else:
            print(f"⚠️ Archivo no encontrado: {filename}")
            return False
            
    except Exception as e:
        print(f"❌ Error eliminando documento: {e}")
        return False