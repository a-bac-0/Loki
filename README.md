# 🧠 AI Content Generator - Loki

This project is a Proof of Concept (PoC) for Digital Content: an AI-powered system to automatically generate text and images for multiple platforms (Twitter/X, Blog, Instagram, LinkedIn, and more) using local and cloud-based LLMs, image generators, and RAG architectures. It features a modern web interface, multi-language support, and is designed for easy extensibility.

---

## 🚀 Features

- Generate text tailored for different platforms and audiences
- Web interface built with Streamlit
- Integrates local and API-based LLMs (Ollama, OpenAI, Groq, LM Studio)
- Image generation with ComfyUI and Stable Diffusion
- Retrieval-Augmented Generation (RAG) for document-based content
- Multi-language support (Spanish, English, French, Italian)
- Easily extensible: agents, RAG, new models

---

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/a-bac-0/Loki.git
cd Loki

# Create a virtual environment (Python 3.11 recommended)
python3.11 -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🔌 Integrations

### LM Studio

1. Download and install [LM Studio](https://lmstudio.ai/)
2. Load a compatible model (e.g., Gemma 3)
3. Start the local server at `http://127.0.0.1:1234/`

### ComfyUI

1. Download and install [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
2. Start the local server at `http://127.0.0.1:8000/`
3. You can use the example workflow in `data/examples/comfyui_workflow.json`

### Ollama

1. Download and install [Ollama](https://ollama.ai/download)
2. Pull recommended models (e.g., llama3, gemma3)
3. Start the Ollama server (`ollama serve`)

---

## 🖥️ Usage

1. Run the application:
   ```bash
   streamlit run frontend/main.py
   ```
2. Select your preferred AI model (LM Studio, Ollama, OpenAI, etc.)
3. Enter the topic, select platform, audience, and tone
4. Click "Generate Content"
5. The app will generate text and, if selected, an image based on the text

---

## 🗂️ Project Structure

```
Loki/
├── app/
│   ├── main.py                # Main application
│   ├── requirements.txt       # Python dependencies
│   ├── config/
│   ├── utils/
│   ├── image_generator/       # Image generation modules
│   ├── img/                   # Generated images
│   ├── docs/                  # Uploaded documents
│   └── ...
├── AI-Agents/                 # Agent and LLM code
├── data/                      # Example workflows, arXiv scripts
├── README.md                  # This file
└── ...
```

---

## 📝 Main Modules

- **Text Generation:** Supports local (Ollama, LM Studio) and API-based (OpenAI, Groq) LLMs
- **Image Generation:** ComfyUI, Stable Diffusion, GPU/CPU support
- **RAG:** Document upload, embedding, and semantic search (ChromaDB, FAISS)
- **Frontend:** Streamlit web interface
- **Multi-format Output:** LinkedIn, Twitter/X, Instagram, Blog

---

## 🗄️ Storage

- **app/img/**: Stores all generated images (PNG, timestamped)
- **app/docs/**: Stores all uploaded user documents (PDF, TXT, DOCX, timestamped)

---

## 🛠️ Troubleshooting

- Ensure all required services (Ollama, LM Studio, ComfyUI) are running
- Check Python and package versions
- For GPU errors, verify CUDA and driver installation
- See each module's README for more details

---

## 📚 Dependencies

- Streamlit, LangChain, PyTorch, Diffusers, FAISS, Sentence Transformers, ChromaDB, etc.

---

## 🏷️ License

MIT License - Free for personal and commercial use.

---

## 👥 Credits

Developed by the Loki team as part of the F5 AI Course. Main contributors: Andreina (frontend, Groq/OpenAI integration), Max (MLstudio, bugfixes, documentation), Juan Carlos (image generation, financial analysis, RAG), Anca (agents, Ollama, RAG, project management).
