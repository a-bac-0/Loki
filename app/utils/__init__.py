# app/utils/__init__.py

"""
Utilidades para el generador de contenido con IA + RAG
"""

# NO importar image_generator aquí para evitar conflictos PyTorch-Streamlit
# from .image_generator import OptimizedGPUImageGenerator

from .model_utils import get_available_models, get_model_names, get_model_info, get_best_model
from .rag_utils import get_embeddings_model, process_uploaded_file, create_vector_store, search_documents, format_context

__all__ = [
    # 'OptimizedGPUImageGenerator',  # Se importa dinámicamente en main.py
    'get_available_models',
    'get_model_names', 
    'get_model_info',
    'get_best_model',
    'get_embeddings_model',
    'process_uploaded_file',
    'create_vector_store',
    'search_documents',
    'format_context'
]
