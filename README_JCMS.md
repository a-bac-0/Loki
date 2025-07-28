# 🤖 Asistente IA Local - F5

## 📋 Descripción

Aplicación de inteligencia artificial local construida con **Streamlit** y **Ollama** que permite:
- Chat interactivo con modelos de IA locales
- Sistema RAG (Retrieval-Augmented Generation) para análisis de documentos
- Interfaz web moderna y fácil de usar
- Procesamiento local (sin envío de datos a servicios externos)

---

## 🎯 Funcionalidades

### 🤖 Chat con IA
- **Múltiples modelos LLM**: Soporte para todos los modelos de Ollama
- **Chat interactivo**: Conversación fluida con historial
- **Respuestas contextuales**: Basadas en documentos cargados

### 📄 Sistema RAG
- **Subida de documentos**: PDF, TXT, DOCX
- **Almacenamiento persistente**: Documentos guardados localmente
- **Búsqueda semántica**: Encuentra información relevante
- **Análisis inteligente**: La IA responde basándose en tus documentos

---

## 🔧 Requisitos del Sistema

### Software Base
- **Python 3.9 o superior**
- **Ollama** instalado y ejecutándose
- **Git** (para clonar el repositorio)
- **8GB RAM mínimo** (recomendado 16GB)

### Sistema Operativo
- ✅ Windows 10/11
- ✅ macOS 10.15+
- ✅ Linux (Ubuntu 18.04+)

---

## 📥 Instalación

### 1. Instalar Ollama

#### Windows
```powershell
# Descargar desde: https://ollama.ai/download
# O usar winget:
winget install Ollama.Ollama
```

#### macOS
```bash
# Usando Homebrew:
brew install ollama
```

#### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### 2. Verificar Ollama
```bash
ollama --version
ollama serve
```

### 3. Clonar el Repositorio
```bash
git clone <URL_DE_TU_REPOSITORIO>
cd ejemplo_Ollama
```

### 4. Crear Entorno Virtual
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 5. Instalar Dependencias
```bash
pip install -r app/requirements.txt
```

---

## 🤖 Modelos de IA Requeridos

### Instalar Modelos en Ollama

**Ejecuta estos comandos en orden de prioridad:**

#### Modelos Principales (Recomendados)
```bash
# LLaMA 3 - Modelo principal (Excelente calidad)
ollama pull llama3:latest

# Gemma 3 - Rápido y eficiente
ollama pull gemma3:latest

# LLaMA 3.2 - Más compacto pero muy bueno
ollama pull llama3.2:latest
```

#### Modelos Especializados
```bash
# LLaVA - Para análisis de imágenes (multimodal)
ollama pull llava:7b

# ChatGPH - Especializado en conversación
ollama pull chatgph/gph-main
```

#### Modelos Adicionales (Opcionales)
```bash
# Mistral - Modelo francés de alta calidad
ollama pull mistral:latest

# Phi-3 - Modelo pequeño y rápido de Microsoft
ollama pull phi3:latest

# CodeLlama - Especializado en código
ollama pull codellama:latest
```

### Verificar Modelos Instalados
```bash
ollama list
```

---

## 🚀 Ejecución de la Aplicación

### Método 1: Script Automatizado (Recomendado)

#### Windows
```powershell
cd app
.\run.bat
```

#### macOS/Linux
```bash
cd app
chmod +x run.sh
./run.sh
```

### Método 2: Manual

#### 1. Iniciar Ollama (en terminal separada)
```bash
ollama serve
```

#### 2. Activar entorno virtual
```bash
# Windows
.\venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

#### 3. Ejecutar Streamlit
```bash
cd app
streamlit run app.py
```

### Método 3: Usando VSCode Tasks
```bash
# En VSCode: Ctrl+Shift+P > "Tasks: Run Task" > "Ejecutar Streamlit App"
```

---

## ⚙️ Configuración

### Variables de Entorno (.env)
Crea un archivo `.env` en el directorio `app/`:

```bash
# app/.env
OLLAMA_BASE_URL=http://localhost:11434
RAG_CHUNK_SIZE=1000
RAG_CHUNK_OVERLAP=200
RAG_DEFAULT_K=3
```

### Configuración Avanzada
Edita `app/config/settings.py` para personalizar:

```python
# Configuración de Ollama
OLLAMA_BASE_URL = "http://localhost:11434"

# Configuración de RAG
RAG_CHUNK_SIZE = 1000        # Tamaño de fragmentos de documento
RAG_CHUNK_OVERLAP = 200      # Solapamiento entre fragmentos
RAG_DEFAULT_K = 3            # Número de fragmentos relevantes

# Configuración de imágenes
IMAGE_SAVE_PATH = "img"
IMAGE_DEFAULT_WIDTH = 512
IMAGE_DEFAULT_HEIGHT = 512
```

---

## 🌐 Uso de la Aplicación

### 1. Acceder a la Interfaz
- Abre tu navegador en: **http://localhost:8501**
- La aplicación se abrirá automáticamente

### 2. Configuración Inicial
- **Seleccionar modelo**: Elige tu modelo preferido en la barra lateral
- **Subir documentos**: Arrastra archivos PDF, TXT o DOCX
- **Configurar parámetros**: Ajusta temperatura y otros settings

### 3. Funcionalidades

#### Chat Básico
1. Selecciona un modelo en la barra lateral
2. Escribe tu pregunta en el chat
3. Recibe respuestas instantáneas

#### Sistema RAG
1. Sube documentos usando el selector de archivos
2. Espera a que se procesen (aparecerán en "Documentos guardados")
3. Haz preguntas sobre el contenido de los documentos
4. La IA responderá basándose en la información de tus archivos

---

## 📁 Estructura del Proyecto

```
ejemplo_Ollama/
├── app/
│   ├── app.py                 # Aplicación principal
│   ├── requirements.txt       # Dependencias Python
│   ├── run.bat               # Script Windows
│   ├── run.sh                # Script Unix/Linux
│   ├── config/
│   │   └── settings.py       # Configuración global
│   ├── utils/
│   │   ├── model_utils.py    # Gestión de modelos
│   │   ├── rag_utils.py      # Sistema RAG
│   │   └── __init__.py
│   ├── docs/                 # Documentos guardados
│   └── img/                  # Imágenes (futuro)
├── README.md                 # Este archivo
├── requirements_simple.txt   # Dependencias básicas
└── .env                      # Variables de entorno
```

---

## 🔍 Modelos Detectados y Configurados

Tu aplicación está configurada para trabajar con estos modelos específicos:

| Modelo | Velocidad | Calidad | Tipo | Descripción |
|--------|-----------|---------|------|-------------|
| **llama3:latest** | 🟢 Rápida | 🟢 Muy Alta | 🔤 Texto | Modelo principal recomendado |
| **gemma3:latest** | 🟢 Rápida | 🟢 Alta | 🔤 Texto | Rápido y eficiente de Google |
| **llama3.2:latest** | 🟢 Muy Rápida | 🟢 Alta | 🔤 Texto | Versión compacta de LLaMA |
| **llava:7b** | 🟡 Media | 🟢 Alta | 👁️ Visión + Texto | Multimodal (texto + imágenes) |
| **chatgph/gph-main** | 🟢 Rápida | 🟢 Alta | 💬 Chat | Especializado en conversación |

---

## 🐛 Solución de Problemas

### Ollama no se conecta
```bash
# Verificar si Ollama está ejecutándose
ollama serve

# Verificar modelos disponibles
ollama list

# Probar conexión
curl http://localhost:11434/api/tags
```

### Error de dependencias
```bash
# Reinstalar dependencias
pip uninstall -r app/requirements.txt -y
pip install -r app/requirements.txt
```

### Puerto ocupado
```bash
# Cambiar puerto de Streamlit
streamlit run app.py --server.port 8502
```

### Problemas de memoria
- Cerrar otros programas que consuman RAM
- Usar modelos más pequeños (phi3, llama3.2)
- Reiniciar Ollama: `ollama stop && ollama serve`

---

## 📚 Documentación Adicional

### Archivos de Documentación
- `app/README.md` - Documentación técnica
- `app/roadmap.md` - Roadmap de desarrollo
- `app/briefing.md` - Brief del proyecto
- `COMPARACION_OBJETIVOS.md` - Comparación de objetivos

### Recursos Útiles
- **Ollama**: https://ollama.ai/
- **Streamlit**: https://streamlit.io/
- **LangChain**: https://python.langchain.com/

---

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

---

## 👥 Créditos

**Desarrollado para el Curso de IA - F5**
- Framework: Streamlit + LangChain
- IA Local: Ollama
- Vectorización: FAISS
- Procesamiento: PyTorch

---

## 📞 Soporte

Si tienes problemas:
1. Revisa la sección de **Solución de Problemas**
2. Verifica que Ollama esté ejecutándose
3. Confirma que los modelos estén instalados
4. Revisa los logs en la terminal

**¡Disfruta tu asistente de IA local! 🚀**
