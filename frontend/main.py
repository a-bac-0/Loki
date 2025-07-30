## frontend/main.py - PARTE 1: CONFIGURACIÓN E IMPORTS
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta
import requests
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.rag.rag_chain import generate_scientific_content

try:
    from langsmith import LangSmithCallbackHandler
except ImportError:
    try:
        from langchain.callbacks.tracers.langsmith import LangSmithCallbackHandler
    except ImportError:
        LangSmithCallbackHandler = None

# Configuración de página con estilo Meta
st.set_page_config(
    page_title="ContentAI Pro | Meta Style",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS Estilo Meta profesional
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    :root {
        --meta-blue: #1877f2;
        --meta-blue-dark: #166fe5;
        --meta-blue-light: #42a5f5;
        --meta-gray-50: #f8f9fa;
        --meta-gray-100: #e4e6ea;
        --meta-gray-200: #dadde1;
        --meta-gray-300: #ced0d4;
        --meta-gray-400: #8a8d91;
        --meta-gray-500: #65676b;
        --meta-gray-600: #4e4f50;
        --meta-gray-700: #3e4042;
        --meta-gray-800: #1c1e21;
        --meta-gray-900: #18191a;
        --meta-white: #ffffff;
        --meta-hero: linear-gradient(90deg, #8e2de2 0%, #4a00e0 100%);;
        --meta-green: #00a400;
        --meta-red: #fa3e3e;
        --meta-orange: #ff6600;
        --meta-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        --meta-shadow-lg: 0 8px 30px rgba(0, 0, 0, 0.12);
        --meta-radius: 8px;
        --meta-radius-lg: 12px;
        --meta-transition: all 0.2s cubic-bezier(0.17, 0.17, 0, 1);
    }

    /* Reset y base */
    .main .block-container {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        padding: 2rem 1.5rem;
        max-width: 1200px;
        color: var(--meta-gray-800);
        background: var(--meta-gray-50);
    }

    /* Tipografía estilo Meta */
    h1, h2, h3, h4, h5, h6 {
        font-weight: 700;
        letter-spacing: -0.02em;
        line-height: 1.2;
        color: var(--meta-gray-900);
    }

    /* Header principal estilo Meta */
    .meta-header {
        background: var(--meta-hero);
        padding: 3rem 2rem;
        border-radius: var(--meta-radius-lg);
        text-align: center;
        margin-bottom: 2rem;
        color: var(--meta-white);
        position: relative;
        overflow: hidden;
        box-shadow: var(--meta-shadow-lg);
    }

    .meta-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, transparent 50%);
        z-index: 1;
    }

    .meta-header h1 {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0 0 0.5rem 0;
        position: relative;
        z-index: 2;
        color: var(--meta-white);
    }

    .meta-header p {
        font-size: 1.125rem;
        opacity: 0.95;
        margin: 0;
        position: relative;
        z-index: 2;
        font-weight: 400;
    }

    /* Cards estilo Meta */
    .meta-card {
        background: var(--meta-white);
        border-radius: var(--meta-radius);
        padding: 0.5rem;
        margin: 1rem 0;
        border: 1px solid var(--meta-gray-200);
        box-shadow: var(--meta-shadow);
        transition: var(--meta-transition);
    }

    .meta-card-line {
        background: var(--meta-hero);
        border-radius: var(--meta-radius);
        padding: 0.5rem;
        border: 1px solid var(--meta-gray-200);
        box-shadow: var(--meta-shadow);
        transition: var(--meta-transition);
    }

    .meta-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--meta-shadow-lg);
        border-color: var(--meta-blue-light);
    }

    /* Botones estilo Meta */
    .stButton > button {
        background: var(--meta-blue) !important;
        color: var(--meta-white) !important;
        border: none !important;
        border-radius: var(--meta-radius) !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        transition: var(--meta-transition) !important;
        width: 100% !important;
        text-transform: none !important;
        letter-spacing: 0 !important;
    }

    .stButton > button:hover {
        background: var(--meta-blue-dark) !important;
        transform: translateY(-1px) !important;
        box-shadow: var(--meta-shadow-lg) !important;
    }

    /* Estados de API estilo Meta */
    .meta-status {
        padding: 0.75rem 1rem;
        border-radius: var(--meta-radius);
        margin: 0.5rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-weight: 500;
        font-size: 0.875rem;
        transition: var(--meta-transition);
    }

    .meta-status.connected {
        background: #e8f5e8;
        color: var(--meta-green);
        border: 1px solid #c3e6c3;
    }

    .meta-status.disconnected {
        background: #ffeaea;
        color: var(--meta-red);
        border: 1px solid #ffb3b3;
    }

    /* Inputs estilo Meta */
    .stTextInput > div > div > input {
        border-radius: var(--meta-radius) !important;
        border: 2px solid var(--meta-gray-200) !important;
        padding: 0.75rem 1rem !important;
        font-size: 0.875rem !important;
        transition: var(--meta-transition) !important;
        background: var(--meta-white) !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: var(--meta-blue) !important;
        box-shadow: 0 0 0 2px rgba(24, 119, 242, 0.1) !important;
    }

    /* Selectbox estilo Meta */
    .stSelectbox > div > div {
        border-radius: var(--meta-radius) !important;
        border: 2px solid var(--meta-gray-200) !important;
    }

    /* Content preview estilo Meta */
    .meta-content-preview {
        background: var(--meta-white);
        border: 1px solid var(--meta-gray-200);
        border-radius: var(--meta-radius);
        padding: 1.5rem;
        margin: 1rem 0;
        font-family: 'Inter', sans-serif;
        line-height: 1.6;
        box-shadow: var(--meta-shadow);
    }

    /* Sidebar estilo Meta */
    .css-1d391kg {
        background: var(--meta-white) !important;
        border-right: 1px solid var(--meta-gray-200) !important;
    }

    /* Métricas estilo Meta */
    .meta-metric {
        background: var(--meta-white);
        padding: 1rem;
        border-radius: var(--meta-radius);
        border: 1px solid var(--meta-gray-200);
        text-align: center;
        transition: var(--meta-transition);
        box-shadow: var(--meta-shadow);
    }

    .meta-metric:hover {
        transform: translateY(-2px);
        box-shadow: var(--meta-shadow-lg);
    }

    .meta-metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--meta-blue);
        margin: 0.25rem 0;
    }

    .meta-metric-label {
        font-size: 0.75rem;
        color: var(--meta-gray-500);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Radio buttons estilo Meta */
    .stRadio > div {
        gap: 0.5rem !important;
    }

    .stRadio > div > label {
        background: var(--meta-white) !important;
        border: 2px solid var(--meta-gray-200) !important;
        border-radius: var(--meta-radius) !important;
        padding: 0.75rem 1rem !important;
        margin: 0.25rem 0 !important;
        transition: var(--meta-transition) !important;
        cursor: pointer !important;
    }

    .stRadio > div > label:hover {
        border-color: var(--meta-blue-light) !important;
        background: var(--meta-gray-50) !important;
    }

    /* Animaciones */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .fade-in-up {
        animation: fadeInUp 0.4s ease-out;
    }

    /* Responsive */
    @media (max-width: 768px) {
        .meta-header h1 {
            font-size: 2rem;
        }
        .meta-header {
            padding: 2rem 1rem;
        }
        .main .block-container {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Importar el agente de contenido visual si está disponible
try:
    from app.agents.content_visual_agent import ContentVisualAgent
except ImportError:
    ContentVisualAgent = None

## frontend/main.py - PARTE 2: CONTENTGENERATOR CLASS

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
## frontend/main.py - PARTE 3: MÉTODOS DE GENERACIÓN IA

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
            Eres un experto en marketing de contenidos y redes sociales con estilo Meta/Facebook.
            
            Tarea: {platform_instructions.get(platform.lower(), 'Crear contenido para redes sociales')}
            Plataforma: {platform}
            Audiencia: {audience}
            Tono: {tone}
            
            Instrucciones:
            1. Crea contenido 100% original y atractivo
            2. Usa un tono {tone} pero moderno
            3. Optimiza específicamente para {platform}
            4. Incluye emojis relevantes (estilo Meta)
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

                return content, "✅ Contenido generado con Groq Llama3-70B"
            elif response.status_code == 401:
                return None, "❌ API key de Groq inválida"
            elif response.status_code == 429:
                return None, "⏳ Límite de velocidad alcanzado. Espera un momento."
            else:
                return None, f"❌ Error en API de Groq: {response.status_code}"

        except requests.exceptions.Timeout:
            return None, "⏳ Timeout conectando con Groq"
        except Exception as e:
            return None, f"❌ Error con Groq: {str(e)}"

    def generate_with_lmstudio_comfyui(self, topic, platform, audience, tone="profesional"):
        """Genera contenido de texto e imagen utilizando LM Studio y ComfyUI"""
        try:
            if not st.session_state.get("has_content_visual_agent", False):
                return None, "❌ El agente de contenido visual no está disponible."

            agent = st.session_state.content_visual_agent
            services = agent.check_services()

            if not all(services.values()):
                return None, "❌ No se pudo conectar a LM Studio o ComfyUI."

            with st.status("🎨 Generando contenido visual...", expanded=True) as status:
                status.update(label="🧠 Generando texto con LM Studio...")

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
                    status.update(label="✅ ¡Contenido visual generado con éxito!", state="complete")
                    return content_result.get("content", ""), "✅ Contenido generado con LM Studio y ComfyUI"
                else:
                    status.update(label="✅ Se generó el contenido", state="complete")
                    return content_result.get("content", ""), "✅ Texto generado con LM Studio"

        except Exception as e:
            return None, f"❌ Error al generar contenido visual: {str(e)}"

    def generate_with_openai(self, topic, platform, audience, tone="profesional", creator_name=""):
        """Generar contenido real con OpenAI"""
        if not self.openai_key:
            return None, "❌ API key de OpenAI no configurada"

        try:
            import openai
            openai.api_key = self.openai_key

            platform_prompts = {
                "twitter": "Crea un tweet atractivo y conciso (máximo 280 caracteres)",
                "blog": "Crea una introducción engaging para un artículo de blog",
                "instagram": "Crea un post visual para Instagram con emojis y hashtags",
                "linkedin": "Crea un post profesional para LinkedIn"
            }

            creator_instruction = ""
            if creator_name:
                creator_instruction = f"\nAl final, añade: '---\n✍️ Creado por {creator_name}'"

            system_prompt = f"""
            Eres un experto en marketing de contenidos con estilo Meta/Facebook.
            
            Tarea: {platform_prompts.get(platform.lower(), 'Crear contenido para redes sociales')}
            Plataforma: {platform}
            Audiencia: {audience}
            Tono: {tone}
            
            Instrucciones:
            1. Crea contenido original y atractivo estilo Meta
            2. Optimiza para {platform}
            3. Usa un tono {tone}
            4. Incluye emojis relevantes
            5. Añade hashtags apropiados
            6. Haz que sea engaging para {audience}{creator_instruction}
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

            content = response.choices[0].message.content.strip()
            if creator_name and f"Creado por {creator_name}" not in content:
                content += f"\n\n---\n✍️ Creado por {creator_name}"

            return content, "✅ Contenido generado con OpenAI GPT-3.5"

        except Exception as e:
            return None, f"❌ Error con OpenAI: {str(e)}"

    def generate_with_ollama(self, topic, platform, audience, tone="profesional", creator_name=""):
        """Generar contenido con Ollama local"""
        try:
            creator_instruction = ""
            if creator_name:
                creator_instruction = f"\nAl final, añade: '---\n✍️ Creado por {creator_name}'"

            prompt = f"""
            Crea contenido para {platform} sobre: {topic}
            Audiencia: {audience}
            Tono: {tone}
            Estilo: Meta/Facebook profesional
            
            Requisitos:
            - Contenido original y atractivo
            - Optimizado para {platform}
            - Incluye emojis relevantes
            - Añade hashtags apropiados
            - Que genere engagement{creator_instruction}
            
            Responde solo con el contenido, sin explicaciones.
            """

            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "llama2", "prompt": prompt, "stream": False},
                timeout=30
            )

            if response.status_code == 200:
                content = response.json()["response"].strip()
                if creator_name and f"Creado por {creator_name}" not in content:
                    content += f"\n\n---\n✍️ Creado por {creator_name}"
                return content, "✅ Contenido generado con Ollama Llama2"
            else:
                return None, "❌ Error conectando con Ollama"

        except requests.exceptions.ConnectionError:
            return None, "❌ Ollama no está ejecutándose. Instala y ejecuta: ollama run llama2"
        except Exception as e:
            return None, f"❌ Error con Ollama: {str(e)}"

    def generate_demo_content(self, topic, platform, audience, tone="profesional", creator_name="", language="es"):
        """Generar contenido demo mejorado con estilo Meta"""
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
                "template": "⚡ {topic} está revolucionando {audience}!\n\n🎯 Lo que necesitas saber:\n• Impacto inmediato\n• Resultados medibles\n• Innovación constante\n\n¿Qué opinas? 👇\n\n#{topic_hashtag} #Innovation #MetaStyle{creator_signature}",
                "emoji": "🐦"
            },
            "blog": {
                "template": "# {topic}: El futuro de {audience}\n\n💡 En el ecosistema digital actual, {topic} no es solo una tendencia: es una revolución que está redefiniendo cómo {audience} interact úa con la tecnología.\n\n## 🚀 Impacto transformador\n\nLos últimos datos muestran un crecimiento exponencial en {topic}. Esta transformación va más allá de simples mejoras: representa un cambio fundamental en...\n\n✨ **Key insights que debes conocer**{creator_signature}",
                "emoji": "📝"
            },
            "instagram": {
                "template": "✨ {topic} para {audience} ✨\n\n🎯 Game-changing tips:\n\n1️⃣ Empieza con bases sólidas\n2️⃣ Consistencia = Resultados\n3️⃣ Adapta según datos\n4️⃣ Mide, optimiza, repite\n\n💫 ¿Cuál implementas hoy?\n\n#{topic_hashtag} #MetaStyle #Growth #Innovation{creator_signature}",
                "emoji": "📸"
            },
            "linkedin": {
                "template": "🚀 Reflexiones sobre {topic} en el contexto profesional\n\nComo comunidad de {audience}, debemos mantenernos a la vanguardia de {topic}.\n\n💡 Insights clave:\n\n🔹 Adaptación continua es fundamental\n🔹 La innovación estratégica genera valor\n🔹 Colaboración efectiva multiplica resultados\n🔹 El impacto en productividad es medible\n\n¿Qué estrategias han funcionado en tu experiencia?\n\n#{topic_hashtag} #MetaStyle #ProfessionalGrowth #Leadership{creator_signature}",
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
            content = f"⚡ Contenido sobre {topic} para {audience}\n\nEste es contenido optimizado para {platform} con tono {tone} y estilo Meta.\n\n#{topic_hashtag} #MetaStyle #Content{creator_signature}"

        return content, f"✅ Contenido demo para {platform} {template_data['emoji']}"

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
            return f"❌ Error generando contenido científico: {str(e)}"

## frontend/main.py - PARTE 4: SESSION STATE Y SIDEBAR

# ===============================
# INICIALIZAR SESSION STATE
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

# Header estilo Meta
st.markdown("""
<div class="meta-header fade-in-up">
    <h1>⚡ ContentAI Pro</h1>
    <p>✨ Únete a ContentAI Pro y transforma tu contenido:  
De tweets virales a artículos científicos con RAG.</p>
    <p>Todo en una sola.</p>
</div>
""", unsafe_allow_html=True)

# Sidebar mejorado estilo Meta
with st.sidebar:
    st.markdown("### ⚙️ Configuración")

    # Multi-language selector estilo Meta
    st.markdown("#### 🌐 Idioma")
    supported_languages = {
        "es": "🇪🇸 Español",
        "en": "🇺🇸 English",
        "fr": "🇫🇷 Français",
        "de": "🇩🇪 Deutsch",
        "zh": "🇨🇳 中文",
        "pt": "🇧🇷 Português"
    }
    selected_lang = st.selectbox(
        "Selecciona idioma",
        options=list(supported_languages.keys()),
        format_func=lambda k: supported_languages[k],
        index=0,
        key="language_selector"
    )
    st.session_state.selected_language = selected_lang

    # Selección de modelo IA estilo Meta
    st.markdown("#### 🤖 Motor de IA")
    
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
        "Selecciona el motor",
        ai_models,
        help="Elige el motor de IA para generar contenido",
        key="ai_model_selector"
    )

    # Configuración de APIs estilo Meta
    st.markdown("#### 🔑 APIs")

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

    # Configuración específica según modelo
    if ai_model == "Groq Llama3 (Gratis)":
        st.markdown("##### 🚀 Groq Configuration")
        groq_key = st.text_input(
            "API Key",
            value=env_vars.get("GROQ_API_KEY", ""),
            type="password",
            placeholder="gsk_...",
            help="Obtén tu key gratuita en console.groq.com",
            key="groq_api_input"
        )

        if groq_key:
            st.markdown('<div class="meta-status connected">✅ Groq configurado</div>', unsafe_allow_html=True)
            st.info("⚡ **Ultra rápido:** 14,400 tokens/minuto gratuitos")
        else:
            st.markdown('<div class="meta-status disconnected">⚠️ API key requerida</div>', unsafe_allow_html=True)

    elif ai_model == "OpenAI GPT-3.5":
        st.markdown("##### 🤖 OpenAI Configuration")
        openai_key = st.text_input(
            "API Key",
            value=env_vars.get("OPENAI_API_KEY", ""),
            type="password",
            placeholder="sk-...",
            help="Obtén tu key en platform.openai.com/api-keys",
            key="openai_api_input"
        )

        if openai_key:
            st.markdown('<div class="meta-status connected">✅ OpenAI configurado</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="meta-status disconnected">⚠️ API key requerida</div>', unsafe_allow_html=True)

    # Configuración de Unsplash
    st.markdown("#### 📸 Imágenes")
    unsplash_key = st.text_input(
        "🖼️ Unsplash Access Key",
        value=env_vars.get("UNSPLASH_ACCESS_KEY", ""),
        type="password",
        placeholder="Tu access key...",
        help="Obtén tu key gratuita en unsplash.com/developers",
        key="unsplash_api_input"
    )

    generate_images = st.checkbox(
        "🎨 **Generar imágenes automáticamente**",
        value=bool(unsplash_key),
        disabled=not bool(unsplash_key),
        help="Busca y adjunta imágenes profesionales automáticamente",
        key="generate_images_checkbox"
    )

    if unsplash_key:
        st.markdown('<div class="meta-status connected">✅ Unsplash activo</div>', unsafe_allow_html=True)
        st.info("📊 **Límites:** 50 descargas/hora gratuitas")
    else:
        st.markdown('<div class="meta-status disconnected">📸 Opcional - mejora el contenido</div>', unsafe_allow_html=True)

    # Configurar APIs en el generador
    st.session_state.content_generator.configure_apis(
        openai_key=openai_key if openai_key else None,
        groq_key=groq_key if groq_key else None,
        unsplash_key=unsplash_key if unsplash_key else None
    )

    # Estado del sistema estilo Meta
    st.markdown("### 📊 Estado del Sistema")

    status_indicators = {
        "Demo Inteligente": ("🎯", "Demo Activo", "connected"),
        "Groq Llama3 (Gratis)": ("🚀" if st.session_state.content_generator.groq_configured else "⏸️", 
                                 "Groq Ultra-Rápido" if st.session_state.content_generator.groq_configured else "Groq Desconectado",
                                 "connected" if st.session_state.content_generator.groq_configured else "disconnected"),
        "OpenAI GPT-3.5": ("🤖" if st.session_state.content_generator.api_configured else "⏸️",
                           "OpenAI Activo" if st.session_state.content_generator.api_configured else "OpenAI Desconectado",
                           "connected" if st.session_state.content_generator.api_configured else "disconnected"),
        "Ollama Local": ("🏠", "Ollama Local", "disconnected"),
        "LM Studio + ComfyUI": ("🎨" if st.session_state.get("has_content_visual_agent", False) else "⏸️",
                               "LM Studio + ComfyUI Activo" if st.session_state.get("has_content_visual_agent", False) else "LM Studio + ComfyUI Desconectado",
                               "connected" if st.session_state.get("has_content_visual_agent", False) else "disconnected")
    }

    if ai_model in status_indicators:
        icon, text, status = status_indicators[ai_model]
        st.markdown(f'<div class="meta-status {status}">{icon} {text}</div>', unsafe_allow_html=True)

    # Estado de imágenes
    img_status = "connected" if st.session_state.content_generator.unsplash_configured else "disconnected"
    img_icon = "🎨" if img_status == "connected" else "📷"
    img_text = "Imágenes Automáticas" if img_status == "connected" else "Solo Texto"
    st.markdown(f'<div class="meta-status {img_status}">{img_icon} {img_text}</div>', unsafe_allow_html=True)

    # Información de costos estilo Meta
    st.markdown("### 💰 Costos")

    cost_mapping = {
        "Demo Inteligente": ("🆓", "Completamente gratuito", "success"),
        "Groq Llama3 (Gratis)": ("🚀", "Gratuito + Ultra rápido", "success"),
        "OpenAI GPT-3.5": ("💳", "~$0.002 per 1K tokens", "info"),
        "Ollama Local": ("🏠", "Gratuito (local)", "info"),
        "LM Studio + ComfyUI": ("🎨", "Gratuito (local)", "info")
    }

    if ai_model in cost_mapping:
        icon, text, msg_type = cost_mapping[ai_model]
        if msg_type == "success":
            st.success(f"{icon} {text}")
        else:
            st.info(f"{icon} {text}")

    if st.session_state.content_generator.unsplash_configured:
        st.info("📸 Unsplash: 50 imágenes/hora gratuitas")

    # Generador Científico (RAG)
    st.markdown("### 🧬 Generador Científico")
    scientific_query = st.text_input(
        "🔬 Tema científico",
        placeholder="ej: física cuántica, IA, biomedicina",
        help="Genera contenido científico usando RAG y arXiv",
        key="scientific_query_input"
    )

    if st.button("🧬 Generar científico", key="generate_scientific", use_container_width=True):
        if scientific_query:
            with st.spinner("Generando contenido científico..."):
                scientific_result = st.session_state.content_generator.generate_scientific_content_multilang(
                    scientific_query, st.session_state.get("selected_language", "en")
                )
                st.session_state.scientific_content = scientific_result
        else:
            st.error("Por favor, ingresa un tema científico")

## frontend/main.py - PARTE 5 CORREGIDA: LAYOUT PRINCIPAL Y FUNCIONES

# Layout principal estilo Meta
col1, col2 = st.columns([2, 1], gap="large")

with col1:
    st.markdown('<div class="meta-card-line">', unsafe_allow_html=True)
    st.markdown("### 📝 Crear Contenido")

    with st.form("content_form", clear_on_submit=False, border=False):
        topic = st.text_input(
            "💡 **Tema Principal**",
            placeholder="ej: Inteligencia Artificial, Marketing Digital, Meta...",
            help="🎯 Describe el tema central de tu contenido",
            key="topic_input"
        )

        st.markdown("#### 📱 Plataforma")
        
        # Platform selection con estilo Meta - SIN KEY EN FORM_SUBMIT_BUTTON
        platforms = [
            {"name": "Twitter", "icon": "🐦", "desc": "Tweets concisos"},
            {"name": "Blog", "icon": "📝", "desc": "Artículos largos"},
            {"name": "Instagram", "icon": "📸", "desc": "Posts visuales"},
            {"name": "LinkedIn", "icon": "💼", "desc": "Contenido pro"}
        ]

        platform_cols = st.columns(2)
        platform_selected = None
        
        for i, platform_data in enumerate(platforms):
            col_idx = i % 2
            with platform_cols[col_idx]:
                # CORREGIDO: Removido el parámetro 'key' que causa error
                if st.form_submit_button(
                    f"{platform_data['icon']} **{platform_data['name']}**\n{platform_data['desc']}",
                    help=f"Optimizar para {platform_data['name']}",
                    use_container_width=True
                ):
                    st.session_state.selected_platform = platform_data['name']
                    platform_selected = platform_data['name']

        if st.session_state.selected_platform:
            selected_platform_data = next(p for p in platforms if p['name'] == st.session_state.selected_platform)
            st.success(f"✅ **{selected_platform_data['icon']} {selected_platform_data['name']}** seleccionado")

        # Configuraciones adicionales
        col_a, col_b, col_c = st.columns(3)

        with col_a:
            audience = st.text_input(
                "🎯 **Audiencia**",
                placeholder="emprendedores, developers...",
                help="👥 Define tu audiencia objetivo",
                key="audience_input"
            )

        with col_b:
            tone = st.selectbox(
                "🎭 **Tono**",
                ["profesional", "casual", "inspiracional", "técnico", "divertido", "educativo"],
                help="🗣️ Estilo de comunicación",
                key="tone_selector"
            )

        with col_c:
            creator_name = st.text_input(
                "✍️ **Creado por**",
                placeholder="Tu nombre...",
                help="👤 Firma del creador",
                key="creator_input"
            )

        # Botón principal de generación
        generate_button = st.form_submit_button(
            "⚡ **Generar Contenido**",
            type="primary",
            use_container_width=True
        )

        # Lógica de generación
        if generate_button:
            if not topic:
                st.error("⚠️ **Ingresa un tema**")
            elif not st.session_state.selected_platform:
                st.error("⚠️ **Selecciona una plataforma**")
            else:
                # Progreso estilo Meta
                progress_container = st.container()
                
                with progress_container:
                    st.markdown("### 🤖 Procesando...")
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    steps = [
                        ("🧠 **Analizando tema...**", 20),
                        ("🎯 **Optimizando plataforma...**", 40),
                        ("✍️ **Generando contenido...**", 60),
                        ("🖼️ **Buscando imagen...**" if generate_images else "🎨 **Aplicando estilo...**", 80),
                        ("✅ **¡Listo!**", 100)
                    ]

                    for step_text, progress in steps:
                        status_text.markdown(f'<div class="meta-card" style="padding: 1rem; margin: 0.5rem 0;">{step_text}</div>', unsafe_allow_html=True)
                        progress_bar.progress(progress)
                        time.sleep(0.5)

                    generator = st.session_state.content_generator
                    platform = st.session_state.selected_platform

                    # Generar según modelo seleccionado
                    if ai_model == "Groq Llama3 (Gratis)" and generator.groq_configured:
                        content, status = generator.generate_with_groq(topic, platform, audience, tone, creator_name)
                    elif ai_model == "OpenAI GPT-3.5" and generator.api_configured:
                        content, status = generator.generate_with_openai(topic, platform, audience, tone, creator_name)
                    elif ai_model == "Ollama Local":
                        content, status = generator.generate_with_ollama(topic, platform, audience, tone, creator_name)
                    elif ai_model == "LM Studio + ComfyUI" and st.session_state.get("has_content_visual_agent", False):
                        content, status = generator.generate_with_lmstudio_comfyui(topic, platform, audience, tone)
                    else:  # Demo Inteligente
                        content, status = generator.generate_demo_content(
                            topic, platform, audience, tone, creator_name, st.session_state.get("selected_language", "es")
                        )

                    # Buscar imagen si está habilitado
                    image_data = None
                    image_status = ""
                    
                    if generate_images and generator.unsplash_configured and content:
                        status_text.markdown('<div class="meta-card" style="padding: 1rem;">🧠 **Analizando para imagen...**</div>', unsafe_allow_html=True)
                        image_data, image_status = generator.search_unsplash_image_intelligent(
                            content=content, topic=topic, platform=platform
                        )

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
                            'timestamp': datetime.now(),
                            'word_count': len(str(content).split()),
                            'char_count': len(str(content)),
                            'hashtags': len([word for word in str(content).split() if word.startswith('#')])
                        }

                        st.session_state.generated_content = result_data
                        status_text.success("✅ **¡Contenido generado!**")
                        progress_bar.empty()
                        st.balloons()
                    else:
                        status_text.error(f"❌ **Error:** {status}")
                        progress_bar.empty()

    st.markdown('</div>', unsafe_allow_html=True)

# Panel lateral con tips estilo Meta
with col2:
    st.markdown('<div class="meta-card-line">', unsafe_allow_html=True)
    st.markdown("### 💡 Tips Style")

    platform_tips = {
        "Twitter": {
            "icon": "🐦",
            "tip": "Máximo 280 caracteres",
            "points": [
                "Usa hashtags trending",
                "Incluye pregunta para engagement", 
                "Emojis aumentan visibilidad",
                "Menciona usuarios relevantes"
            ]
        },
        "Blog": {
            "icon": "📝", 
            "tip": "Estructura clara y SEO optimized",
            "points": [
                "Subtítulos para mejor UX",
                "Listas y bullet points",
                "Call-to-action claro",
                "Keywords estratégicas"
            ]
        },
        "Instagram": {
            "icon": "📸",
            "tip": "Visual-first content",
            "points": [
                "Hasta 30 hashtags relevantes",
                "Stories y Reels prioritarios",
                "Ubicación para discovery",
                "Horarios de mayor actividad"
            ]
        },
        "LinkedIn": {
            "icon": "💼",
            "tip": "Valor profesional y networking",
            "points": [
                "Insights de la industria",
                "Tono profesional accesible",
                "Experiencias personales",
                "Preguntas para discusión"
            ]
        }
    }

    current_platform = st.session_state.selected_platform
    if current_platform in platform_tips:
        tip_data = platform_tips[current_platform]
        st.markdown(f"#### {tip_data['icon']} {current_platform}")
        st.info(f"**💡 {tip_data['tip']}**")
        
        st.markdown("**📋 Best practices:**")
        for point in tip_data['points']:
            st.markdown(f"• {point}")
    else:
        st.info("💡 Selecciona una plataforma para tips específicos")

    st.markdown("#### 📄 Templates Rápidos")
    quick_topics = [
        {"text": "Meta AI Updates", "emoji": "🤖"},
        {"text": "Productivity Hacks", "emoji": "⚡"},
        {"text": "Tech Innovation", "emoji": "🚀"},
        {"text": "Digital Strategy", "emoji": "📈"},
        {"text": "Meta Ads Tips", "emoji": "🎯"}
    ]

    for topic_data in quick_topics:
        # CORREGIDO: Cambiado button por checkbox para evitar conflictos
        if st.checkbox(
            f"{topic_data['emoji']} {topic_data['text']}",
            key=f"quick_{topic_data['text'].replace(' ', '_')}",
            help=f"Usar '{topic_data['text']}' como tema"
        ):
            st.info(f"💡 **{topic_data['text']}** seleccionado")

    st.markdown('</div>', unsafe_allow_html=True)

# Mostrar contenido generado estilo Meta
if st.session_state.generated_content:
    content_data = st.session_state.generated_content

    st.markdown("---")
    st.markdown("### 📊 Contenido Generado")

    # Métricas estilo Meta
    col1, col2, col3, col4, col5 = st.columns(5)

    metrics = [
        ("📱", content_data['platform'], "Plataforma"),
        ("🤖", content_data['model'].split()[0], "Motor IA"),
        ("📝", f"{content_data['char_count']:,}", "Caracteres"),
        ("📊", f"{content_data['word_count']:,}", "Palabras"),
        ("#️⃣", content_data.get('hashtags', 0), "Hashtags")
    ]

    for i, (icon, value, label) in enumerate(metrics):
        with [col1, col2, col3, col4, col5][i]:
            st.markdown(f"""
            <div class="meta-metric">
                <div style="font-size: 1.5rem; margin-bottom: 0.25rem;">{icon}</div>
                <div class="meta-metric-value">{value}</div>
                <div class="meta-metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    # Contenido principal
    st.markdown(f"""
    <div class="meta-card">
        <h4>🎯 Contenido para {content_data['platform']}</h4>
        <div class="meta-content-preview">
            {content_data['content'].replace(chr(10), '<br>')}
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1rem; color: var(--meta-gray-500); font-size: 0.875rem;">
            <span>✨ {content_data['status']}</span>
            <span>🕒 {content_data['timestamp'].strftime('%H:%M:%S')}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Mostrar imagen si existe
    if content_data.get('image_data'):
        st.markdown("#### 📸 Imagen Profesional")
        
        image_data = content_data['image_data']
        col_img1, col_img2 = st.columns([3, 2])

        with col_img1:
            st.image(
                image_data['url'],
                caption=f"📷 Foto por {image_data['author']} en Unsplash",
                use_container_width=True
            )

        with col_img2:
            st.markdown('<div class="meta-card">', unsafe_allow_html=True)
            st.markdown("**🎨 Detalles:**")
            st.markdown(f"**👤 Autor:** [{image_data['author']}]({image_data['author_url']})")
            
            if image_data['description']:
                st.markdown(f"**📝 Desc:** {image_data['description'][:80]}{'...' if len(image_data['description']) > 80 else ''}")
            
            st.markdown(f"**📐 Tamaño:** {image_data.get('width', 'N/A')} × {image_data.get('height', 'N/A')}")
            
            if st.button("📥 **Descargar**", use_container_width=True, key="download_img"):
                st.success("✅ **Lista para descargar**")
                st.info("💡 Clic derecho → 'Guardar imagen como...'")
            st.markdown('</div>', unsafe_allow_html=True)

    elif content_data.get('image_path') and os.path.exists(content_data['image_path']):
        st.markdown("#### 🎨 Imagen ComfyUI")
        
        col_img1, col_img2 = st.columns([3, 2])
        
        with col_img1:
            st.image(
                content_data['image_path'],
                caption="🖼️ Generada con IA",
                use_container_width=True
            )
        
        with col_img2:
            st.markdown('<div class="meta-card">', unsafe_allow_html=True)
            st.markdown("**🎨 Detalles:**")
            st.markdown("**🤖 Motor:** ComfyUI")
            if content_data.get('image_prompt'):
                st.markdown(f"**📝 Prompt:** {content_data['image_prompt'][:80]}{'...' if len(content_data.get('image_prompt', '')) > 80 else ''}")
            st.markdown(f"**📊 Estado:** {content_data.get('image_status', 'Generada con éxito')}")
            
            if st.button("📥 **Descargar**", use_container_width=True, key="download_comfy"):
                st.success("✅ **Lista para descargar**")
            st.markdown('</div>', unsafe_allow_html=True)

    # Botones de acción estilo Meta
    st.markdown("#### 🛠️ Acciones")
    
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📋 **Copiar**", use_container_width=True, key="copy_content"):
            st.success("✅ **Copiado!**")
            st.code(content_data['content'], language=None)

    with col2:
        if st.button("🔄 **Regenerar**", use_container_width=True, key="regenerate"):
            st.session_state.generated_content = None
            st.info("🔄 **Listo para nueva versión**")
            st.rerun()

    with col3:
        if st.button("📊 **Analizar**", use_container_width=True, key="analyze"):
            generator = st.session_state.content_generator
            if generator.unsplash_configured:
                try:
                    extracted_concepts = generator.extract_visual_concepts_from_content(
                        content_data['content'], content_data['topic']
                    )
                    st.success(f"🎯 **Conceptos:** {extracted_concepts}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            else:
                st.info("📊 **Análisis básico disponible**")

    with col4:
        # Exportar datos
        export_data = f"""# Contenido Meta Style - {content_data['platform']}

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
Generado con ContentAI Pro • Meta Style
"""

        st.download_button(
            label="📤 **Exportar**",
            data=export_data,
            file_name=f"meta_content_{content_data['platform'].lower()}_{content_data['timestamp'].strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True
        )

    # Detalles expandibles
    with st.expander("🔍 Ver Detalles del Proceso"):
        st.markdown(f"""
        **📝 Parámetros:**
        - **Tema:** {content_data['topic']}
        - **Audiencia:** {content_data['audience']}
        - **Tono:** {content_data['tone']}
        - **Creador:** {content_data.get('creator_name', 'No especificado')}
        - **Modelo:** {content_data['model']}
        - **Timestamp:** {content_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}

        **📸 Imagen:**
        - **Estado:** {content_data.get('image_status', 'Sin imagen')}
        - **Fuente:** {"Unsplash" if content_data.get('image_data') else "ComfyUI" if content_data.get('image_path') else "No aplicable"}
        """)

# Mostrar contenido científico
if st.session_state.get('scientific_content'):
    st.markdown("---")
    st.markdown("### 🧬 Contenido Científico (RAG)")
    st.markdown(f"""
    <div class='meta-card'>
        <h4>🔬 {scientific_query if 'scientific_query' in locals() else 'Contenido Científico'}</h4>
        <div class='meta-content-preview'>
            {st.session_state.scientific_content.replace(chr(10), '<br>')}
        </div>
        <small style="color: var(--meta-gray-500);">✨ Generado con RAG, LangChain y LangSmith</small>
    </div>
    """, unsafe_allow_html=True)

# Footer estilo Meta
st.markdown("---")
st.markdown("### 🚀 ContentAI Pro • Meta Professional")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    #### 🔮 Próximamente
    - 📅 **Auto-scheduling**
    - 🎨 **Editor integrado**
    - 📊 **Analytics avanzados**
    - 🔗 **API integrations**
    - 🧪 **A/B Testing**
    """)

with col2:
    st.markdown("""
    #### 🤖 Motores IA
    - 🚀 **Groq Llama3** (Ultra rápido)
    - 🤖 **OpenAI GPT** (Versátil)
    - 🏠 **Ollama** (Local/Privado)
    - 🎯 **Demo Smart** (Gratuito)
    - 🎨 **LM Studio + ComfyUI** (Visual)
    """)

with col3:
    st.markdown("""
    #### 📱 Plataformas
    - 🐦 **Twitter/X** (Posts optimizados)
    - 📸 **Instagram** (Visual content)
    - 💼 **LinkedIn** (Professional)
    - 📝 **Blog/Web** (Long-form)
    - 🔜 **TikTok, YouTube**
    """)

with col4:
    st.markdown("""
    #### 🎨 Características
    - 🖼️ **Auto-imágenes** (Unsplash)
    - 🧠 **Análisis semántico**
    - 📊 **Métricas real-time**
    - 💾 **Export avanzado**
    - 🧬 **RAG científico**
    """)

# Footer final
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: var(--meta-gray-500); padding: 2rem 0;">
    <p><strong>ContentAI Pro v3.0 Meta Style</strong> | Desarrollado con ❤️ y Streamlit</p>
    <p>⚡ <strong>Powered by:</strong> Multi-IA, RAG, Análisis Semántico, Generación Visual</p>
    <p>🌐 <strong>Multi-idioma:</strong> ES, EN, FR, DE, ZH, PT | 📧 <strong>Soporte 24/7</strong></p>
</div>
""", unsafe_allow_html=True)