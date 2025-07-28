# utils/model_utils.py - Versión corregida

import requests
from typing import List, Dict, Any, Optional

def get_available_models() -> List[Dict[str, Any]]:
    """
    Obtiene la lista de modelos disponibles en Ollama.
    """
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            print(f"✅ Encontrados {len(models)} modelos disponibles")
            return models
        else:
            print(f"⚠️ Error obteniendo modelos: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error conectando con Ollama: {e}")
        return []

def get_model_names(models: List[Dict[str, Any]]) -> List[str]:
    """
    Extrae los nombres de los modelos de la lista de modelos disponibles.
    """
    try:
        model_names = []
        for model in models:
            name = model.get('name', '')
            if name:
                # Limpiar el nombre del modelo (quitar :latest si está presente para display)
                display_name = name
                if display_name.endswith(':latest'):
                    display_name = display_name[:-7]  # Quitar ':latest'
                model_names.append(name)  # Pero mantener el nombre completo internamente
        
        return sorted(list(set(model_names)))
    except Exception as e:
        print(f"❌ Error procesando nombres de modelos: {e}")
        return []

def get_model_info(model_name: str) -> Dict[str, str]:
    """
    Obtiene información detallada sobre un modelo específico.
    """
    # Base de datos de información de modelos conocidos
    model_database = {
        # Modelos Llama
        'llama2': {
            'speed': 'Media',
            'quality': 'Buena',
            'description': 'Modelo versátil y equilibrado',
            'type': 'General Purpose LLM',
            'recommended_use': 'Chat general, análisis de texto'
        },
        'llama3': {
            'speed': 'Media',
            'quality': 'Muy Buena',
            'description': 'Versión mejorada con mejor comprensión',
            'type': 'General Purpose LLM',
            'recommended_use': 'Chat avanzado, análisis complejo'
        },
        'llama3.1': {
            'speed': 'Media-Lenta',
            'quality': 'Excelente',
            'description': 'Última versión con capacidades mejoradas',
            'type': 'Advanced LLM',
            'recommended_use': 'Tareas complejas, razonamiento avanzado'
        },
        # Modelos Code Llama
        'codellama': {
            'speed': 'Media',
            'quality': 'Muy Buena',
            'description': 'Especializado en generación de código',
            'type': 'Code Generation LLM',
            'recommended_use': 'Programación, debug, explicación de código'
        },
        # Modelos Mistral
        'mistral': {
            'speed': 'Rápida',
            'quality': 'Buena',
            'description': 'Modelo eficiente y rápido',
            'type': 'Efficient LLM',
            'recommended_use': 'Respuestas rápidas, chat ligero'
        },
        'mixtral': {
            'speed': 'Media',
            'quality': 'Muy Buena',
            'description': 'Modelo mixto con excelente rendimiento',
            'type': 'Mixture of Experts LLM',
            'recommended_use': 'Análisis complejo, tareas múltiples'
        },
        # Modelos de Embeddings
        'nomic-embed-text': {
            'speed': 'Muy Rápida',
            'quality': 'Excelente',
            'description': 'Modelo especializado en embeddings de texto',
            'type': 'Embedding Model',
            'recommended_use': 'RAG, búsqueda semántica, análisis de similitud'
        },
        'all-minilm': {
            'speed': 'Muy Rápida',
            'quality': 'Buena',
            'description': 'Modelo ligero para embeddings',
            'type': 'Embedding Model',
            'recommended_use': 'Embeddings rápidos, dispositivos limitados'
        },
        # Modelos Gemma
        'gemma': {
            'speed': 'Media',
            'quality': 'Buena',
            'description': 'Modelo de Google, eficiente y preciso',
            'type': 'General Purpose LLM',
            'recommended_use': 'Chat general, tareas variadas'
        },
        # Modelos Phi
        'phi3': {
            'speed': 'Rápida',
            'quality': 'Buena',
            'description': 'Modelo compacto de Microsoft',
            'type': 'Compact LLM',
            'recommended_use': 'Dispositivos con recursos limitados'
        }
    }
    
    # Limpiar nombre del modelo para búsqueda
    clean_name = model_name.replace(':latest', '').replace(':chat', '').replace(':instruct', '')
    base_name = clean_name.split(':')[0]  # Tomar solo la parte base del nombre
    
    # Buscar información en la base de datos
    info = model_database.get(base_name, model_database.get(clean_name, {}))
    
    # Si no se encuentra, proporcionar información genérica
    if not info:
        # Intentar determinar el tipo basado en el nombre
        if 'embed' in model_name.lower():
            info = {
                'speed': 'Rápida',
                'quality': 'Buena',
                'description': 'Modelo de embeddings',
                'type': 'Embedding Model',
                'recommended_use': 'Procesamiento de texto, RAG'
            }
        elif 'code' in model_name.lower():
            info = {
                'speed': 'Media',
                'quality': 'Buena',
                'description': 'Modelo especializado en código',
                'type': 'Code Generation LLM',
                'recommended_use': 'Programación, desarrollo'
            }
        else:
            info = {
                'speed': 'Desconocida',
                'quality': 'Desconocida',
                'description': 'Modelo de propósito general',
                'type': 'General Purpose LLM',
                'recommended_use': 'Uso general'
            }
    
    return info

def get_best_model(available_models: List[Dict[str, Any]]) -> str:
    """
    Determina el mejor modelo disponible basado en criterios predefinidos.
    """
    if not available_models:
        return "llama2"  # Fallback por defecto
    
    model_names = [model.get('name', '') for model in available_models]
    
    # Lista de preferencias de modelos (en orden de preferencia)
    preferred_models = [
        'llama3.1',
        'llama3.1:latest',
        'llama3',
        'llama3:latest',
        'mixtral',
        'mixtral:latest',
        'codellama',
        'codellama:latest',
        'mistral',
        'mistral:latest',
        'gemma',
        'gemma:latest',
        'llama2',
        'llama2:latest',
        'phi3',
        'phi3:latest'
    ]
    
    # Buscar el primer modelo preferido que esté disponible
    for preferred in preferred_models:
        if preferred in model_names:
            print(f"✅ Mejor modelo encontrado: {preferred}")
            return preferred
    
    # Si no se encuentra ningún modelo preferido, usar el primero disponible
    # pero evitar modelos de embeddings para chat
    for model in model_names:
        if 'embed' not in model.lower():
            print(f"✅ Usando primer modelo disponible: {model}")
            return model
    
    # Último recurso: usar el primer modelo disponible
    first_model = model_names[0]
    print(f"⚠️ Usando modelo por defecto: {first_model}")
    return first_model

def is_embedding_model(model_name: str) -> bool:
    """
    Determina si un modelo es específicamente para embeddings.
    """
    embedding_indicators = [
        'embed',
        'embedding',
        'sentence',
        'all-minilm',
        'e5-',
        'bge-',
        'gte-'
    ]
    
    model_lower = model_name.lower()
    return any(indicator in model_lower for indicator in embedding_indicators)

def is_code_model(model_name: str) -> bool:
    """
    Determina si un modelo está especializado en código.
    """
    code_indicators = [
        'code',
        'codellama',
        'starcoder',
        'wizardcoder',
        'deepseek-coder'
    ]
    
    model_lower = model_name.lower()
    return any(indicator in model_lower for indicator in code_indicators)

def get_embedding_models(available_models: List[Dict[str, Any]]) -> List[str]:
    """
    Filtra y retorna solo los modelos apropiados para embeddings.
    """
    model_names = [model.get('name', '') for model in available_models]
    embedding_models = [name for name in model_names if is_embedding_model(name)]
    
    # Si no hay modelos específicos de embeddings, agregar algunos LLM como fallback
    if not embedding_models:
        fallback_models = ['llama2', 'llama3', 'mistral']
        for fallback in fallback_models:
            if any(fallback in name for name in model_names):
                matching_models = [name for name in model_names if fallback in name]
                embedding_models.extend(matching_models)
                break
    
    return embedding_models

def verify_model_availability(model_name: str) -> bool:
    """
    Verifica si un modelo específico está disponible en Ollama.
    """
    try:
        available_models = get_available_models()
        model_names = [model.get('name', '') for model in available_models]
        return model_name in model_names
    except Exception as e:
        print(f"❌ Error verificando disponibilidad del modelo: {e}")
        return False