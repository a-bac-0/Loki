## frontend/main.py - VERSIÓN CORREGIDA COMPLETA
import streamlit as st
import requests
import json
import time
import re
from datetime import datetime, timedelta

# Configuración de página
st.set_page_config(
    page_title="🧠 Generador de Contenido IA",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS mejorado estilo moderno
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .main .block-container {
        font-family: 'Inter', sans-serif;
        padding: 2rem;
    }
    
    .hero-section {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #d946ef 100%);
        padding: 3rem 2rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 2rem;
        color: white;
    }
    
    .hero-section h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        letter-spacing: -0.02em;
    }
    
    .hero-section p {
        font-size: 1.1rem;
        opacity: 0.9;
        margin: 0;
    }
    
    .content-card {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #e5e7eb;
        margin: 1rem 0;
    }
    
    .platform-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 2px solid transparent;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
        margin: 0.5rem;
    }
    
    .platform-card:hover {
        border-color: #6366f1;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
    }
    
    .platform-card.selected {
        border-color: #6366f1;
        background: linear-gradient(135deg, #6366f115, #8b5cf615);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4) !important;
    }
    
    .generated-content {
        background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
        padding: 2rem;
        border-radius: 12px;
        border-left: 4px solid #0ea5e9;
        margin: 2rem 0;
    }
    
    .api-status {
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .api-status.connected {
        background: #dcfce7;
        color: #166534;
        border: 1px solid #bbf7d0;
    }
    
    .api-status.disconnected {
        background: #fef2f2;
        color: #991b1b;
        border: 1px solid #fecaca;
    }
    
    .progress-step {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #6366f1;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ===============================
# AGENTES DE IA - VERSIÓN CORREGIDA
# ===============================

class ContentGenerator:
    """Generador de contenido con múltiples opciones de IA"""
    
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
        """
        Extrae conceptos visuales del contenido generado usando análisis semántico
        en lugar de diccionarios estáticos
        """
        if not content:
            return ["business", "professional"]
        
        # Combinar contenido y tema para análisis completo
        full_text = f"{topic} {content}".lower()
        
        # 1. Extraer palabras clave que tienen fuerte componente visual
        visual_keywords = self._extract_visual_keywords(full_text)
        
        # 2. Extraer entidades principales (sustantivos importantes)
        main_entities = self._extract_main_entities(full_text)
        
        # 3. Determinar contexto temático
        thematic_context = self._determine_thematic_context(full_text)
        
        # 4. Combinar y limpiar resultados
        all_concepts = visual_keywords + main_entities + thematic_context
        clean_concepts = self._clean_and_prioritize_concepts(all_concepts)
        
        # 5. Añadir respaldos inteligentes si es necesario
        if len(clean_concepts) < 2:
            smart_fallbacks = self._generate_contextual_fallbacks(content, topic)
            clean_concepts.extend(smart_fallbacks)
        
        return clean_concepts[:5]

    def _extract_visual_keywords(self, text):
        """Extrae palabras con fuerte componente visual del texto"""
        
        # Patrones que indican conceptos altamente visuales
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
        
        # Retornar las más relevantes sin duplicados
        return list(dict.fromkeys(visual_words))[:3]

    def _extract_main_entities(self, text):
        """Extrae las entidades/sustantivos principales del texto"""
        
        # Filtrar palabras comunes
        stop_words = {
            'the', 'and', 'for', 'with', 'you', 'your', 'this', 'that', 'will', 'can', 
            'are', 'is', 'have', 'has', 'more', 'most', 'make', 'get', 'como', 'para',
            'con', 'por', 'una', 'los', 'las', 'del', 'que', 'sus', 'muy', 'más'
        }
        
        # Extraer palabras candidatas (4+ letras)
        words = re.findall(r'\b[a-zA-ZáéíóúÁÉÍÓÚñÑ]{4,12}\b', text)
        
        # Filtrar y contar frecuencias
        word_freq = {}
        for word in words:
            word_lower = word.lower()
            if word_lower not in stop_words and word_lower.isalpha():
                word_freq[word_lower] = word_freq.get(word_lower, 0) + 1
        
        # Ordenar por frecuencia y tomar los más relevantes
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
        
        # Buscar indicadores en el texto
        for context, data in context_indicators.items():
            for keyword in data['keywords']:
                if keyword in text:
                    detected_concepts.extend(data['visual_concepts'][:2])
                    break  # Solo uno por contexto
        
        return detected_concepts[:3]

    def _clean_and_prioritize_concepts(self, concepts):
        """Limpia y prioriza los conceptos extraídos"""
        if not concepts:
            return []
        
        # Remover duplicados manteniendo orden
        clean_concepts = []
        seen = set()
        
        for concept in concepts:
            if not concept:
                continue
                
            # Limpiar concepto
            clean_concept = str(concept).strip().lower()
            
            # Filtrar conceptos válidos
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
        
        # Analizar características del contenido
        if len(content) > 200:  # Contenido largo
            fallbacks.extend(["article", "information", "reading"])
        
        if "#" in content or "@" in content:  # Social media
            fallbacks.extend(["social media", "communication", "smartphone"])
        
        if any(emoji in content for emoji in "🚀💡✨🎯"):  # Contenido con emojis
            fallbacks.extend(["modern", "vibrant", "innovative"])
        
        if "•" in content or "1." in content:  # Listas
            fallbacks.extend(["presentation", "infographic", "organization"])
        
        # Basado en el tema
        if topic:
            topic_words = [word.lower() for word in topic.split() if len(word) > 3]
            fallbacks.extend(topic_words[:2])
        
        # Fallbacks universales
        fallbacks.extend(["business", "professional", "success", "modern"])
        
        return fallbacks[:4]

    def _perform_unsplash_search(self, query, orientation="landscape"):
        """Realiza la búsqueda real en Unsplash con parámetros optimizados"""
        try:
            url = "https://api.unsplash.com/search/photos"
            headers = {"Authorization": f"Client-ID {self.unsplash_key}"}
            params = {
                "query": query,
                "per_page": 15,  # Más opciones para mejor selección
                "orientation": orientation,
                "content_filter": "high",
                "order_by": "relevant"
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=12)
            
            if response.status_code == 200:
                data = response.json()
                if data["results"]:
                    # Buscar la mejor imagen (alta resolución y relevante)
                    for image_data in data["results"]:
                        # Priorizar imágenes con buena resolución
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
                    
                    # Si no hay imágenes de alta resolución, tomar la primera disponible
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
            # Análisis inteligente del contenido para extraer conceptos visuales
            visual_concepts = self.extract_visual_concepts_from_content(content, topic)
            
            print(f"🧠 Conceptos extraídos automáticamente: {visual_concepts}")
            
            # Estrategias de búsqueda progresivas
            search_strategies = [
                # 1. Conceptos específicos del contenido
                visual_concepts[:2],
                
                # 2. Combinaciones de conceptos
                [f"{visual_concepts[0]} {visual_concepts[1]}"] if len(visual_concepts) >= 2 else [],
                
                # 3. Conceptos con contexto de plataforma
                [f"{visual_concepts[0]} {platform.lower()}"] if visual_concepts and platform else [],
                
                # 4. Tema original si es simple
                [topic] if topic and len(topic.split()) <= 2 else [],
                
                # 5. Conceptos universales de respaldo
                ["professional workspace", "business success", "modern technology"]
            ]
            
            # Probar cada estrategia
            for strategy_num, keywords_list in enumerate(search_strategies, 1):
                if not keywords_list:
                    continue
                    
                for keyword in keywords_list:
                    if not keyword or len(keyword.strip()) < 3:
                        continue
                        
                    print(f"🔍 Probando (Estrategia {strategy_num}): '{keyword}'")
                    
                    # Realizar búsqueda
                    image_result = self._perform_unsplash_search(keyword.strip(), orientation)
                    
                    if image_result[0]:  # Si encontró imagen
                        return image_result[0], f"✅ Encontrada con '{keyword}' (Análisis inteligente - Estrategia {strategy_num})"
                    else:
                        print(f"❌ Sin resultados para: '{keyword}'")
            
            # Si no encontró nada
            attempted_keywords = [kw for strategy in search_strategies for kw in strategy if kw][:5]
            return None, f"❌ Sin resultados tras análisis inteligente. Probados: {', '.join(attempted_keywords[:3])}..."
            
        except Exception as e:
            return None, f"Error en búsqueda inteligente: {str(e)}"
    
    def generate_with_groq(self, topic, platform, audience, tone="profesional"):
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
            7. Que invite a la interacción
            
            Responde SOLO con el contenido final, sin explicaciones adicionales.
            """
            
            data = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Crea contenido sobre: {topic}"}
                ],
                "model": "llama3-70b-8192",  # Modelo más potente de Groq
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
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama2",
                    "prompt": prompt,
                    "stream": False
                },
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
    
    def generate_demo_content(self, topic, platform, audience, tone="profesional"):
        """Generar contenido demo mejorado"""
        
        # Función auxiliar para limpiar hashtags
        def clean_hashtag(text):
            if not text:
                return "Content"
            # Remover espacios y caracteres especiales para hashtags
            return ''.join(word.capitalize() for word in str(text).replace(' ', '').replace(',', '').replace('.', '') if word.isalnum())[:20]
        
        platform_templates = {
            "twitter": {
                "template": "🔥 {topic} está revolucionando el mundo de {audience}!\n\n✨ Los beneficios que debes conocer:\n• Mayor productividad\n• Mejores resultados\n• Innovación constante\n\n¿Qué opinas? 👇\n\n#Innovation #{topic_hashtag} #Productivity",
                "emoji": "🐦"
            },
            "blog": {
                "template": "# Descubre cómo {topic} está transformando el mundo de {audience}\n\n¿Te has preguntado alguna vez cómo {topic} puede revolucionar tu enfoque? En este artículo exploraremos las tendencias más importantes y cómo puedes aprovecharlas.\n\n## Lo que necesitas saber\n\nEn los últimos años, hemos visto un crecimiento exponencial en {topic}, especialmente entre {audience}. Esta transformación no es solo una moda pasajera, sino un cambio fundamental que está redefiniendo...",
                "emoji": "📝"
            },
            "instagram": {
                "template": "✨ {topic} para {audience} ✨\n\n🎯 Tips que cambiarán tu juego:\n\n1️⃣ Empieza con fundamentos sólidos\n2️⃣ Mantén la consistencia\n3️⃣ Adapta según resultados\n4️⃣ Mide y optimiza\n\n💡 ¿Cuál implementarás primero?\n\n#{topic_hashtag} #Tips #Growth #Success #Motivation",
                "emoji": "📸"
            },
            "linkedin": {
                "template": "💼 Reflexiones sobre {topic} en el contexto profesional\n\nComo profesionales en el área de {audience}, es crucial mantenernos actualizados sobre las últimas tendencias en {topic}.\n\nMis principales observaciones:\n\n🔹 La importancia de la adaptación continua\n🔹 El valor de la innovación estratégica\n🔹 La necesidad de colaboración efectiva\n🔹 El impacto en la productividad\n\n¿Qué estrategias han funcionado mejor en tu experiencia?\n\n#{topic_hashtag} #ProfessionalDevelopment #Innovation #Leadership",
                "emoji": "💼"
            }
        }
        
        template_data = platform_templates.get(platform.lower(), platform_templates["twitter"])
        
        # Crear hashtag limpio
        topic_hashtag = clean_hashtag(topic)
        
        # Formatear el template con los valores
        try:
            content = template_data["template"].format(
                topic=topic, 
                audience=audience, 
                topic_hashtag=topic_hashtag
            )
        except KeyError as e:
            # Fallback si hay algún error en el formato
            content = f"🎯 Contenido sobre {topic} para {audience}\n\nEste es un contenido optimizado para {platform} con tono {tone}.\n\n#{topic_hashtag} #Content #Marketing"
        
        return content, f"Contenido demo para {platform} {template_data['emoji']}"

# ===============================
# INICIALIZAR SESSION STATE
# ===============================

if 'content_generator' not in st.session_state:
    st.session_state.content_generator = ContentGenerator()
if 'generated_content' not in st.session_state:
    st.session_state.generated_content = None
if 'selected_platform' not in st.session_state:
    st.session_state.selected_platform = "Twitter"

# ===============================
# INTERFAZ PRINCIPAL
# ===============================

# Hero Section
st.markdown("""
<div class="hero-section">
    <h1>🧠 Generador de Contenido IA</h1>
    <p>Crea contenido atractivo y optimizado para cualquier plataforma con inteligencia artificial</p>
</div>
""", unsafe_allow_html=True)

# Sidebar para configuración
with st.sidebar:
    st.markdown("### ⚙️ Configuración")
    
    # Selección de modelo IA
    ai_model = st.radio(
        "🤖 Modelo de IA",
        ["Demo Inteligente", "Groq Llama3 (Gratis)", "OpenAI GPT-3.5", "Ollama Local"],
        help="Selecciona qué modelo usar para generar contenido"
    )
    
    # Configuración de APIs
    st.markdown("#### 🔑 APIs")
    
    # Groq Configuration
    groq_key = None
    if ai_model == "Groq Llama3 (Gratis)":
        groq_key = st.text_input(
            "Groq API Key (Gratis)",
            type="password",
            help="Obtén tu key gratis en: https://console.groq.com"
        )
        
        if groq_key:
            st.success("✅ Groq configurado")
            st.info("⚡ Límite: 14,400 tokens/minuto gratis")
        else:
            st.warning("⚠️ Necesitas una API key para usar Groq")
        
        st.markdown("**🚀 Ventajas de Groq:**")
        st.markdown("• Ultra rápido (10x más que otros)")
        st.markdown("• 14,400 tokens/minuto gratis")
        st.markdown("• Modelo Llama3-70B potente")
        st.markdown("• Sin límites de uso diario")
    
    # OpenAI Configuration  
    openai_key = None
    if ai_model == "OpenAI GPT-3.5":
        openai_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Obtén tu key en: https://platform.openai.com/api-keys"
        )
        
        if not openai_key:
            st.warning("⚠️ Necesitas una API key para usar OpenAI")
    
    # Unsplash Configuration (siempre disponible)
    st.markdown("#### 📸 Imágenes con Unsplash")
    unsplash_key = st.text_input(
        "Unsplash Access Key (Opcional)",
        type="password",
        help="Obtén tu key gratis en: https://unsplash.com/developers"
    )
    
    generate_images = st.checkbox(
        "🖼️ Generar imágenes automáticamente",
        value=bool(unsplash_key),
        disabled=not bool(unsplash_key),
        help="Busca imágenes automáticamente para acompañar el contenido"
    )
    
    # Configurar APIs en el generador
    if openai_key or groq_key or unsplash_key:
        st.session_state.content_generator.configure_apis(
            openai_key=openai_key if openai_key else None,
            groq_key=groq_key if groq_key else None,
            unsplash_key=unsplash_key if unsplash_key else None
        )
    
    # Estado de conexiones
    st.markdown("### 📊 Estado")
    
    if ai_model == "Demo Inteligente":
        st.markdown('<div class="api-status connected">✅ Demo listo</div>', unsafe_allow_html=True)
    elif ai_model == "Groq Llama3 (Gratis)":
        status = "connected" if st.session_state.content_generator.groq_configured else "disconnected"
        icon = "✅" if status == "connected" else "❌"
        st.markdown(f'<div class="api-status {status}">{icon} Groq</div>', unsafe_allow_html=True)
    elif ai_model == "OpenAI GPT-3.5":
        status = "connected" if st.session_state.content_generator.api_configured else "disconnected"
        icon = "✅" if status == "connected" else "❌"
        st.markdown(f'<div class="api-status {status}">{icon} OpenAI</div>', unsafe_allow_html=True)
    elif ai_model == "Ollama Local":
        st.markdown('<div class="api-status disconnected">🔄 Verificar Ollama</div>', unsafe_allow_html=True)
    
    # Estado de Unsplash
    unsplash_status = "connected" if st.session_state.content_generator.unsplash_configured else "disconnected"
    unsplash_icon = "✅" if unsplash_status == "connected" else "❌"
    st.markdown(f'<div class="api-status {unsplash_status}">{unsplash_icon} Unsplash</div>', unsafe_allow_html=True)
    
    # Costos aproximados
    st.markdown("### 💰 Costos")
    if ai_model == "Demo Inteligente":
        st.info("🆓 Completamente gratuito")
    elif ai_model == "Groq Llama3 (Gratis)":
        st.success("🚀 Gratuito + Ultra rápido")
        st.info("14,400 tokens/minuto gratis")
    elif ai_model == "OpenAI GPT-3.5":
        st.info("💸 ~$0.002 por 1K tokens")
    elif ai_model == "Ollama Local":
        st.info("🆓 Gratuito (requiere instalación)")
    
    if st.session_state.content_generator.unsplash_configured:
        st.info("📸 Unsplash: 50 descargas/hora gratis")

# Layout principal
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📝 Crear Contenido")
    
    # Formulario principal
    with st.form("content_form"):
        # Input del tema
        topic = st.text_input(
            "💡 Tema",
            placeholder="Ej: Inteligencia Artificial, Marketing Digital, Productividad...",
            help="Describe el tema principal de tu contenido"
        )
        
        # Selección de plataforma con cards visuales
        st.markdown("#### 📱 Plataforma")
        
        platforms = [
            {"name": "Twitter", "icon": "🐦", "desc": "Tweets concisos y virales"},
            {"name": "Blog", "icon": "📝", "desc": "Artículos informativos"},
            {"name": "Instagram", "icon": "📸", "desc": "Posts visuales con hashtags"},
            {"name": "LinkedIn", "icon": "💼", "desc": "Contenido profesional"}
        ]
        
        platform_cols = st.columns(4)
        
        for i, platform_data in enumerate(platforms):
            with platform_cols[i]:
                if st.form_submit_button(
                    f"{platform_data['icon']}\n{platform_data['name']}\n{platform_data['desc']}",
                    help=f"Optimizar para {platform_data['name']}",
                    use_container_width=True
                ):
                    st.session_state.selected_platform = platform_data['name']
        
        # Mostrar plataforma seleccionada
        if st.session_state.selected_platform:
            selected_platform_data = next(p for p in platforms if p['name'] == st.session_state.selected_platform)
            st.success(f"✅ Plataforma seleccionada: **{selected_platform_data['icon']} {selected_platform_data['name']}**")
        
        # Inputs adicionales
        col_a, col_b = st.columns(2)
        
        with col_a:
            audience = st.text_input(
                "🎯 Audiencia",
                placeholder="Ej: adolescentes, marketers, emprendedores...",
                help="Define tu público objetivo"
            )
        
        with col_b:
            tone = st.selectbox(
                "🎭 Tono",
                ["profesional", "casual", "divertido", "inspiracional", "educativo"],
                help="Selecciona el tono del contenido"
            )
        
        # Botón de generación
        generate_button = st.form_submit_button(
            "🚀 Generar Contenido",
            type="primary"
        )
        
        # Lógica de generación
        if generate_button:
            if not topic:
                st.error("⚠️ Por favor, ingresa un tema")
            elif not st.session_state.selected_platform:
                st.error("⚠️ Por favor, selecciona una plataforma")
            else:
                # Mostrar progreso
                progress_container = st.container()
                
                with progress_container:
                    st.markdown("### 🤖 Generando contenido...")
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Pasos del proceso
                    steps = [
                        ("🧠 Analizando tema y audiencia...", 20),
                        ("✍️ Generando contenido optimizado...", 40),
                        ("🖼️ Buscando imagen perfecta..." if generate_images else "🎨 Aplicando estilo de la plataforma...", 60),
                        ("🎨 Finalizando optimización...", 80),
                        ("✅ Contenido listo!", 100)
                    ]
                    
                    for step_text, progress in steps:
                        status_text.markdown(f'<div class="progress-step">{step_text}</div>', unsafe_allow_html=True)
                        progress_bar.progress(progress)
                        time.sleep(0.8)
                    
                    # Generar contenido según el modelo seleccionado
                    generator = st.session_state.content_generator
                    platform = st.session_state.selected_platform
                    
                    if ai_model == "Groq Llama3 (Gratis)" and generator.groq_configured:
                        content, status = generator.generate_with_groq(topic, platform, audience, tone)
                    elif ai_model == "OpenAI GPT-3.5" and generator.api_configured:
                        content, status = generator.generate_with_openai(topic, platform, audience, tone)
                    elif ai_model == "Ollama Local":
                        content, status = generator.generate_with_ollama(topic, platform, audience, tone)
                    else:  # Demo Inteligente
                        content, status = generator.generate_demo_content(topic, platform, audience, tone)
                    
                    # Buscar imagen en Unsplash si está configurado - VERSIÓN CORREGIDA
                    image_data = None
                    image_status = ""
                    search_keyword_used = ""
                    
                    if generate_images and generator.unsplash_configured and content:
                        status_text.markdown('<div class="progress-step">🧠 Analizando contenido para encontrar imagen perfecta...</div>', unsafe_allow_html=True)
                        
                        # Usar la nueva búsqueda inteligente - LÍNEA CORREGIDA
                        image_data, image_status = generator.search_unsplash_image_intelligent(
                            content=content,  # Pasar el contenido real generado
                            topic=topic,
                            platform=platform
                        )
                        
                        if image_data:
                            search_keyword_used = "Análisis inteligente del contenido"
                            print(f"✅ Imagen encontrada con análisis inteligente")
                        else:
                            print(f"❌ Análisis inteligente no encontró resultados: {image_status}")
                    
                    if content:
                        # Guardar resultado
                        st.session_state.generated_content = {
                            'topic': topic,
                            'platform': platform,
                            'audience': audience,
                            'tone': tone,
                            'content': content,
                            'status': status,
                            'model': ai_model,
                            'image_data': image_data,
                            'image_status': image_status,
                            'search_keyword_used': search_keyword_used,
                            'timestamp': datetime.now()
                        }
                        
                        status_text.success("✅ ¡Contenido generado exitosamente!")
                        progress_bar.empty()
                        st.balloons()
                    else:
                        status_text.error(f"❌ Error: {status}")
                        progress_bar.empty()

with col2:
    st.markdown("### 💡 Sugerencias")
    
    # Tips dinámicos según la plataforma
    platform_tips = {
        "Twitter": "🐦 Mantén el mensaje conciso y usa hashtags trending",
        "Blog": "📝 Incluye títulos atractivos y estructura clara",
        "Instagram": "📸 Usa emojis llamativos y hashtags populares",
        "LinkedIn": "💼 Enfócate en valor profesional y networking"
    }
    
    current_tip = platform_tips.get(st.session_state.selected_platform, "💡 Selecciona una plataforma para ver tips específicos")
    st.info(current_tip)
    
    # Plantillas rápidas
    st.markdown("#### 📄 Plantillas Rápidas")
    
    quick_topics = [
        "🔥 Tendencias 2025",
        "💡 Tips de productividad",
        "🚀 Innovación tecnológica",
        "📈 Estrategias de crecimiento",
        "🎯 Marketing efectivo"
    ]
    
    for topic_template in quick_topics:
        if st.button(topic_template, use_container_width=True, key=f"template_{topic_template}"):
            st.session_state.quick_topic = topic_template

# Mostrar contenido generado
if st.session_state.generated_content:
    content_data = st.session_state.generated_content
    
    st.markdown("---")
    st.markdown("### 📊 Contenido Generado")
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Plataforma", content_data['platform'])
    with col2:
        st.metric("Modelo IA", content_data['model'].split()[0])
    with col3:
        st.metric("Caracteres", len(content_data['content']))
    with col4:
        st.metric("Palabras", len(content_data['content'].split()))
    
    # Contenido final
    st.markdown(f"""
    <div class="generated-content">
        <h4>🎯 Contenido para {content_data['platform']}</h4>
        <div style="background: white; padding: 1.5rem; border-radius: 8px; margin: 1rem 0;">
            {content_data['content'].replace(chr(10), '<br>')}
        </div>
        <small>✨ {content_data['status']}</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Mostrar imagen de Unsplash si existe
    if content_data.get('image_data'):
        st.markdown("#### 📸 Imagen de Unsplash")
        
        image_data = content_data['image_data']
        
        col_img1, col_img2 = st.columns([2, 1])
        
        with col_img1:
            st.image(
                image_data['url'], 
                caption=f"📷 Foto por {image_data['author']} en Unsplash",
                use_column_width=True
            )
        
        with col_img2:
            st.markdown("**Detalles de la imagen:**")
            st.write(f"**Autor:** [{image_data['author']}]({image_data['author_url']})")
            if image_data['description']:
                st.write(f"**Descripción:** {image_data['description'][:100]}...")
            st.write(f"**Estado:** {content_data.get('image_status', 'Imagen encontrada')}")
            
            # Botón para descargar imagen
            if st.button("📥 Descargar Imagen Original", use_container_width=True):
                st.info("💡 Haz clic derecho en la imagen y selecciona 'Guardar imagen como...'")
    
    elif content_data.get('image_status'):
        st.markdown("#### 📸 Estado de Imagen")
        if "No se encontraron" in content_data['image_status']:
            st.warning(f"⚠️ {content_data['image_status']}")
            st.info("💡 Intenta con un tema más específico o verifica tu API key de Unsplash")
        else:
            st.info(f"ℹ️ {content_data['image_status']}")
    
    # Botones de acción
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Copiar Contenido", use_container_width=True):
            # Simular copiado al portapapeles
            st.success("✅ Contenido copiado!")
            st.code(content_data['content'])
    
    with col2:
        if st.button("🔄 Regenerar", use_container_width=True):
            # Limpiar el contenido generado para forzar regeneración
            st.session_state.generated_content = None
            st.info("🔄 Haz clic en 'Generar Contenido' para crear una nueva versión")
    
    with col3:
        if st.button("📤 Compartir", use_container_width=True):
            st.info("📤 Función de compartir próximamente")
    
    # Mostrar detalles del proceso con análisis inteligente
    with st.expander("🔍 Ver Detalles del Proceso"):
        st.markdown(f"""
        **📝 Parámetros utilizados:**
        - **Tema:** {content_data['topic']}
        - **Audiencia:** {content_data['audience']}
        - **Tono:** {content_data['tone']}
        - **Modelo:** {content_data['model']}
        - **Timestamp:** {content_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
        
        **📸 Información de imagen:**
        - **Estado:** {content_data.get('image_status', 'Sin imagen')}
        - **Método:** {content_data.get('search_keyword_used', 'N/A')}
        - **Fuente:** {"Unsplash" if content_data.get('image_data') else "No aplicable"}
        """)
        
        # Mostrar análisis inteligente de keywords
        if st.button("🧠 Ver Análisis de Keywords", key="show_analysis"):
            generator = st.session_state.content_generator
            if generator.unsplash_configured:
                try:
                    extracted_concepts = generator.extract_visual_concepts_from_content(
                        content_data['content'], 
                        content_data['topic']
                    )
                    st.success(f"🎯 **Conceptos extraídos automáticamente:** {extracted_concepts}")
                    st.info("💡 Estos conceptos se generan analizando el contenido real, no usando diccionarios estáticos")
                except Exception as e:
                    st.error(f"Error en análisis: {str(e)}")
            else:
                st.warning("⚠️ Configura Unsplash para ver el análisis inteligente")
        
        if content_data.get('image_data'):
            image_data = content_data['image_data']
            st.markdown(f"""
            **🖼️ Detalles de imagen Unsplash:**
            - **Autor:** {image_data['author']}
            - **Descripción:** {image_data.get('description', 'Sin descripción')}
            - **Resolución:** {image_data.get('width', 'N/A')} x {image_data.get('height', 'N/A')}
            - **URL:** [Ver en Unsplash]({image_data['author_url']})
            """)

# Footer con información mejorada
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 🚀 Próximas Funciones
    - Programación automática
    - Múltiples variaciones
    - Análisis de engagement
    - Editor de imágenes
    """)

with col2:
    st.markdown("""
    ### 🔧 APIs Soportadas
    - Groq Llama3 (Ultra rápido)
    - OpenAI GPT-3.5/4
    - Ollama (Local)
    - Unsplash (Imágenes)
    - Anthropic Claude
    """)

with col3:
    st.markdown("""
    ### 📊 Plataformas
    - Twitter/X
    - Instagram
    - LinkedIn
    - Blog/Website
    """)