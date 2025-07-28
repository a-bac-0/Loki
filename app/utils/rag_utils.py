# app/utils/rag_utils.py

import streamlit as st
import tempfile
import os
from langchain_ollama import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredWordDocumentLoader
from langchain.schema import Document

@st.cache_resource
def get_embeddings_model(ollama_url="http://localhost:11434"):
    """Inicializa el modelo de embeddings de Ollama"""
    try:
        return OllamaEmbeddings(
            base_url=ollama_url,
            model="nomic-embed-text"  # Modelo recomendado para embeddings
        )
    except:
        # Fallback a un modelo más común
        return OllamaEmbeddings(
            base_url=ollama_url,
            model="llama3.2"
        )

def process_uploaded_file(uploaded_file, save_to_docs=True):
    """Procesa archivos subidos y extrae el texto
    
    Args:
        uploaded_file: Archivo subido por Streamlit
        save_to_docs: Si True, guarda el archivo en app/docs permanentemente
    """
    try:
        if save_to_docs:
            # Guardar archivo en la carpeta docs
            import os
            from datetime import datetime
            
            # Crear nombre único con timestamp para evitar conflictos
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            original_name = uploaded_file.name
            name_without_ext = os.path.splitext(original_name)[0]
            file_extension = os.path.splitext(original_name)[1]
            
            # Crear nombre único: nombre_original_timestamp.extension
            unique_filename = f"{name_without_ext}_{timestamp}{file_extension}"
            
            # Ruta completa donde guardar el archivo
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Volver al directorio app
            docs_dir = os.path.join(current_dir, "docs")
            
            # Crear carpeta docs si no existe
            os.makedirs(docs_dir, exist_ok=True)
            
            # Guardar archivo permanentemente
            file_path = os.path.join(docs_dir, unique_filename)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            
            # Usar la ruta permanente
            tmp_file_path = file_path
            
            # Notificar al usuario
            st.success(f"📁 Archivo guardado como: `{unique_filename}`")
            
        else:
            # Crear archivo temporal (comportamiento original)
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
        
        # Cargar documento según el tipo
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'pdf':
            try:
                # Intentar importar pypdf primero
                import pypdf
                loader = PyPDFLoader(tmp_file_path)
            except ImportError:
                st.error("❌ pypdf no está instalado. Ejecuta: pip install pypdf")
                return []
        elif file_extension == 'txt':
            loader = TextLoader(tmp_file_path, encoding='utf-8')
        elif file_extension in ['docx', 'doc']:
            try:
                loader = UnstructuredWordDocumentLoader(tmp_file_path)
            except ImportError:
                st.error("❌ unstructured no está instalado. Ejecuta: pip install unstructured")
                return []
        else:
            # Para otros tipos, intentar como texto plano
            content = uploaded_file.getvalue().decode('utf-8', errors='ignore')
            return [Document(page_content=content, metadata={"source": uploaded_file.name})]
        
        documents = loader.load()
        
        # Actualizar metadata con información del archivo
        for doc in documents:
            if save_to_docs:
                doc.metadata.update({
                    "source": unique_filename,  # Usar el nombre único si se guardó
                    "original_name": original_name,
                    "file_path": tmp_file_path if save_to_docs else None
                })
            else:
                doc.metadata.update({
                    "source": uploaded_file.name
                })
        
        # Limpiar archivo temporal solo si no se guardó permanentemente
        if not save_to_docs:
            try:
                os.unlink(tmp_file_path)
            except:
                pass  # Ignorar errores al limpiar temporales
        
        return documents
        
    except Exception as e:
        st.error(f"Error procesando archivo {uploaded_file.name}: {str(e)}")
        # Mostrar comando específico según el tipo de archivo
        if uploaded_file.name.lower().endswith('.pdf'):
            st.code("pip install pypdf")
        elif uploaded_file.name.lower().endswith(('.docx', '.doc')):
            st.code("pip install unstructured python-docx")
        return []

def create_vector_store(documents, embeddings):
    """Crea un vector store a partir de documentos"""
    if not documents:
        return None
    
    # Dividir documentos en chunks más pequeños
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    
    splits = text_splitter.split_documents(documents)
    
    # Crear vector store con FAISS
    vectorstore = FAISS.from_documents(splits, embeddings)
    
    return vectorstore

def search_documents(query, vectorstore, k=3):
    """Busca documentos relevantes usando similaridad semántica"""
    if not vectorstore:
        return []
    
    try:
        relevant_docs = vectorstore.similarity_search(query, k=k)
        return relevant_docs
    except Exception as e:
        st.error(f"Error en búsqueda: {str(e)}")
        return []

def format_context(relevant_docs):
    """Formatea documentos relevantes como contexto"""
    if not relevant_docs:
        return ""
    
    context_parts = []
    for i, doc in enumerate(relevant_docs, 1):
        source = doc.metadata.get('source', 'Documento desconocido')
        content = doc.page_content.strip()
        context_parts.append(f"Fuente {i} ({source}):\n{content}")
    
    return "\n\n".join(context_parts)

def get_saved_documents():
    """Obtiene la lista de documentos guardados en app/docs"""
    import os
    import glob
    from datetime import datetime
    
    try:
        # Obtener ruta de la carpeta docs
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        docs_dir = os.path.join(current_dir, "docs")
        
        if not os.path.exists(docs_dir):
            return []
        
        # Buscar todos los archivos en la carpeta docs
        supported_extensions = ['*.pdf', '*.txt', '*.docx', '*.doc']
        all_files = []
        
        for extension in supported_extensions:
            files = glob.glob(os.path.join(docs_dir, extension))
            all_files.extend(files)
        
        # Crear lista con información de archivos
        docs_info = []
        for file_path in all_files:
            filename = os.path.basename(file_path)
            size = os.path.getsize(file_path)
            modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            
            docs_info.append({
                'filename': filename,
                'path': file_path,
                'size': size,
                'modified': modified_time,
                'size_mb': size / (1024 * 1024)
            })
        
        # Ordenar por fecha de modificación (más recientes primero)
        docs_info.sort(key=lambda x: x['modified'], reverse=True)
        
        return docs_info
        
    except Exception as e:
        st.error(f"Error obteniendo documentos guardados: {str(e)}")
        return []

def load_saved_document(file_path):
    """Carga un documento guardado desde app/docs"""
    try:
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            try:
                import pypdf
                loader = PyPDFLoader(file_path)
            except ImportError:
                st.error("❌ pypdf no está instalado. Ejecuta: pip install pypdf")
                return []
        elif file_extension == '.txt':
            loader = TextLoader(file_path, encoding='utf-8')
        elif file_extension in ['.docx', '.doc']:
            try:
                loader = UnstructuredWordDocumentLoader(file_path)
            except ImportError:
                st.error("❌ unstructured no está instalado. Ejecuta: pip install unstructured")
                return []
        else:
            # Para otros tipos, intentar como texto plano
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return [Document(page_content=content, metadata={"source": os.path.basename(file_path)})]
        
        documents = loader.load()
        
        # Actualizar metadata con información del archivo guardado
        for doc in documents:
            doc.metadata.update({
                "source": os.path.basename(file_path),
                "file_path": file_path
            })
        
        return documents
        
    except Exception as e:
        st.error(f"Error cargando documento {file_path}: {str(e)}")
        return []

def delete_saved_document(file_path):
    """Elimina un documento guardado de app/docs"""
    try:
        import os
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        st.error(f"Error eliminando archivo: {str(e)}")
        return False
