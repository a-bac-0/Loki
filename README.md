# 🧠 Generador de Contenido con LLMs - PoC Digital Content

Este proyecto es una Prueba de Concepto (PoC) para Digital Content. El objetivo es generar contenido automático (texto e imágenes) para múltiples plataformas (Twitter, Blog, Instagram, LinkedIn) utilizando modelos de lenguaje (LLMs) y técnicas de IA generativa.

Ahora incluye integración con **LM Studio** y **ComfyUI** para generar contenido visual completo (texto + imagen) utilizando modelos locales.

---

## 🚀 Características

- Generación de texto adaptado a distintas plataformas y audiencias
- Interfaz web con Streamlit
- Integración con modelos locales o vía API (ej: Ollama, OpenAI)
- Integración con LM Studio para generación de texto con modelos locales
- Integración con ComfyUI para generación de imágenes personalizadas
- Flujo completo de generación de contenido visual (texto + imagen)
- Preparado para ampliación: multilenguaje, agentes y RAG

---

## 📦 Instalación

```bash
# Clona el repositorio
git clone https://github.com/a-bac-0/Loki.git
cd content-generator

# Crea el entorno virtual (usa Python 3.11 recomendado)
python3.11 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instala las dependencias
pip install -r requirements.txt
```

---

## 🔌 Integración con LM Studio y ComfyUI

### Configuración de LM Studio

1. Descarga e instala [LM Studio](https://lmstudio.ai/)
2. Carga un modelo compatible (como Gemma 3)
3. Inicia el servidor local en `http://127.0.0.1:1234/`

### Configuración de ComfyUI

1. Descarga e instala [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
2. Inicia el servidor local en `http://127.0.0.1:8000/`
3. Puedes utilizar el flujo de trabajo de ejemplo incluido en `data/examples/comfyui_workflow.json`

### Uso

1. Ejecuta la aplicación: `streamlit run frontend/main.py`
2. Selecciona "LM Studio + ComfyUI" como modelo de IA
3. Ingresa el tema, selecciona la plataforma, audiencia y tono
4. Haz clic en "Generar Contenido"
5. La aplicación generará texto con LM Studio y luego una imagen con ComfyUI basada en ese texto
