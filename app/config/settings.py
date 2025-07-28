# app/config/settings.py

"""
Configuración global de la aplicación
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de Ollama
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Configuración de imágenes
IMAGE_SAVE_PATH = "img"
IMAGE_DEFAULT_WIDTH = 512
IMAGE_DEFAULT_HEIGHT = 512
IMAGE_MAX_RESOLUTION = 1024

# Configuración de RAG
RAG_CHUNK_SIZE = 1000
RAG_CHUNK_OVERLAP = 200
RAG_DEFAULT_K = 3

# Configuración de PyTorch
PYTORCH_SETTINGS = {
    'PYTORCH_DISABLE_WATCHER': '1',
    'TORCH_LOGS': '+all'
}

# Aplicar configuración de PyTorch
for key, value in PYTORCH_SETTINGS.items():
    os.environ[key] = value

# Modelos preferidos por orden de prioridad
PREFERRED_MODELS = [
    "llama3:latest",
    "gemma3:latest", 
    "llama3.2:latest",
    "llava:7b",
    "chatgph/gph-main"
]

# Configuración de Streamlit
STREAMLIT_CONFIG = {
    "page_title": "Generador de Contenido IA con RAG",
    "layout": "wide",
    "initial_sidebar_state": "collapsed"
}

# Tipos de archivo soportados
SUPPORTED_FILE_TYPES = ['pdf', 'txt', 'docx', 'doc']

# Configuración de dependencias
REQUIRED_PACKAGES = [
    "torch",
    "torchvision", 
    "diffusers",
    "transformers",
    "sentence-transformers",
    "faiss-cpu",
    "accelerate"
]
