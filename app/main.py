## frontend/main.py - PARTE 1: CONFIGURACIÓN Y CONTENTGENERATOR
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta

import requests
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rag.rag_chain import generate_scientific_content

try:
    from langsmith import LangSmithCallbackHandler
except ImportError:
    try:
        from langchain.callbacks.tracers.langsmith import LangSmithCallbackHandler
    except ImportError:
        LangSmithCallbackHandler = None

# Configuración de página
st.set_page_config(
    page_title="🧠 ContentAI Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS profesional unificado
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --primary-color: #6366f1;
        --primary-dark: #4f46e5;
        --secondary-color: #8b5cf6;
        --accent-color: #06b6d4;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --error-color: #ef4444;
        --text-primary: #1f2937;
        --text-secondary: #6b7280;
        --bg-primary: #ffffff;
        --bg-secondary: #f8fafc;
        --bg-tertiary: #f1f5f9;
        --border-color: #e2e8f0;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        --radius-sm: 6px;
        --radius-md: 8px;
        --radius-lg: 12px;
        --radius-xl: 16px;
    }
    
    .main .block-container {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        padding: 1.5rem 2rem 3rem 2rem;
        max-width: 1400px;
        color: var(--text-primary);
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-weight: 600;
        letter-spacing: -0.025em;
        line-height: 1.2;
    }
    
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-size: 400% 400%;
        animation: gradientShift 8s ease infinite;
        padding: 4rem 3rem;
        border-radius: var(--radius-xl);
        text-align: center;
        margin-bottom: 3rem;
        color: white;
        position: relative;
        overflow: hidden;
        box-shadow: var(--shadow-xl);
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .hero-section h1 {
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 1.5rem;
        letter-spacing: -0.04em;
        text-shadow: 0 4px 6px rgba(0,0,0,0.1);
        position: relative;
        z-index: 1;
    }
    
    .hero-section p {
        font-size: 1.25rem;
        opacity: 0.95;
        margin: 0;
        font-weight: 400;
        position: relative;
        z-index: 1;
        max-width: 600px;
        margin: 0 auto;
        line-height: 1.6;
    }
    
    .content-card {
        background: var(--bg-primary);
        padding: 2.5rem;
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-color);
        margin: 1.5rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .content-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
        border-color: var(--primary-color);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        padding: 0.875rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        width: 100% !important;
        box-shadow: var(--shadow-md) !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, var(--primary-dark), #7c3aed) !important;
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-lg) !important;
    }
    
    .generated-content {
        background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
        padding: 2.5rem;
        border-radius: var(--radius-lg);
        border-left: 4px solid var(--accent-color);
        margin: 2rem 0;
        box-shadow: var(--shadow-md);
        position: relative;
        overflow: hidden;
    }
    
    .generated-content::after {
        content: '✨';
        position: absolute;
        top: 1rem;
        right: 1rem;
        font-size: 1.5rem;
        opacity: 0.6;
    }
    
    .generated-content h4 {
        color: var(--text-primary);
        margin-bottom: 1.5rem;
        font-size: 1.375rem;
    }
    
    .generated-content .content-preview {
        background: white;
        padding: 2rem;
        border-radius: var(--radius-md);
        border: 1px solid rgba(6, 182, 212, 0.2);
        margin: 1.5rem 0;
        font-family: 'Inter', sans-serif;
        line-height: 1.6;
        box-shadow: var(--shadow-sm);
    }
    
    .api-status {
        padding: 0.875rem 1.25rem;
        border-radius: var(--radius-md);
        margin: 0.75rem 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .api-status.connected {
        background: linear-gradient(135deg, #d1fae5, #a7f3d0);
        color: #065f46;
        border: 1px solid #86efac;
    }
    
    .api-status.disconnected {
        background: linear-gradient(135deg, #fee2e2, #fecaca);
        color: #991b1b;
        border: 1px solid #f87171;
    }
    
    .progress-step {
        background: white;
        padding: 1.25rem 1.5rem;
        border-radius: var(--radius-md);
        margin: 0.75rem 0;
        border-left: 4px solid var(--primary-color);
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--border-color);
    }
    
    .metric-card {
        background: var(--bg-primary);
        padding: 1.5rem;
        border-radius: var(--radius-lg);
        border: 1px solid var(--border-color);
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: var(--shadow-sm);
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }
    
    .tips-card {
        background: linear-gradient(135deg, #fef7ff, #faf5ff);
        border: 1px solid #e9d5ff;
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .tips-card h4 {
        color: var(--secondary-color);
        margin-bottom: 1rem;
        font-size: 1.125rem;
    }
    
    .stTextInput > div > div > input {
        border-radius: var(--radius-md) !important;
        border: 2px solid var(--border-color) !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
    }
    
    .image-preview {
        border-radius: var(--radius-lg);
        overflow: hidden;
        box-shadow: var(--shadow-lg);
        border: 1px solid var(--border-color);
    }
    
    .fade-in {
        animation: fadeIn 0.6s ease-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @media (max-width: 768px) {
        .hero-section h1 {
            font-size: 2.5rem;
        }
        .hero-section {
            padding: 3rem 2rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# ===============================
# AGENTES DE IA - VERSIÓN UNIFICADA
# ===============================

# Importar el agente de contenido visual si está disponible
try:
    from app.agents.content_visual_agent import ContentVisualAgent
except ImportError:
    ContentVisualAgent = None

class ContentGenerator:
    """Generador de contenido unificado con múltiples opciones de IA"""

    def __init__(self):
        self.openai_key = None
        self.groq_key = None
        self.unsplash_key = None
        self.api_configured = False
        self.groq_configured = False
        self.unsplash_configured = False

    def configure_apis(self, openai_key=None, groq_key=None, unsplash_key=None):
        """Configurar APIs"""
        self.openai_key = openai_key
        self.groq_key = groq_key
        self.unsplash_key = unsplash_key
        self.api_configured = bool(openai_key)
        self.groq_configured = bool(groq_key)
        self.unsplash_configured = bool(unsplash_key)

    def extract_visual_concepts_from_content(self, content, topic=""):
        """Extrae conceptos visuales del contenido generado usando análisis semántico"""
        if not content:
            return ["business", "professional"]

        full_text = f"{topic} {content}".lower()
        visual_keywords = self._extract_visual_keywords(full_text)
        main_entities = self._extract_main_entities(full_text)
        thematic_context = self._determine_thematic_context(full_text)

        all_concepts = visual_keywords + main_entities + thematic_context
        clean_concepts = self._clean_and_prioritize_concepts(all_concepts)

        if len(clean_concepts) < 2:
            smart_fallbacks = self._generate_contextual_fallbacks(content, topic)
            clean_concepts.extend(smart_fallbacks)

        return clean_concepts[:5]

    def _extract_visual_keywords(self, text):
        """Extrae palabras con fuerte componente visual del texto"""
        visual_patterns = {
            'objects': r'\b(computer|laptop|phone|device|book|office|workspace|desk|meeting|presentation)\b',
            'activities': r'\b(working|creating|building|designing|planning|analyzing|learning|teaching)\b',
            'concepts': r'\b(innovation|technology|success|growth|teamwork|leadership|creativity)\b',
            'environments': r'\b(office|home|studio|classroom|outdoor|urban|modern|professional)\b'
        }

        visual_words = []
        for category, pattern in visual_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            visual_words.extend([match.lower() for match in matches])

        return list(dict.fromkeys(visual_words))[:3]

    def _extract_main_entities(self, text):
        """Extrae las entidades/sustantivos principales del texto"""
        stop_words = {
            'the', 'and', 'for', 'with', 'you', 'your', 'this', 'that', 'will', 'can',
            'are', 'is', 'have', 'has', 'more', 'most', 'make', 'get', 'como', 'para',
            'con', 'por', 'una', 'los', 'las', 'del', 'que', 'sus', 'muy', 'más'
        }

        words = re.findall(r'\b[a-zA-ZáéíóúÁÉÍÓÚñÑ]{4,12}\b', text)

        word_freq = {}
        for word in words:
            word_lower = word.lower()
            if word_lower not in stop_words and word_lower.isalpha():
                word_freq[word_lower] = word_freq.get(word_lower, 0) + 1

        sorted_entities = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_entities[:4] if freq >= 1]

    def _determine_thematic_context(self, text):
        """Determina el contexto temático y sugiere conceptos visuales apropiados"""
        context_indicators = {
            'technology': {
                'keywords': ['technology', 'digital', 'ai', 'artificial', 'data', 'software', 'innovation'],
                'visual_concepts': ['technology', 'computer', 'innovation', 'digital']
            },
            'business': {
                'keywords': ['business', 'company', 'market', 'sales', 'revenue', 'professional', 'strategy'],
                'visual_concepts': ['business meeting', 'professional', 'success', 'teamwork']
            },
            'education': {
                'keywords': ['learn', 'education', 'teaching', 'student', 'course', 'knowledge'],
                'visual_concepts': ['learning', 'books', 'education', 'classroom']
            },
            'creativity': {
                'keywords': ['creative', 'design', 'art', 'visual', 'innovative', 'inspiration'],
                'visual_concepts': ['creative', 'design', 'art', 'inspiration']
            },
            'health': {
                'keywords': ['health', 'wellness', 'fitness', 'exercise', 'medical', 'care'],
                'visual_concepts': ['health', 'fitness', 'wellness', 'exercise']
            },
            'communication': {
                'keywords': ['social', 'media', 'communication', 'network', 'connect', 'share'],
                'visual_concepts': ['communication', 'social media', 'networking', 'team']
            }
        }

        detected_concepts = []

        for context, data in context_indicators.items():
            for keyword in data['keywords']:
                if keyword in text:
                    detected_concepts.extend(data['visual_concepts'][:2])
                    break

        return detected_concepts[:3]

    def _clean_and_prioritize_concepts(self, concepts):
        """Limpia y prioriza los conceptos extraídos"""
        if not concepts:
            return []

        clean_concepts = []
        seen = set()

        for concept in concepts:
            if not concept:
                continue

            clean_concept = str(concept).strip().lower()

            if (len(clean_concept) >= 3 and 
                len(clean_concept) <= 20 and 
                clean_concept not in seen and
                clean_concept.replace(' ', '').isalpha()):

                seen.add(clean_concept)
                clean_concepts.append(clean_concept)

        return clean_concepts

    def _generate_contextual_fallbacks(self, content, topic):
        """Genera conceptos de respaldo basados en el contexto del contenido"""
        fallbacks = []

        if len(content) > 200:
            fallbacks.extend(["article", "information", "reading"])

        if "#" in content or "@" in content:
            fallbacks.extend(["social media", "communication", "smartphone"])

        if any(emoji in content for emoji in "🚀💡✨🎯"):
            fallbacks.extend(["modern", "vibrant", "innovative"])

        if "•" in content or "1." in content:
            fallbacks.extend(["presentation", "infographic", "organization"])

        if topic:
            topic_words = [word.lower() for word in topic.split() if len(word) > 3]
            fallbacks.extend(topic_words[:2])

        fallbacks.extend(["business", "professional", "success", "modern"])

        return fallbacks[:4]

    def _perform_unsplash_search(self, query, orientation="landscape"):
        """Realiza la búsqueda real en Unsplash con parámetros optimizados"""
        try:
            url = "https://api.unsplash.com/search/photos"
            headers = {"Authorization": f"Client-ID {self.unsplash_key}"}
            params = {
                "query": query,
                "per_page": 15,
                "orientation": orientation,
                "content_filter": "high",
                "order_by": "relevant"
            }

            response = requests.get(url, headers=headers, params=params, timeout=12)

            if response.status_code == 200:
                data = response.json()
                if data["results"]:
                    for image_data in data["results"]:
                        if (image_data.get("width", 0) >= 800 and 
                            image_data.get("height", 0) >= 600):

                            return {
                                "url": image_data["urls"]["regular"],
                                "thumb": image_data["urls"]["thumb"],
                                "description": image_data.get("description", "") or image_data.get("alt_description", ""),
                                "author": image_data["user"]["name"],
                                "author_url": image_data["user"]["links"]["html"],
                                "download_url": image_data["links"]["download_location"],
                                "width": image_data.get("width", 0),
                                "height": image_data.get("height", 0)
                            }, "Imagen de alta calidad encontrada"

                    image_data = data["results"][0]
                    return {
                        "url": image_data["urls"]["regular"],
                        "thumb": image_data["urls"]["thumb"],
                        "description": image_data.get("description", "") or image_data.get("alt_description", ""),
                        "author": image_data["user"]["name"],
                        "author_url": image_data["user"]["links"]["html"],
                        "download_url": image_data["links"]["download_location"],
                        "width": image_data.get("width", 0),
                        "height": image_data.get("height", 0)
                    }, "Imagen encontrada"
                else:
                    return None, f"Sin resultados para '{query}'"

            elif response.status_code == 403:
                return None, "API key inválida o sin permisos"
            elif response.status_code == 429:
                return None, "Límite de velocidad alcanzado"
            else:
                return None, f"Error HTTP {response.status_code}"

        except requests.exceptions.Timeout:
            return None, "Timeout en búsqueda"
        except Exception as e:
            return None, f"Error: {str(e)}"

    def search_unsplash_image_intelligent(self, content, topic="", platform="", orientation="landscape"):
        """Búsqueda inteligente de imágenes basada en análisis del contenido real"""
        if not self.unsplash_key:
            return None, "API key de Unsplash no configurada"

        try:
            visual_concepts = self.extract_visual_concepts_from_content(content, topic)

            search_strategies = [
                visual_concepts[:2],
                [f"{visual_concepts[0]} {visual_concepts[1]}"] if len(visual_concepts) >= 2 else [],
                [f"{visual_concepts[0]} {platform.lower()}"] if visual_concepts and platform else [],
                [topic] if topic and len(topic.split()) <= 2 else [],
                ["professional workspace", "business success", "modern technology"]
            ]

            for strategy_num, keywords_list in enumerate(search_strategies, 1):
                if not keywords_list:
                    continue

                for keyword in keywords_list:
                    if not keyword or len(keyword.strip()) < 3:
                        continue

                    image_result = self._perform_unsplash_search(keyword.strip(), orientation)

                    if image_result[0]:
                        return image_result[0], f"✅ Encontrada con '{keyword}' (Análisis inteligente - Estrategia {strategy_num})"

            attempted_keywords = [kw for strategy in search_strategies for kw in strategy if kw][:5]
            return None, f"❌ Sin resultados tras análisis inteligente. Probados: {', '.join(attempted_keywords[:3])}..."

        except Exception as e:
            return None, f"Error en búsqueda inteligente: {str(e)}"

    def generate_with_groq(self, topic, platform, audience, tone="profesional", creator_name=""):
        """Generar contenido real con Groq (Ultra rápido y gratuito)"""
        if not self.groq_key:
            return None, "API key de Groq no configurada"

        try:
            platform_instructions = {
                "twitter": "Crea un tweet atractivo y conciso (máximo 280 caracteres)",
                "blog": "Crea una introducción engaging para un artículo de blog",
                "instagram": "Crea un post visual para Instagram con emojis y hashtags",
                "linkedin": "Crea un post profesional para LinkedIn"
            }

            headers = {
                "Authorization": f"Bearer {self.groq_key}",
                "Content-Type": "application/json"
            }

            creator_instruction = ""
            if creator_name:
                creator_instruction = f"\n8. Al final del contenido, añade una línea separadora (---) y luego '✍️ Creado por {creator_name}'"

            system_prompt = f"""
            Eres un experto en marketing de contenidos y redes sociales.
            
            Tarea: {platform_instructions.get(platform.lower(), 'Crear contenido para redes sociales')}
            Plataforma: {platform}
            Audiencia: {audience}
            Tono: {tone}
            
            Instrucciones:
            1. Crea contenido 100% original y atractivo
            2. Usa un tono {tone}
            3. Optimiza específicamente para {platform}
            4. Incluye emojis relevantes
            5. Añade hashtags apropiados al final
            6. Haz que sea engaging para {audience}
            7. Que invite a la interacción{creator_instruction}
            
            Responde SOLO con el contenido final, sin explicaciones adicionales.
            """

            data = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Crea contenido sobre: {topic}"}
                ],
                "model": "llama3-70b-8192",
                "temperature": 0.7,
                "max_tokens": 500,
                "top_p": 0.9,
                "stream": False
            }

            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"].strip()

                if creator_name and f"Creado por {creator_name}" not in content:
                    content += f"\n\n---\n✍️ Creado por {creator_name}"

                return content, "Contenido generado con Groq Llama3-70B (Ultra rápido)"
            elif response.status_code == 401:
                return None, "API key de Groq inválida"
            elif response.status_code == 429:
                return None, "Límite de velocidad alcanzado. Espera un momento."
            else:
                return None, f"Error en API de Groq: {response.status_code}"

        except requests.exceptions.Timeout:
            return None, "Timeout conectando con Groq"
        except Exception as e:
            return None, f"Error con Groq: {str(e)}"

    def generate_with_lmstudio_comfyui(self, topic, platform, audience, tone="profesional"):
        """Genera contenido de texto e imagen utilizando LM Studio y ComfyUI"""
        try:
            if not st.session_state.get("has_content_visual_agent", False):
                return None, "El agente de contenido visual no está disponible."

            agent = st.session_state.content_visual_agent
            services = agent.check_services()

            if not all(services.values()):
                return None, "No se pudo conectar a LM Studio o ComfyUI."

            with st.status("Generando contenido visual...", expanded=True) as status:
                status.update(label="Generando texto con LM Studio...")

                def status_update(msg):
                    status.update(label=msg)

                content_result = agent.generate_complete_content(
                    topic=topic,
                    platform=platform,
                    audience=audience,
                    tone=tone,
                    status_callback=status_update,
                )

                if content_result and "content" in content_result:
                    status.update(label="¡Contenido visual generado con éxito!", state="complete")
                    return content_result.get("content", ""), "Contenido generado con LM Studio y ComfyUI"
                else:
                    status.update(label="Se generó el contenido", state="complete")
                    return content_result.get("content", ""), "Texto generado con LM Studio"

        except Exception as e:
            return None, f"Error al generar contenido visual: {str(e)}"

    def generate_with_openai(self, topic, platform, audience, tone="profesional"):
        """Generar contenido real con OpenAI"""
        if not self.openai_key:
            return None, "API key de OpenAI no configurada"

        try:
            import openai
            openai.api_key = self.openai_key

            platform_prompts = {
                "twitter": "Crea un tweet atractivo y conciso (máximo 280 caracteres)",
                "blog": "Crea una introducción engaging para un artículo de blog",
                "instagram": "Crea un post visual para Instagram con emojis y hashtags",
                "linkedin": "Crea un post profesional para LinkedIn"
            }

            system_prompt = f"""
            Eres un experto en marketing de contenidos.
            
            Tarea: {platform_prompts.get(platform.lower(), 'Crear contenido para redes sociales')}
            Plataforma: {platform}
            Audiencia: {audience}
            Tono: {tone}
            
            Instrucciones:
            1. Crea contenido original y atractivo
            2. Optimiza para {platform}
            3. Usa un tono {tone}
            4. Incluye emojis relevantes
            5. Añade hashtags apropiados
            6. Haz que sea engaging para {audience}
            """

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Crea contenido sobre: {topic}"}
                ],
                max_tokens=400,
                temperature=0.7
            )

            return response.choices[0].message.content.strip(), "Contenido generado con OpenAI GPT-3.5"

        except Exception as e:
            return None, f"Error con OpenAI: {str(e)}"

    def generate_with_ollama(self, topic, platform, audience, tone="profesional"):
        """Generar contenido con Ollama local"""
        try:
            prompt = f"""
            Crea contenido para {platform} sobre: {topic}
            Audiencia: {audience}
            Tono: {tone}
            
            Requisitos:
            - Contenido original y atractivo
            - Optimizado para {platform}
            - Incluye emojis relevantes
            - Añade hashtags apropiados
            - Que genere engagement
            
            Responde solo con el contenido, sin explicaciones.
            """
## frontend/main.py - PARTE 2: MÉTODOS RESTANTES E INTERFAZ

    # Continuación de generate_with_ollama
            response = requests.post(
                "http://host.docker.internal:11435/api/generate",
                json={"model": "llama2", "prompt": prompt, "stream": False},
                timeout=30
            )

            if response.status_code == 200:
                content = response.json()["response"]
                return content.strip(), "Contenido generado con Ollama Llama2"
            else:
                return None, "Error conectando con Ollama"

        except requests.exceptions.ConnectionError:
            return None, "Ollama no está ejecutándose. Instala y ejecuta: ollama run llama2"
        except Exception as e:
            return None, f"Error con Ollama: {str(e)}"

    def generate_demo_content(self, topic, platform, audience, tone="profesional", creator_name="", language="es"):
        """Generar contenido demo mejorado con soporte multi-idioma"""
        def clean_hashtag(text):
            if not text:
                return "Content"
            return ''.join(word.capitalize() for word in str(text).replace(' ', '').replace(',', '').replace('.', '') if word.isalnum())[:20]

        # Crear la firma del creador
        creator_signature = ""
        if creator_name:
            creator_signature = f"\n\n---\n✍️ Creado por {creator_name}"

        platform_templates = {
            "twitter": {
                "template": "🔥 {topic} está revolucionando el mundo de {audience}!\n\n✨ Los beneficios que debes conocer:\n• Mayor productividad\n• Mejores resultados\n• Innovación constante\n\n¿Qué opinas? 👇\n\n#Innovation #{topic_hashtag} #Productivity{creator_signature}",
                "emoji": "🐦"
            },
            "blog": {
                "template": "# Descubre cómo {topic} está transformando el mundo de {audience}\n\n¿Te has preguntado alguna vez cómo {topic} puede revolucionar tu enfoque? En este artículo exploraremos las tendencias más importantes y cómo puedes aprovecharlas.\n\n## Lo que necesitas saber\n\nEn los últimos años, hemos visto un crecimiento exponencial en {topic}, especialmente entre {audience}. Esta transformación no es solo una moda pasajera, sino un cambio fundamental que está redefiniendo...{creator_signature}",
                "emoji": "📝"
            },
            "instagram": {
                "template": "✨ {topic} para {audience} ✨\n\n🎯 Tips que cambiarán tu juego:\n\n1️⃣ Empieza con fundamentos sólidos\n2️⃣ Mantén la consistencia\n3️⃣ Adapta según resultados\n4️⃣ Mide y optimiza\n\n💡 ¿Cuál implementarás primero?\n\n#{topic_hashtag} #Tips #Growth #Success #Motivation{creator_signature}",
                "emoji": "📸"
            },
            "linkedin": {
                "template": "💼 Reflexiones sobre {topic} en el contexto profesional\n\nComo profesionales en el área de {audience}, es crucial mantenernos actualizados sobre las últimas tendencias en {topic}.\n\nMis principales observaciones:\n\n🔹 La importancia de la adaptación continua\n🔹 El valor de la innovación estratégica\n🔹 La necesidad de colaboración efectiva\n🔹 El impacto en la productividad\n\n¿Qué estrategias han funcionado mejor en tu experiencia?\n\n#{topic_hashtag} #ProfessionalDevelopment #Innovation #Leadership{creator_signature}",
                "emoji": "💼"
            }
        }

        template_data = platform_templates.get(platform.lower(), platform_templates["twitter"])
        topic_hashtag = clean_hashtag(topic)

        try:
            content = template_data["template"].format(
                topic=topic,
                audience=audience,
                topic_hashtag=topic_hashtag,
                creator_signature=creator_signature
            )
        except KeyError:
            content = f"🎯 Contenido sobre {topic} para {audience}\n\nEste es un contenido optimizado para {platform} con tono {tone}.\n\n#{topic_hashtag} #Content #Marketing{creator_signature}"

        return content, f"Contenido demo para {platform} {template_data['emoji']}"

    def generate_scientific_content_multilang(self, query, target_lang=None):
        """Función para generar contenido científico multiidioma"""
        try:
            base_content = generate_scientific_content(query)
            if not target_lang:
                target_lang = st.session_state.get("selected_language", "en")

            # Si hay DeepL configurado y el idioma no es inglés, traducir
            import dotenv
            env_vars = {}
            try:
                env_vars = dotenv.dotenv_values(".env")
            except Exception:
                pass
                
            deepl_api_key = env_vars.get("DEEPL_API_KEY", "")
            if deepl_api_key and target_lang != "en":
                try:
                    from deep_translator import DeeplTranslator
                    translated = DeeplTranslator(api_key=deepl_api_key).translate(
                        text=base_content, target_lang=target_lang.upper()
                    )
                    return translated
                except Exception as e:
                    return base_content + f"\n\n[Error de traducción: {str(e)}]"
            else:
                return base_content
        except Exception as e:
            return f"Error generando contenido científico: {str(e)}"

# ===============================
# Inicializar SESSION STATE
# ===============================

if 'content_generator' not in st.session_state:
    st.session_state.content_generator = ContentGenerator()
if 'generated_content' not in st.session_state:
    st.session_state.generated_content = None
if 'selected_platform' not in st.session_state:
    st.session_state.selected_platform = "Twitter"
if 'scientific_content' not in st.session_state:
    st.session_state.scientific_content = None

# Inicializar el agente de contenido visual si está disponible
if 'content_visual_agent' not in st.session_state:
    if ContentVisualAgent:
        try:
            default_workflow_file = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "data",
                "examples",
                "flujo-imagen-post.json"
            )

            if os.path.exists(default_workflow_file):
                st.session_state.content_visual_agent = ContentVisualAgent(workflow_file=default_workflow_file)
                st.session_state.has_content_visual_agent = True
            else:
                alt_workflow_file = os.path.join(os.getcwd(), "data", "examples", "flujo-imagen-post.json")
                if os.path.exists(alt_workflow_file):
                    st.session_state.content_visual_agent = ContentVisualAgent(workflow_file=alt_workflow_file)
                    st.session_state.has_content_visual_agent = True
                else:
                    st.session_state.content_visual_agent = ContentVisualAgent()
                    st.session_state.has_content_visual_agent = True
                    st.warning("⚠️ No se encontró el archivo de flujo de trabajo para ComfyUI.")
        except Exception as e:
            st.session_state.has_content_visual_agent = False
    else:
        st.session_state.has_content_visual_agent = False

# ===============================
# INTERFAZ PRINCIPAL
# ===============================

# Hero Section Premium
st.markdown("""
<div class="hero-section fade-in">
    <h1>🧠 ContentAI Pro</h1>
    <p>Genera contenido profesional optimizado para cualquier plataforma con inteligencia artificial avanzada</p>
</div>
""", unsafe_allow_html=True)

# Sidebar mejorado
with st.sidebar:
    st.markdown("### ⚙️ Configuración Avanzada")

    # Multi-language selector
    st.markdown("#### 🌐 Idioma / Language")
    supported_languages = {
        "es": "Español",
        "en": "English",
        "fr": "Français",
        "de": "Deutsch",
        "zh": "中文",
        "pt": "Português"
    }
    selected_lang = st.selectbox(
        "Selecciona el idioma / Select language",
        options=list(supported_languages.keys()),
        format_func=lambda k: supported_languages[k],
        index=0
    )
    st.session_state.selected_language = selected_lang

    # Selección de modelo IA
    ai_models = [
        "Demo Inteligente",
        "Groq Llama3 (Gratis)",
        "OpenAI GPT-3.5",
        "Ollama Local"
    ]

    # Añadir la opción de LM Studio + ComfyUI si está disponible
    if st.session_state.get("has_content_visual_agent", False):
        ai_models.append("LM Studio + ComfyUI")

    ai_model = st.radio(
        "🤖 Motor de IA",
        ai_models,
        help="Selecciona el motor de IA para generar contenido"
    )

    # Configuración de APIs
    st.markdown("#### 🔑 Configuración de APIs")

    # Cargar variables de entorno
    import dotenv
    env_vars = {}
    try:
        env_vars = dotenv.dotenv_values(".env")
    except Exception:
        pass

    openai_key = None
    groq_key = None
    unsplash_key = None

    if ai_model == "Groq Llama3 (Gratis)":
        groq_key = st.text_input(
            "🚀 Groq API Key",
            value=env_vars.get("GROQ_API_KEY", ""),
            type="password",
            placeholder="gsk_...",
            help="Obtén tu key gratuita en console.groq.com"
        )

        if groq_key:
            st.markdown('<div class="api-status connected">✅ Groq configurado correctamente</div>', unsafe_allow_html=True)
            st.info("⚡ **Ultra rápido:** 14,400 tokens/minuto gratuitos")
        else:
            st.markdown('<div class="api-status disconnected">⚠️ API key requerida</div>', unsafe_allow_html=True)

    if ai_model == "OpenAI GPT-3.5":
        openai_key = st.text_input(
            "🤖 OpenAI API Key",
            value=env_vars.get("OPENAI_API_KEY", ""),
            type="password",
            placeholder="sk-...",
            help="Obtén tu key en platform.openai.com/api-keys"
        )

        if openai_key:
            st.markdown('<div class="api-status connected">✅ OpenAI configurado</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="api-status disconnected">⚠️ API key requerida</div>', unsafe_allow_html=True)

    # Configuración de Unsplash
    st.markdown("#### 📸 Generación de Imágenes")
    unsplash_key = st.text_input(
        "🖼️ Unsplash Access Key",
        value=env_vars.get("UNSPLASH_ACCESS_KEY", ""),
        type="password",
        placeholder="Tu access key...",
        help="Obtén tu key gratuita en unsplash.com/developers"
    )

    generate_images = st.checkbox(
        "🎨 **Generar imágenes automáticamente**",
        value=bool(unsplash_key),
        disabled=not bool(unsplash_key),
        help="Busca y adjunta imágenes profesionales automáticamente"
    )

    if unsplash_key:
        st.markdown('<div class="api-status connected">✅ Unsplash activo</div>', unsafe_allow_html=True)
        st.info("📊 **Límites:** 50 descargas/hora gratuitas")
    else:
        st.markdown('<div class="api-status disconnected">📸 Opcional - mejora el contenido</div>', unsafe_allow_html=True)

    # Configurar APIs en el generador
    st.session_state.content_generator.configure_apis(
        openai_key=openai_key if openai_key else None,
        groq_key=groq_key if groq_key else None,
        unsplash_key=unsplash_key if unsplash_key else None
    )

    # Estado del sistema
    st.markdown("### 📊 Estado del Sistema")

    if ai_model == "Demo Inteligente":
        st.markdown('<div class="api-status connected">🎯 Demo Inteligente Activo</div>', unsafe_allow_html=True)
    elif ai_model == "Groq Llama3 (Gratis)":
        status = "connected" if st.session_state.content_generator.groq_configured else "disconnected"
        icon = "🚀" if status == "connected" else "⏸️"
        text = "Groq Ultra-Rápido" if status == "connected" else "Groq Desconectado"
        st.markdown(f'<div class="api-status {status}">{icon} {text}</div>', unsafe_allow_html=True)
    elif ai_model == "OpenAI GPT-3.5":
        status = "connected" if st.session_state.content_generator.api_configured else "disconnected"
        icon = "🤖" if status == "connected" else "⏸️"
        text = "OpenAI GPT Activo" if status == "connected" else "OpenAI Desconectado"
        st.markdown(f'<div class="api-status {status}">{icon} {text}</div>', unsafe_allow_html=True)
    elif ai_model == "Ollama Local":
        st.markdown('<div class="api-status disconnected">🏠 Ollama Local (Verificar)</div>', unsafe_allow_html=True)
    elif ai_model == "LM Studio + ComfyUI":
        status = "connected" if st.session_state.get("has_content_visual_agent", False) else "disconnected"
        icon = "🎨" if status == "connected" else "⏸️"
        text = "LM Studio + ComfyUI Activo" if status == "connected" else "LM Studio + ComfyUI Desconectado"
        st.markdown(f'<div class="api-status {status}">{icon} {text}</div>', unsafe_allow_html=True)

    img_status = "connected" if st.session_state.content_generator.unsplash_configured else "disconnected"
    img_icon = "🎨" if img_status == "connected" else "📷"
    img_text = "Imágenes Automáticas" if img_status == "connected" else "Solo Texto"
    st.markdown(f'<div class="api-status {img_status}">{img_icon} {img_text}</div>', unsafe_allow_html=True)

    # Información de costos
    st.markdown("### 💰 Información de Costos")

    cost_info = {
        "Demo Inteligente": ("🆓", "Completamente gratuito", "success"),
        "Groq Llama3 (Gratis)": ("🚀", "Gratuito + Ultra rápido", "success"),
        "OpenAI GPT-3.5": ("💳", "~$0.002 por 1K tokens", "info"),
        "Ollama Local": ("🏠", "Gratuito (hardware local)", "info"),
        "LM Studio + ComfyUI": ("🎨", "Gratuito (hardware local)", "info")
    }

    if ai_model in cost_info:
        icon, text, type_msg = cost_info[ai_model]
        if type_msg == "success":
            st.success(f"{icon} {text}")
        else:
            st.info(f"{icon} {text}")

    if st.session_state.content_generator.unsplash_configured:
        st.info("📸 Unsplash: 50 imágenes/hora gratuitas")

    # Sección de Generador Científico (RAG)
    st.markdown("### 🧬 Generador Científico (RAG)")
    scientific_query = st.text_input(
        "🔬 Tema científico (ej: física cuántica, IA, biomedicina)",
        help="Genera contenido científico divulgativo usando RAG y arXiv"
    )

    if st.button("🧬 Generar contenido científico", key="generate_scientific"):
        if scientific_query:
            with st.spinner("Generando contenido científico..."):
                scientific_result = st.session_state.content_generator.generate_scientific_content_multilang(
                    scientific_query, st.session_state.get("selected_language", "en")
                )
                st.session_state.scientific_content = scientific_result
        else:
            st.error("Por favor, ingresa un tema científico")

# Layout principal
col1, col2 = st.columns([3, 2], gap="large")

with col1:
    st.markdown("### 📝 Crear Contenido Profesional")

    with st.form("content_form", clear_on_submit=False, border=False):
        topic = st.text_input(
            "💡 **Tema Principal**",
            placeholder="Ejemplo: Inteligencia Artificial, Marketing Digital, Productividad Personal...",
            help="🎯 Describe el tema central de tu contenido"
        )

        st.markdown("#### 📱 Selecciona tu Plataforma")

        platforms = [
            {"name": "Twitter", "icon": "🐦", "desc": "Tweets virales y concisos"},
            {"name": "Blog", "icon": "📝", "desc": "Artículos informativos"},
            {"name": "Instagram", "icon": "📸", "desc": "Posts visuales atractivos"},
            {"name": "LinkedIn", "icon": "💼", "desc": "Contenido profesional"}
        ]

        platform_cols = st.columns(2)

        for i, platform_data in enumerate(platforms):
            col_idx = i % 2
            with platform_cols[col_idx]:
                if st.form_submit_button(
                    f"{platform_data['icon']} **{platform_data['name']}**\n{platform_data['desc']}",
                    help=f"Optimizar contenido para {platform_data['name']}",
                    use_container_width=True,
                    type="secondary"
                ):
                    st.session_state.selected_platform = platform_data['name']

        if st.session_state.selected_platform:
            selected_platform_data = next(p for p in platforms if p['name'] == st.session_state.selected_platform)
            st.success(f"✅ **Plataforma seleccionada:** {selected_platform_data['icon']} **{selected_platform_data['name']}** - {selected_platform_data['desc']}")

        col_a, col_b, col_c = st.columns(3)

        with col_a:
            audience = st.text_input(
                "🎯 **Audiencia Objetivo**",
                placeholder="Ejemplo: emprendedores, estudiantes, marketers...",
                help="👥 Define específicamente a quién va dirigido el contenido"
            )

        with col_b:
            tone = st.selectbox(
                "🎭 **Tono de Comunicación**",
                ["profesional", "casual", "divertido", "inspiracional", "educativo", "técnico"],
                help="🗣️ Selecciona el estilo de comunicación apropiado"
            )

        with col_c:
            creator_name = st.text_input(
                "✍️ **Creado por**",
                placeholder="Tu nombre o marca...",
                help="👤 Nombre que aparecerá como autor del contenido"
            )

        generate_button = st.form_submit_button(
            "🚀 **Generar Contenido Profesional**",
            type="primary",
            use_container_width=True
        )

        if generate_button:
            if not topic:
                st.error("⚠️ **Por favor, ingresa un tema para tu contenido**")
            elif not st.session_state.selected_platform:
                st.error("⚠️ **Por favor, selecciona una plataforma objetivo**")
            else:
                progress_container = st.container()

                with progress_container:
                    st.markdown("### 🤖 Generando Contenido...")

                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    steps = [
                        ("🧠 **Analizando tema y audiencia...**", 15),
                        ("🎯 **Optimizando para la plataforma...**", 30),
                        ("✍️ **Generando contenido atractivo...**", 50),
                        ("🖼️ **Buscando imagen perfecta...**" if generate_images else "🎨 **Aplicando estilo profesional...**", 70),
                        ("🔧 **Refinando y optimizando...**", 85),
                        ("✅ **¡Contenido profesional listo!**", 100)
                    ]

                    for step_text, progress in steps:
                        status_text.markdown(f'<div class="progress-step">{step_text}</div>', unsafe_allow_html=True)
                        progress_bar.progress(progress)
                        time.sleep(0.7)

                    generator = st.session_state.content_generator
                    platform = st.session_state.selected_platform

                    # Generar contenido según el modelo seleccionado
                    if ai_model == "Groq Llama3 (Gratis)" and generator.groq_configured:
                        content, status = generator.generate_with_groq(topic, platform, audience, tone, creator_name)
                    elif ai_model == "OpenAI GPT-3.5" and generator.api_configured:
                        content, status = generator.generate_with_openai(topic, platform, audience, tone)
                    elif ai_model == "Ollama Local":
                        content, status = generator.generate_with_ollama(topic, platform, audience, tone)
                    elif ai_model == "LM Studio + ComfyUI" and st.session_state.get("has_content_visual_agent", False):
                        content, status = generator.generate_with_lmstudio_comfyui(topic, platform, audience, tone)
                    else:  # Demo Inteligente
                        content, status = generator.generate_demo_content(
                            topic, platform, audience, tone, creator_name, st.session_state.get("selected_language", "es")
                        )

                    # Buscar imagen en Unsplash si está configurado
                    image_data = None
                    image_status = ""
                    search_keyword_used = ""

                    if generate_images and generator.unsplash_configured and content:
                        status_text.markdown('<div class="progress-step">🧠 **Analizando contenido para imagen perfecta...**</div>', unsafe_allow_html=True)

                        image_data, image_status = generator.search_unsplash_image_intelligent(
                            content=content,
                            topic=topic,
                            platform=platform
                        )

                        if image_data:
                            search_keyword_used = "Análisis semántico inteligente"

                    if content:
                        # Guardar resultado
                        result_data = {
                            'topic': topic,
                            'platform': platform,
                            'audience': audience,
                            'tone': tone,
                            'creator_name': creator_name,
                            'content': content,
                            'status': status,
                            'model': ai_model,
                            'image_data': image_data,
                            'image_status': image_status,
                            'search_keyword_used': search_keyword_used,
                            'timestamp': datetime.now(),
                            'word_count': len(str(content).split()),
                            'char_count': len(str(content)),
                            'hashtags': len([word for word in str(content).split() if word.startswith('#')])
                        }

                        st.session_state.generated_content = result_data

                        status_text.success("✅ **¡Contenido profesional generado exitosamente!**")
                        progress_bar.empty()
                        st.balloons()

                    else:
                        status_text.error(f"❌ **Error en la generación:** {status}")
                        progress_bar.empty()

with col2:
    st.markdown('<div class="tips-card">', unsafe_allow_html=True)
    st.markdown("### 💡 Sugerencias Inteligentes")

    platform_tips = {
        "Twitter": {
            "icon": "🐦",
            "main_tip": "Mantén el mensaje bajo 280 caracteres",
            "tips": [
                "Usa hashtags trending para mayor alcance",
                "Incluye una pregunta para generar engagement",
                "Agrega emojis para mayor visibilidad",
                "Menciona usuarios relevantes con @"
            ]
        },
        "Blog": {
            "icon": "📝",
            "main_tip": "Estructura clara con títulos atractivos",
            "tips": [
                "Incluye subtítulos para mejor lectura",
                "Usa listas y bullet points",
                "Agrega un call-to-action al final",
                "Optimiza para SEO con keywords"
            ]
        },
        "Instagram": {
            "icon": "📸",
            "main_tip": "Contenido visual y emojis llamativos",
            "tips": [
                "Usa hasta 30 hashtags relevantes",
                "Incluye stories y reels para mayor alcance",
                "Agrega ubicación para descubrimiento local",
                "Programa posts en horas de mayor actividad"
            ]
        },
        "LinkedIn": {
            "icon": "💼",
            "main_tip": "Enfócate en valor profesional y networking",
            "tips": [
                "Comparte insights de la industria",
                "Usa un tono profesional pero accesible",
                "Incluye experiencias personales relevantes",
                "Haz preguntas para fomentar discusión"
            ]
        }
    }

    current_platform = st.session_state.selected_platform
    if current_platform in platform_tips:
        tip_data = platform_tips[current_platform]
        st.markdown(f"#### {tip_data['icon']} {current_platform}")
        st.info(f"**💡 Tip principal:** {tip_data['main_tip']}")

        st.markdown("**📋 Mejores prácticas:**")
        for tip in tip_data['tips']:
            st.markdown(f"• {tip}")
    else:
        st.info("💡 Selecciona una plataforma para ver tips específicos")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="tips-card">', unsafe_allow_html=True)
    st.markdown("#### 📄 Plantillas Rápidas")

    quick_topics = [
        {"text": "🔥 Tendencias 2025", "emoji": "🔥"},
        {"text": "💡 Tips de productividad", "emoji": "💡"},
        {"text": "🚀 Innovación tecnológica", "emoji": "🚀"},
        {"text": "📈 Estrategias de crecimiento", "emoji": "📈"},
        {"text": "🎯 Marketing efectivo", "emoji": "🎯"}
    ]

    for topic_data in quick_topics:
        if st.button(
            f"{topic_data['emoji']} {topic_data['text']}",
            use_container_width=True,
            key=f"template_{topic_data['text']}",
            help=f"Usar '{topic_data['text']}' como tema"
        ):
            st.info(f"💡 Tema seleccionado: **{topic_data['text']}**")

    st.markdown('</div>', unsafe_allow_html=True)

# Mostrar contenido generado
if st.session_state.generated_content:
    content_data = st.session_state.generated_content

    st.markdown("---")
    st.markdown("### 📊 Contenido Generado Profesional")

    # Métricas
    col1, col2, col3, col4, col5 = st.columns(5)

    metrics = [
        ("Plataforma", content_data['platform'], "📱"),
        ("Motor IA", content_data['model'].split()[0], "🤖"),
        ("Caracteres", f"{content_data['char_count']:,}", "📝"),
        ("Palabras", f"{content_data['word_count']:,}", "📊"),
        ("Hashtags", content_data.get('hashtags', 0), "#️⃣")
    ]

    for i, (label, value, icon) in enumerate(metrics):
        with [col1, col2, col3, col4, col5][i]:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
                <div style="font-size: 1.2rem; font-weight: 600; color: var(--primary-color); margin: 0.5rem 0;">{value}</div>
                <div style="font-size: 0.875rem; color: var(--text-secondary); font-weight: 500; text-transform: uppercase;">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    # Contenido final
    st.markdown(f"""
    <div class="generated-content">
        <h4>🎯 Contenido Optimizado para {content_data['platform']}</h4>
        <div class="content-preview">
            {content_data['content'].replace(chr(10), '<br>')}
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1rem;">
            <small style="color: var(--text-secondary);">✨ {content_data['status']}</small>
            <small style="color: var(--text-secondary);">🕒 {content_data['timestamp'].strftime('%H:%M:%S')}</small>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Mostrar imagen de Unsplash si existe
    if content_data.get('image_data'):
        st.markdown("#### 📸 Imagen Profesional de Unsplash")

        image_data = content_data['image_data']

        col_img1, col_img2 = st.columns([3, 2])

        with col_img1:
            st.markdown('<div class="image-preview">', unsafe_allow_html=True)
            st.image(
                image_data['url'],
                caption=f"📷 Foto por {image_data['author']} en Unsplash",
                use_container_width=True
            )
            st.markdown('</div>', unsafe_allow_html=True)

        with col_img2:
            st.markdown("**🎨 Detalles de la Imagen:**")
            st.markdown(f"**👤 Autor:** [{image_data['author']}]({image_data['author_url']})")

            if image_data['description']:
                st.markdown(f"**📝 Descripción:** {image_data['description'][:100]}{'...' if len(image_data['description']) > 100 else ''}")

            st.markdown(f"**📐 Dimensiones:** {image_data.get('width', 'N/A')} × {image_data.get('height', 'N/A')}")

            if st.button("📥 **Descargar Imagen Original**", use_container_width=True, key="download_img"):
                st.success("✅ **Imagen lista para descargar**")
                st.info("💡 **Tip:** Haz clic derecho en la imagen → 'Guardar imagen como...'")

    # Mostrar imagen generada por ComfyUI
    elif content_data.get('image_path') and os.path.exists(content_data['image_path']):
        st.markdown("#### 🎨 Imagen Generada con ComfyUI")

        col_img1, col_img2 = st.columns([3, 2])

        with col_img1:
            st.markdown('<div class="image-preview">', unsafe_allow_html=True)
            st.image(
                content_data['image_path'],
                caption="🖼️ Imagen generada con IA",
                use_container_width=True
            )
            st.markdown('</div>', unsafe_allow_html=True)

        with col_img2:
            st.markdown("**🎨 Detalles de la Imagen:**")
            st.markdown("**🤖 Generada por:** ComfyUI")
            if content_data.get('image_prompt'):
                st.markdown(f"**📝 Prompt:** {content_data['image_prompt'][:100]}{'...' if len(content_data.get('image_prompt', '')) > 100 else ''}")
            st.markdown(f"**📊 Estado:** {content_data.get('image_status', 'Imagen generada con éxito')}")

            if st.button("📥 **Descargar Imagen**", use_container_width=True, key="download_comfy_img"):
                st.success("✅ **Imagen lista para descargar**")
                st.info("💡 **Tip:** Haz clic derecho en la imagen → 'Guardar imagen como...'")

    elif content_data.get('image_status'):
        st.markdown("#### 📸 Estado de Imagen")
        if "No se encontraron" in content_data['image_status'] or "Sin resultados" in content_data['image_status']:
            st.warning(f"⚠️ {content_data['image_status']}")
            st.info("💡 Intenta con un tema más específico o verifica tu API key de Unsplash")
        else:
            st.info(f"ℹ️ {content_data['image_status']}")

    # Botones de acción
    st.markdown("#### 🛠️ Acciones Disponibles")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📋 **Copiar Contenido**", use_container_width=True, key="copy_content"):
            st.success("✅ **Contenido copiado al portapapeles!**")
            st.code(content_data['content'], language=None)

    with col2:
        if st.button("🔄 **Regenerar**", use_container_width=True, key="regenerate"):
            st.session_state.generated_content = None
            st.info("🔄 **Listo para generar una nueva versión**")
            st.rerun()

    with col3:
        if st.button("📊 **Analizar**", use_container_width=True, key="analyze"):
            # Mostrar análisis inteligente de keywords
            generator = st.session_state.content_generator
            if generator.unsplash_configured:
                try:
                    extracted_concepts = generator.extract_visual_concepts_from_content(
                        content_data['content'], content_data['topic']
                    )
                    st.success(f"🎯 **Conceptos extraídos automáticamente:** {extracted_concepts}")
                    st.info("💡 Estos conceptos se generan analizando el contenido real, no usando diccionarios estáticos")
                except Exception as e:
                    st.error(f"Error en análisis: {str(e)}")
            else:
                st.info("📊 **Análisis básico disponible**")

    with col4:
        # Preparar datos para exportar
        export_data = f"""# Contenido Generado - {content_data['platform']}

**Tema:** {content_data['topic']}
**Audiencia:** {content_data['audience']}
**Tono:** {content_data['tone']}
**Creador:** {content_data.get('creator_name', 'No especificado')}
**Fecha:** {content_data['timestamp'].strftime('%Y-%m-%d %H:%M')}
**Motor:** {content_data['model']}

## Estadísticas:
- **Caracteres:** {content_data['char_count']}
- **Palabras:** {content_data['word_count']}
- **Hashtags:** {content_data.get('hashtags', 0)}

## Contenido:

{content_data['content']}

---
Generado con ContentAI Pro
"""

        st.download_button(
            label="📤 **Exportar**",
            data=export_data,
            file_name=f"contenido_{content_data['platform'].lower()}_{content_data['timestamp'].strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True
        )

    # Detalles del proceso expandible
    with st.expander("🔍 Ver Detalles del Proceso"):
        st.markdown(f"""
        **📝 Parámetros utilizados:**
        - **Tema:** {content_data['topic']}
        - **Audiencia:** {content_data['audience']}
        - **Tono:** {content_data['tone']}
        - **Creador:** {content_data.get('creator_name', 'No especificado')}
        - **Modelo:** {content_data['model']}
        - **Timestamp:** {content_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}

        **📸 Información de imagen:**
        - **Estado:** {content_data.get('image_status', 'Sin imagen')}
        - **Método:** {content_data.get('search_keyword_used', 'N/A')}
        - **Fuente:** {"Unsplash" if content_data.get('image_data') else "ComfyUI" if content_data.get('image_path') else "No aplicable"}
        """)

        if content_data.get('image_data'):
            image_data = content_data['image_data']
            st.markdown(f"""
            **🖼️ Detalles de imagen Unsplash:**
            - **Autor:** {image_data['author']}
            - **Descripción:** {image_data.get('description', 'Sin descripción')}
            - **Resolución:** {image_data.get('width', 'N/A')} x {image_data.get('height', 'N/A')}
            - **URL:** [Ver en Unsplash]({image_data['author_url']})
            """)

        elif content_data.get('image_path'):
            st.markdown(f"""
            **🎨 Detalles de imagen ComfyUI:**
            - **Ruta:** {content_data['image_path']}
            - **Prompt:** {content_data.get('image_prompt', 'No disponible')}
            - **Estado:** {content_data.get('image_status', 'Generada exitosamente')}
            """)

# Mostrar contenido científico generado
if st.session_state.get('scientific_content'):
    st.markdown("---")
    st.markdown("### 🧬 Contenido Científico Generado (RAG)")
    st.markdown(f"""
    <div class='generated-content'>
        <h4>🔬 {scientific_query if 'scientific_query' in locals() else 'Contenido Científico'}</h4>
        <div class='content-preview'>
            {st.session_state.scientific_content.replace(chr(10), '<br>')}
        </div>
        <small style="color: var(--text-secondary);">✨ Generado con RAG, LangChain y LangSmith</small>
    </div>
    """, unsafe_allow_html=True)

# Footer con información mejorada
st.markdown("---")
st.markdown("### 🚀 ContentAI Pro - Información del Sistema")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    #### 🔮 Próximas Funciones
    - 📅 **Programación automática**
    - 🎨 **Editor de imágenes integrado**
    - 📊 **Analytics de engagement**
    - 🔗 **Integración con APIs sociales**
    - 🧪 **A/B Testing automático**
    """)

with col2:
    st.markdown("""
    #### 🤖 Motores IA Disponibles
    - 🚀 **Groq Llama3** (Ultra rápido)
    - 🤖 **OpenAI GPT-3.5/4** (Versátil)
    - 🏠 **Ollama** (Local/Privado)
    - 🎯 **Demo Inteligente** (Gratuito)
    - 🎨 **LM Studio + ComfyUI** (Visual)
    """)

with col3:
    st.markdown("""
    #### 📱 Plataformas Soportadas
    - 🐦 **Twitter/X** (Posts y threads)
    - 📸 **Instagram** (Posts y stories)
    - 💼 **LinkedIn** (Posts profesionales)
    - 📝 **Blog/Website** (Artículos)
    - 🔜 **TikTok, YouTube** (Próximamente)
    """)

with col4:
    st.markdown("""
    #### 🎨 Características Premium
    - 🖼️ **Imágenes automáticas** (Unsplash)
    - 🧠 **Análisis semántico IA**
    - 📊 **Métricas en tiempo real**
    - 💾 **Exportación avanzada**
    - 🧬 **Generador científico RAG**
    """)

# Información de versión y créditos
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: var(--text-secondary); padding: 2rem 0;">
    <p><strong>ContentAI Pro v2.0 Unificado</strong> | Desarrollado con ❤️ usando Streamlit</p>
    <p>🚀 <strong>Características:</strong> Multi-idioma, RAG Científico, Análisis Semántico, Generación Visual</p>
    <p>📧 <strong>Soporte:</strong> Múltiples motores IA | 🌐 <strong>Idiomas:</strong> ES, EN, FR, DE, ZH, PT</p>
</div>
""", unsafe_allow_html=True)         