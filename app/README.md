# app/README.md

# 🧠 Generador de Contenido con IA + RAG

Una aplicación completa para generar contenido de texto e imágenes usando modelos locales de Ollama con soporte para RAG (Retrieval-Augmented Generation).

## 🚀 Características

- **Generación de texto** con modelos locales de Ollama
- **Generación de imágenes** con Stable Diffusion optimizado para GPU/CPU
- **Sistema RAG** para enriquecer el contenido con documentos propios
- **Múltiples formatos** de salida (LinkedIn, Twitter, Instagram, Blog)
- **Guardado automático** de imágenes en `app/img/`
- **Interfaz moderna** con Streamlit

## 📁 Estructura del proyecto

```
app/
├── main.py                 # Aplicación principal
├── requirements.txt        # Dependencias Python
├── .env                   # Variables de entorno
├── README.md              # Este archivo
├── config/
│   └── settings.py        # Configuración global
├── utils/
│   ├── __init__.py        # Módulo de utilidades
│   ├── image_generator.py # Generador de imágenes optimizado
│   ├── model_utils.py     # Utilidades para modelos Ollama
│   └── rag_utils.py       # Funciones RAG
└── img/                   # Directorio para imágenes generadas
```

## 🛠️ Instalación

### 1. Prerrequisitos

Asegúrate de tener instalado:
- Python 3.8+
- [Ollama](https://ollama.ai/) ejecutándose localmente

### 2. Instalar dependencias

```bash
cd app
pip install -r requirements.txt
```

### 3. Configurar Ollama

Instala al menos un modelo de texto:

```bash
# Modelos recomendados (elige uno o varios)
ollama pull llama3.2
ollama pull gemma3
ollama pull nomic-embed-text  # Para RAG
```

### 4. Ejecutar la aplicación

```bash
streamlit run main.py
```

## 🎯 Uso

### Generación de Texto

1. Selecciona "📝 Solo Texto" o "🎨 Texto + Imagen"
2. Elige tu modelo de IA favorito
3. Configura el tema, plataforma y audiencia
4. Opcionalmente activa RAG cargando documentos
5. ¡Genera contenido!

### Generación de Imágenes

1. Selecciona "🖼️ Solo Imagen" o "🎨 Texto + Imagen"
2. Configura la resolución deseada
3. Describe la imagen que quieres generar
4. Las imágenes se guardan automáticamente en `app/img/`

### Sistema RAG

1. Sube documentos (PDF, TXT, DOCX) en la sección RAG
2. Procesa los documentos para crear embeddings
3. Activa RAG en la generación para usar tu contenido

## ⚙️ Configuración

### Variables de entorno (`.env`)

```bash
OLLAMA_BASE_URL=http://localhost:11434
PYTORCH_DISABLE_WATCHER=1
IMAGE_QUALITY=95
RAG_MODEL=nomic-embed-text
```

### GPU vs CPU

La aplicación detecta automáticamente si tienes GPU disponible:
- **Con GPU**: Genera imágenes en ~30-60 segundos
- **Solo CPU**: Genera imágenes en ~2-5 minutos

## 🔧 Solución de problemas

### Error: "Sistema de generación de imágenes no disponible"

```bash
pip install torch torchvision diffusers transformers sentence-transformers faiss-cpu accelerate
```

### Error: "No se pudieron detectar modelos en Ollama"

```bash
# Verificar que Ollama esté ejecutándose
ollama list

# Instalar un modelo
ollama pull llama3.2
```

### Error de memoria GPU

- Usa resoluciones más pequeñas (448x448)
- Cierra otras aplicaciones que usen GPU
- La aplicación tiene fallback automático a CPU

## 📋 Dependencias principales

- **Streamlit**: Interfaz web
- **LangChain**: Framework para LLM y RAG
- **PyTorch**: Machine learning
- **Diffusers**: Generación de imágenes
- **FAISS**: Búsqueda vectorial rápida
- **Sentence Transformers**: Embeddings

## 🎨 Formatos de salida

- **LinkedIn**: Contenido profesional con hashtags
- **Twitter/X**: Textos concisos (<280 caracteres)
- **Instagram**: Contenido visual con emojis
- **Blog**: Artículos extensos y estructurados

## 📸 Imágenes generadas

Todas las imágenes se guardan automáticamente en:
- **Ubicación**: `app/img/`
- **Formato**: PNG de alta calidad
- **Nomenclatura**: `imagen_generada_YYYYMMDD_HHMMSS.png`

## 🤖 Modelos recomendados

### Para texto:
- **llama3.2**: Rápido y eficiente
- **gemma3**: Excelente calidad
- **llava**: Soporte multimodal

### Para embeddings (RAG):
- **nomic-embed-text**: Optimizado para RAG
- **llama3.2**: Fallback compatible

## 🎯 Próximas características

- [ ] Soporte para más modelos de imagen
- [ ] Integración con APIs externas
- [ ] Sistema de plantillas personalizadas
- [ ] Exportación a múltiples formatos
- [ ] Historial de generaciones

## 📝 Licencia

MIT License - Libre para uso personal y comercial.

## 🆘 Soporte

Si encuentras problemas:

1. Revisa la sección de solución de problemas
2. Verifica que Ollama esté ejecutándose
3. Comprueba las dependencias con el botón de verificación
4. Usa el botón "🔧 Reiniciar generador" si hay problemas con imágenes

---

¡Disfruta creando contenido con IA! 🚀
