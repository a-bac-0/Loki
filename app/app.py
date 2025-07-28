# app/app.py - Aplicación simplificada sin generación de imágenes

import os
import sys
import warnings
import streamlit as st
import requests
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredWordDocumentLoader
from langchain.schema import Document
import tempfile
import uuid
import time
from datetime import datetime

# Añadir el directorio actual al path para importaciones locales
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Suprimir advertencias innecesarias
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=RuntimeWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)

# Importar utilidades locales
try:
    from utils.model_utils import get_available_models, get_model_names, get_model_info, get_best_model
    from utils.rag_utils import (
        get_embeddings_model, 
        process_uploaded_file, 
        create_vector_store,
        search_documents,
        format_context,
        get_saved_documents,
        load_saved_document,
        delete_saved_document
    )
    print("✅ Utilidades locales importadas correctamente")
except ImportError as e:
    print(f"⚠️ Error importando utilidades locales: {e}")
    # Definir funciones dummy para evitar errores
    def get_available_models(*args, **kwargs): return []
    def get_model_names(*args, **kwargs): return []
    def get_model_info(*args, **kwargs): return {"speed": "Unknown", "quality": "Unknown", "description": "Unknown", "type": "Unknown"}
    def get_best_model(*args, **kwargs): return "llama3"

# Cargar variables de entorno
load_dotenv()

def main():
    """Función principal de la aplicación"""
    
    # Configuración inicial de Streamlit
    st.set_page_config(
        page_title="Asistente IA Local - F5",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Verificar disponibilidad de Ollama
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        ollama_disponible = response.status_code == 200
    except:
        ollama_disponible = False
    
    if not ollama_disponible:
        st.error("❌ **Ollama no está disponible**")
        st.write("Por favor, asegúrate de que Ollama esté instalado y ejecutándose:")
        st.code("ollama serve", language="bash")
        st.stop()
    
    # Título principal
    st.title("🤖 Asistente IA Local - F5")
    st.write("### Análisis de documentos con Retrieval-Augmented Generation (RAG)")
    st.info("ℹ️ **Versión simplificada** - Solo funcionalidad de texto y RAG")
    
    # Inicializar estado de sesión
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = None
    if "processed_docs" not in st.session_state:
        st.session_state.processed_docs = []
    
    # Sidebar para configuración
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        # Selección de modelo
        try:
            available_models = get_available_models()
            model_names = get_model_names(available_models)
            
            if model_names:
                # Buscar el mejor modelo disponible como default
                best_model = get_best_model(available_models)
                default_index = 0
                
                # Buscar el índice del mejor modelo en la lista
                for i, model in enumerate(model_names):
                    if best_model in model:
                        default_index = i
                        break
                
                selected_model = st.selectbox(
                    "🧠 Modelo LLM:",
                    model_names,
                    index=default_index,
                    help="Selecciona el modelo de lenguaje a utilizar"
                )
                
                # Mostrar información del modelo
                model_info = get_model_info(selected_model)
                if model_info:
                    st.markdown(f"""
                    **ℹ️ Información del modelo:**
                    - **Velocidad:** {model_info.get('speed', 'Unknown')}
                    - **Calidad:** {model_info.get('quality', 'Unknown')}
                    - **Tipo:** {model_info.get('type', 'Unknown')}
                    """)
            else:
                st.error("❌ No se encontraron modelos disponibles")
                selected_model = "llama3"
                
        except Exception as e:
            st.error(f"❌ Error obteniendo modelos: {str(e)}")
            selected_model = "llama3"
        
        st.divider()
        
        # Gestión de documentos
        st.header("📄 Gestión de Documentos")
        
        # Documentos guardados
        try:
            saved_docs = get_saved_documents()
            
            if saved_docs:
                st.write(f"📚 **{len(saved_docs)} documentos guardados:**")
                
                for doc_info in saved_docs:
                    # Manejar tanto formato dict como string
                    if isinstance(doc_info, dict):
                        doc_file = doc_info.get('filename', 'Unknown')
                        file_size = doc_info.get('size', 0)
                        mod_time = doc_info.get('modified', None)
                    else:
                        doc_file = str(doc_info)
                        file_size = 0
                        mod_time = None
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        # Mostrar información del documento
                        display_name = doc_file
                        if mod_time:
                            try:
                                dt = datetime.fromtimestamp(mod_time)
                                display_name = f"{doc_file} ({dt.strftime('%d/%m/%Y %H:%M')})"
                            except:
                                pass
                        
                        # Mostrar tamaño si está disponible
                        if file_size > 0:
                            size_mb = file_size / (1024 * 1024)
                            if size_mb > 1:
                                size_str = f"{size_mb:.1f} MB"
                            else:
                                size_kb = file_size / 1024
                                size_str = f"{size_kb:.1f} KB"
                            display_name += f" ({size_str})"
                        
                        st.write(f"📄 {display_name}")
                    
                    with col2:
                        # Botón para procesar documento
                        if st.button("📂", key=f"load_{doc_file}", help="Procesar documento"):
                            try:
                                with st.spinner("Procesando documento..."):
                                    # Buscar el archivo en la carpeta docs
                                    docs_dir = os.path.join(current_dir, "docs")
                                    file_path = os.path.join(docs_dir, doc_file)
                                    
                                    if os.path.exists(file_path):
                                        # Crear un objeto similar a uploaded_file
                                        class FileUpload:
                                            def __init__(self, path):
                                                self.name = os.path.basename(path)
                                                with open(path, 'rb') as f:
                                                    self._content = f.read()
                                            
                                            def getvalue(self):
                                                return self._content
                                        
                                        file_obj = FileUpload(file_path)
                                        
                                        # Procesar archivo
                                        chunks = process_uploaded_file(file_obj)
                                        
                                        if chunks:
                                            # Crear vector store
                                            embeddings = get_embeddings_model()
                                            texts = [doc.page_content for doc in chunks]
                                            metadatas = [doc.metadata for doc in chunks]
                                            
                                            st.session_state.vector_store = FAISS.from_texts(
                                                texts=texts,
                                                embedding=embeddings,
                                                metadatas=metadatas
                                            )
                                            
                                            # Guardar información de chunks
                                            st.session_state.processed_docs = [
                                                {
                                                    'content': doc.page_content,
                                                    'metadata': doc.metadata
                                                }
                                                for doc in chunks
                                            ]
                                            
                                            st.success(f"✅ Documento '{doc_file}' procesado: {len(chunks)} fragmentos")
                                            st.rerun()
                                        else:
                                            st.error("❌ No se pudieron extraer fragmentos del documento")
                                    else:
                                        st.error("❌ Archivo no encontrado")
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                        
                        # Botón para eliminar documento
                        if st.button("🗑️", key=f"delete_{doc_file}", help="Eliminar documento"):
                            try:
                                # Eliminar archivo físico
                                docs_dir = os.path.join(current_dir, "docs")
                                file_path = os.path.join(docs_dir, doc_file)
                                
                                if os.path.exists(file_path):
                                    os.remove(file_path)
                                    st.success("✅ Documento eliminado")
                                    st.rerun()
                                else:
                                    st.error("❌ Archivo no encontrado")
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
            else:
                st.info("📝 No hay documentos guardados")
        
        except Exception as e:
            st.error(f"❌ Error gestionando documentos: {str(e)}")
        
        st.divider()
        
        # Subida de archivos
        st.header("📤 Subir Documento")
        uploaded_file = st.file_uploader(
            "Selecciona un archivo:",
            type=['pdf', 'txt', 'docx'],
            help="Formatos soportados: PDF, TXT, DOCX"
        )
        
        if uploaded_file:
            if st.button("🔄 Procesar Archivo", type="primary"):
                try:
                    with st.spinner("Procesando documento..."):
                        # Procesar archivo
                        chunks = process_uploaded_file(uploaded_file)
                        
                        if chunks:
                            # Crear vector store
                            embeddings = get_embeddings_model()
                            texts = [doc.page_content for doc in chunks]
                            metadatas = [doc.metadata for doc in chunks]
                            
                            st.session_state.vector_store = FAISS.from_texts(
                                texts=texts,
                                embedding=embeddings,
                                metadatas=metadatas
                            )
                            
                            # Guardar información de chunks
                            st.session_state.processed_docs = [
                                {
                                    'content': doc.page_content,
                                    'metadata': doc.metadata
                                }
                                for doc in chunks
                            ]
                            
                            st.success(f"✅ Archivo procesado: {len(chunks)} fragmentos")
                            st.info(f"📄 **{uploaded_file.name}** listo para consultas")
                        else:
                            st.error("❌ No se pudieron extraer fragmentos del documento")
                            
                except Exception as e:
                    st.error(f"❌ Error procesando archivo: {str(e)}")
        
        st.divider()
        
        # Información del sistema
        st.header("ℹ️ Estado del Sistema")
        st.success("✅ Ollama conectado")
        if st.session_state.vector_store:
            st.success(f"✅ RAG activo ({len(st.session_state.processed_docs)} fragmentos)")
        else:
            st.info("⏳ RAG no activo (sube un documento)")
        
        # Mostrar que la generación de imágenes está deshabilitada
        st.warning("⚠️ Generación de imágenes: DESHABILITADA")
        st.caption("Se eliminó para evitar conflictos con PyTorch")
    
    # Área principal de chat
    st.header("💬 Chat con IA")
    
    # Mostrar historial de chat
    for i, message in enumerate(st.session_state.chat_history):
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])
                
                # Mostrar contexto si está disponible
                if "context" in message and message["context"]:
                    with st.expander("📚 Contexto utilizado"):
                        st.write(message["context"])
    
    # Input del usuario
    user_input = st.chat_input("Escribe tu pregunta aquí...")
    
    if user_input:
        # Agregar mensaje del usuario al historial
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.write(user_input)
        
        # Generar respuesta
        with st.chat_message("assistant"):
            with st.spinner("Generando respuesta..."):
                try:
                    # Buscar contexto relevante si hay RAG disponible
                    context = ""
                    if st.session_state.vector_store:
                        relevant_docs = search_documents(st.session_state.vector_store, user_input)
                        context = format_context(relevant_docs)
                    
                    # Crear prompt
                    if context:
                        prompt_template = PromptTemplate(
                            template="""Contexto relevante:
{context}

Pregunta del usuario: {question}

Por favor, responde basándote en el contexto proporcionado. Si la información no está en el contexto, indícalo claramente y proporciona una respuesta general si es posible.""",
                            input_variables=["context", "question"]
                        )
                        prompt = prompt_template.format(context=context, question=user_input)
                    else:
                        prompt = user_input
                    
                    # Generar respuesta con Ollama
                    llm = OllamaLLM(
                        model=selected_model,
                        base_url="http://localhost:11434"
                    )
                    
                    response = llm.invoke(prompt)
                    
                    # Mostrar respuesta
                    st.write(response)
                    
                    # Mostrar contexto si está disponible
                    if context:
                        with st.expander("📚 Contexto utilizado"):
                            st.write(context)
                    
                    # Agregar respuesta al historial
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": response,
                        "context": context if context else None
                    })
                    
                except Exception as e:
                    error_msg = f"❌ Error generando respuesta: {str(e)}"
                    st.error(error_msg)
                    st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
    
    # Botón para limpiar historial
    if st.session_state.chat_history:
        st.divider()
        if st.button("🗑️ Limpiar Historial"):
            st.session_state.chat_history = []
            st.rerun()

if __name__ == "__main__":
    main()
