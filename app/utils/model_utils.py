# app/utils/model_utils.py

import requests

def get_available_models(base_url="http://localhost:11434"):
    """Obtiene la lista de modelos disponibles en Ollama"""
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return [(model["name"], model.get("size", "Tamaño desconocido")) for model in models]
        return []
    except:
        return []

def get_model_names(models_info):
    """Extrae solo los nombres de los modelos"""
    return [model[0] for model in models_info]

def get_model_info(model_name):
    """Obtiene información adicional sobre el modelo"""
    info = {
        "speed": "🟡 Media",
        "quality": "🟡 Media", 
        "description": "Modelo de propósito general",
        "type": "🔤 Texto"
    }
    
    model_lower = model_name.lower()
    
    # Información específica por modelo detectado en tu sistema
    if "llama3.2" in model_lower:
        info["speed"] = "🟢 Muy Rápida"
        info["quality"] = "🟢 Alta"
        info["description"] = "LLaMA 3.2 - Modelo compacto y eficiente de Meta"
        info["type"] = "🔤 Texto"
    elif "llama3" in model_lower and "llama3.2" not in model_lower:
        info["speed"] = "🟢 Rápida"
        info["quality"] = "🟢 Muy Alta"
        info["description"] = "LLaMA 3 - Modelo avanzado de Meta, excelente para texto"
        info["type"] = "🔤 Texto"
    elif "llava" in model_lower:
        info["speed"] = "🟡 Media"
        info["quality"] = "🟢 Alta"
        info["description"] = "LLaVA - Modelo multimodal para visión y lenguaje"
        info["type"] = "👁️ Visión + Texto"
    elif "gemma3" in model_lower:
        info["speed"] = "🟢 Rápida"
        info["quality"] = "🟢 Alta"
        info["description"] = "Gemma 3 - Modelo de Google, optimizado y eficiente"
        info["type"] = "🔤 Texto"
    elif "gph-main" in model_lower or "chatgph" in model_lower:
        info["speed"] = "🟢 Rápida"
        info["quality"] = "🟢 Alta"
        info["description"] = "ChatGPH - Modelo especializado en conversación"
        info["type"] = "💬 Chat"
    # Fallbacks para otros modelos comunes
    elif "gpt" in model_lower:
        info["speed"] = "🟡 Media"
        info["quality"] = "🟢 Muy Alta"
        info["description"] = "Modelo tipo GPT, excelente calidad de texto"
        info["type"] = "🔤 Texto"
    elif "phi" in model_lower:
        info["speed"] = "🟢 Muy Rápida"
        info["quality"] = "🟡 Media"
        info["description"] = "Modelo pequeño y rápido de Microsoft"
        info["type"] = "🔤 Texto"
    elif "mistral" in model_lower:
        info["speed"] = "🟢 Rápida"
        info["quality"] = "🟢 Alta"
        info["description"] = "Modelo francés, excelente rendimiento"
        info["type"] = "🔤 Texto"
    elif "gemma" in model_lower:
        info["speed"] = "🟢 Rápida"
        info["quality"] = "🟢 Alta"
        info["description"] = "Modelo de Google, optimizado y eficiente"
        info["type"] = "🔤 Texto"
    
    return info

def get_best_model(available_models):
    """Selecciona el mejor modelo basado en tus modelos locales"""
    # Prioridad de modelos basada en tu instalación local
    preferred_models = [
        "llama3.2:latest",     # Más compacto pero muy bueno - MODELO PRINCIPAL
        "llama3:latest",       # Excelente calidad general
        "gemma3:latest",       # Rápido y eficiente  
        "llava:7b",           # Para tareas multimodales
        "chatgph/gph-main"    # Para chat especializado
    ]
    
    model_names = get_model_names(available_models) if isinstance(available_models[0], tuple) else available_models
    
    for preferred in preferred_models:
        for available in model_names:
            if preferred in available:
                return available
    
    # Si no encuentra ningún modelo preferido, devuelve el primero disponible
    return model_names[0] if model_names else "llama3"
