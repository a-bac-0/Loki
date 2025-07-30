##loki-claves

## frontend/main.py
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta

import requests
import streamlit as st
import dotenv
from deep_translator import DeeplTranslator

# Load environment variables at startup
dotenv.load_dotenv()

# Debug: Print if .env file exists
env_file_path = os.path.join(os.getcwd(), '.env')
if os.path.exists(env_file_path):
    print(f"✅ .env file found at: {env_file_path}")
else:
    print(f"❌ .env file not found at: {env_file_path}")
    # Try alternative locations
    alt_paths = ['./.env', '../.env', '../../.env']
    for alt_path in alt_paths:
        if os.path.exists(alt_path):
            print(f"✅ Found .env at alternative location: {alt_path}")
            dotenv.load_dotenv(alt_path)
            break

# Configure Streamlit page
st.set_page_config(
    page_title="🧠 Generador de Contenido IA",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Styles
st.markdown("""
<style>
.hero-section {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
}

.generated-content {
    background: #f8f9fa;
    border-left: 4px solid #667eea;
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
}

.progress-step {
    color: #667eea;
    font-weight: bold;
    margin: 0.5rem 0;
}

.api-status {
    padding: 0.5rem;
    border-radius: 5px;
    margin: 0.2rem 0;
}

.api-configured {
    background-color: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

.api-not-configured {
    background-color: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}
</style>
""", unsafe_allow_html=True)

# ContentGenerator class with all methods
class ContentGenerator:
    def __init__(self):
        self.openai_key = None
        self.groq_key = None
        self.unsplash_key = None
        self.deepl_key = None  # Add DeepL key
        self.api_configured = False
        self.groq_configured = False
        self.unsplash_configured = False
        self.deepl_configured = False  # Add DeepL status

    def configure_apis(self, openai_key=None, groq_key=None, unsplash_key=None, deepl_key=None):
        """Configure API keys and set status flags"""
        self.openai_key = openai_key
        self.groq_key = groq_key
        self.unsplash_key = unsplash_key
        self.deepl_key = deepl_key
        
        self.api_configured = bool(openai_key)
        self.groq_configured = bool(groq_key)
        self.unsplash_configured = bool(unsplash_key)
        self.deepl_configured = bool(deepl_key)

    def translate_content(self, content, target_language):
        """Translate content using DeepL API"""
        if not self.deepl_configured or target_language == 'en':
            return content, "No translation needed"
            
        try:
            # DeepL language codes mapping (expanded)
            deepl_codes = {
                'es': 'ES',
                'fr': 'FR', 
                'de': 'DE',
                'it': 'IT',
                'pt': 'PT-PT',  # Portuguese (Portugal) - also supports PT-BR
                'zh': 'ZH',
                'ja': 'JA',
                'ko': 'KO',
                'ru': 'RU',
                'nl': 'NL',
                'pl': 'PL',
                'sv': 'SV',
                'da': 'DA',
                'fi': 'FI',
                'no': 'NB',  # Norwegian Bokmål
                'cs': 'CS',  # Czech
                'sk': 'SK',  # Slovak
                'sl': 'SL',  # Slovenian
                'et': 'ET',  # Estonian
                'lv': 'LV',  # Latvian
                'lt': 'LT',  # Lithuanian
                'hu': 'HU',  # Hungarian
                'ro': 'RO',  # Romanian
                'bg': 'BG',  # Bulgarian
                'el': 'EL',  # Greek
                'tr': 'TR',  # Turkish
                'ar': 'AR',  # Arabic
                'hi': 'HI',  # Hindi
                'id': 'ID',  # Indonesian
                'uk': 'UK',  # Ukrainian
            }
            
            target_code = deepl_codes.get(target_language)
            if not target_code:
                return content, f"Language {target_language} not supported by DeepL"
            
            # Use deep_translator which is more robust
            translator = DeeplTranslator(api_key=self.deepl_key, source="auto", target=target_code)
            translated = translator.translate(content)
            
            if translated and translated != content:
                return translated, f"Translated to {target_language} with DeepL"
            else:
                return content, f"Translation to {target_language} returned same content"
            
        except Exception as e:
            # Return original content with error message but don't fail completely
            error_msg = str(e)
            if "quota" in error_msg.lower() or "limit" in error_msg.lower():
                return content, f"DeepL quota exceeded - showing original content"
            elif "key" in error_msg.lower() or "auth" in error_msg.lower():
                return content, f"DeepL authentication error - showing original content"
            else:
                return content, f"Translation error: {error_msg} - showing original content"

    def _clean_and_prioritize_concepts(self, concepts):
        """Clean and prioritize extracted concepts"""
        if not concepts:
            return []

        clean_concepts = []
        seen = set()

        for concept in concepts:
            if not concept:
                continue

            clean_concept = str(concept).strip().lower()

            if (
                len(clean_concept) >= 3
                and len(clean_concept) <= 20
                and clean_concept not in seen
                and clean_concept.replace(" ", "").isalpha()
            ):
                clean_concepts.append(clean_concept)
                seen.add(clean_concept)

        return clean_concepts

    def extract_visual_concepts_from_content(self, content, topic=""):
        """Extract visual concepts from content for image search"""
        if not content:
            return ["business", "professional", "modern"]

        # Simple keyword extraction
        import re
        
        # Remove common words and extract meaningful terms
        stop_words = {
            'es': ['el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'al', 'una', 'su', 'del', 'las', 'los'],
            'en': ['the', 'is', 'at', 'which', 'on', 'and', 'a', 'to', 'are', 'as', 'was', 'with', 'for', 'his', 'he', 'be', 'not', 'by', 'but', 'have', 'you', 'that', 'this']
        }
        
        # Extract words from content
        words = re.findall(r'\b[a-zA-ZáéíóúÁÉÍÓÚñÑ]{4,}\b', content.lower())
        
        # Filter out stop words
        filtered_words = []
        for word in words:
            is_stop_word = False
            for lang_stops in stop_words.values():
                if word in lang_stops:
                    is_stop_word = True
                    break
            if not is_stop_word:
                filtered_words.append(word)
        
        # Get most frequent words
        from collections import Counter
        word_counts = Counter(filtered_words)
        concepts = [word for word, count in word_counts.most_common(5)]
        
        # Add topic words if provided
        if topic:
            topic_words = re.findall(r'\b[a-zA-ZáéíóúÁÉÍÓÚñÑ]{4,}\b', topic.lower())
            concepts.extend(topic_words)
        
        # Clean and return
        return self._clean_and_prioritize_concepts(concepts)

    def _perform_unsplash_search(self, query, orientation="landscape"):
        """Perform actual Unsplash search with optimized parameters"""
        try:
            url = "https://api.unsplash.com/search/photos"
            headers = {"Authorization": f"Client-ID {self.unsplash_key}"}
            params = {
                "query": query,
                "per_page": 15,
                "orientation": orientation,
                "content_filter": "high",
                "order_by": "relevant",
            }

            response = requests.get(url, headers=headers, params=params, timeout=12)

            if response.status_code == 200:
                data = response.json()
                if data["results"]:
                    # Look for high quality image
                    for image_data in data["results"]:
                        if (
                            image_data.get("width", 0) >= 800
                            and image_data.get("height", 0) >= 600
                        ):
                            return {
                                "url": image_data["urls"]["regular"],
                                "thumb": image_data["urls"]["thumb"],
                                "description": image_data.get("description", "") or image_data.get("alt_description", ""),
                                "author": image_data["user"]["name"],
                                "author_url": image_data["user"]["links"]["html"],
                                "download_url": image_data["links"]["download_location"],
                                "width": image_data.get("width", 0),
                                "height": image_data.get("height", 0),
                            }, "High quality image found"

                    # If no high res images, take first available
                    image_data = data["results"][0]
                    return {
                        "url": image_data["urls"]["regular"],
                        "thumb": image_data["urls"]["thumb"],
                        "description": image_data.get("description", "") or image_data.get("alt_description", ""),
                        "author": image_data["user"]["name"],
                        "author_url": image_data["user"]["links"]["html"],
                        "download_url": image_data["links"]["download_location"],
                        "width": image_data.get("width", 0),
                        "height": image_data.get("height", 0),
                    }, "Image found"
                else:
                    return None, f"No results for '{query}'"

            elif response.status_code == 403:
                return None, "Invalid API key or no permissions"
            elif response.status_code == 429:
                return None, "Rate limit reached"
            else:
                return None, f"HTTP Error {response.status_code}"

        except requests.exceptions.Timeout:
            return None, "Search timeout"
        except Exception as e:
            return None, f"Error: {str(e)}"

    def search_unsplash_image_intelligent(self, content, topic="", platform="", orientation="landscape"):
        """Intelligent image search based on real content analysis"""
        if not self.unsplash_key:
            return None, "Unsplash API key not configured"

        try:
            # Intelligent content analysis for visual concepts
            visual_concepts = self.extract_visual_concepts_from_content(content, topic)
            
            # Progressive search strategies
            search_strategies = [
                # 1. Specific content concepts
                visual_concepts[:2],
                # 2. Concept combinations
                ([f"{visual_concepts[0]} {visual_concepts[1]}"] if len(visual_concepts) >= 2 else []),
                # 3. Concepts with platform context
                ([f"{visual_concepts[0]} {platform.lower()}"] if visual_concepts and platform else []),
                # 4. Original topic if simple
                ([topic] if topic and len(topic.split()) <= 2 else []),
                # 5. Universal fallback concepts
                ["professional workspace", "business success", "modern technology"],
            ]

            # Try each strategy
            for strategy_num, keywords_list in enumerate(search_strategies, 1):
                if not keywords_list:
                    continue

                for keyword in keywords_list:
                    if not keyword or len(keyword.strip()) < 3:
                        continue

                    # Perform search
                    image_result = self._perform_unsplash_search(keyword.strip(), orientation)

                    if image_result[0]:  # If image found
                        return (
                            image_result[0],
                            f"✅ Found with '{keyword}' (Intelligent analysis - Strategy {strategy_num})",
                        )

            # If nothing found
            attempted_keywords = [kw for strategy in search_strategies for kw in strategy if kw][:5]
            return (
                None,
                f"❌ No results after intelligent analysis. Tried: {', '.join(attempted_keywords[:3])}...",
            )

        except Exception as e:
            return None, f"Error in intelligent search: {str(e)}"

    def generate_with_groq(self, topic, platform, audience, tone="profesional", language="es"):
        """Generate real content with Groq (Ultra fast and free)"""
        if not self.groq_key:
            return None, "Groq API key not configured"

        try:
            platform_instructions = {
                "twitter": "Create an attractive and concise tweet (max 280 characters)",
                "blog": "Create an engaging introduction for a blog article", 
                "instagram": "Create a visual post for Instagram with emojis and hashtags",
                "linkedin": "Create a professional post for LinkedIn",
            }

            headers = {
                "Authorization": f"Bearer {self.groq_key}",
                "Content-Type": "application/json",
            }

            # Language specific instructions
            language_instructions = {
                'es': 'Responde en español',
                'en': 'Respond in English', 
                'fr': 'Répondez en français',
                'de': 'Antworten Sie auf Deutsch',
                'it': 'Rispondi in italiano',
                'pt': 'Responda em português',
                'zh': '请用中文回答'
            }
            
            lang_instruction = language_instructions.get(language, 'Respond in English')
            
            # Generate directly in target language or English as fallback
            system_prompt = f"""
            You are an expert in content marketing and social media.
            
            Task: {platform_instructions.get(platform.lower(), 'Create social media content')}
            Platform: {platform}
            Audience: {audience}
            Tone: {tone}
            Language: {language}
            
            Instructions:
            1. Create 100% original and attractive content
            2. Use a {tone} tone
            3. Optimize specifically for {platform}
            4. Include relevant emojis
            5. Add appropriate hashtags at the end
            6. Make it engaging for {audience}
            7. Encourage interaction
            8. {lang_instruction}
            
            Respond ONLY with the final content, no additional explanations.
            """

            data = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Create content about: {topic}"},
                ],
                "model": "llama3-70b-8192",
                "temperature": 0.7,
                "max_tokens": 500,
                "top_p": 0.9,
                "stream": False,
            }

            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"].strip()
                
                # Fallback translation if content appears to be in English and target is not English
                if language != 'en' and self.deepl_configured:
                    # Simple check if content contains English words (basic heuristic)
                    english_indicators = ['the', 'and', 'for', 'with', 'this', 'that', 'your', 'you', 'are', 'is']
                    content_lower = content.lower()
                    english_word_count = sum(1 for word in english_indicators if word in content_lower)
                    
                    # If content seems to be in English, translate it
                    if english_word_count >= 2:
                        translated_content, translation_status = self.translate_content(content, language)
                        return translated_content, f"Generated with Groq + {translation_status}"
                
                return content, f"Content generated with Groq Llama3-70B in {language.upper()}"
            elif response.status_code == 401:
                return None, "Invalid Groq API key"
            elif response.status_code == 429:
                return None, "Rate limit reached. Wait a moment."
            else:
                return None, f"Groq API error: {response.status_code}"

        except requests.exceptions.Timeout:
            return None, "Timeout connecting to Groq"
        except Exception as e:
            return None, f"Groq error: {str(e)}"

    def generate_with_openai(self, topic, platform, audience, tone="profesional", language="es"):
        """Generate real content with OpenAI"""
        if not self.openai_key:
            return None, "OpenAI API key not configured"

        try:
            headers = {
                "Authorization": f"Bearer {self.openai_key}",
                "Content-Type": "application/json",
            }

            platform_prompts = {
                "twitter": "Create an attractive and concise tweet (max 280 characters)",
                "blog": "Create an engaging introduction for a blog article",
                "instagram": "Create a visual post for Instagram with emojis and hashtags",
                "linkedin": "Create a professional post for LinkedIn",
            }

            # Language specific instructions
            language_instructions = {
                'es': 'Responde en español',
                'en': 'Respond in English', 
                'fr': 'Répondez en français',
                'de': 'Antworten Sie auf Deutsch',
                'it': 'Rispondi in italiano',
                'pt': 'Responda em português',
                'zh': '请用中文回答'
            }
            
            lang_instruction = language_instructions.get(language, 'Respond in English')

            # Generate directly in target language
            system_prompt = f"""
            You are an expert in content marketing.
            
            Task: {platform_prompts.get(platform.lower(), 'Create social media content')}
            Platform: {platform}
            Audience: {audience}
            Tone: {tone}
            Language: {language}
            
            Instructions:
            1. Create original and attractive content
            2. Optimize for {platform}
            3. Use a {tone} tone
            4. Include relevant emojis
            5. Add appropriate hashtags
            6. Make it engaging for {audience}
            7. {lang_instruction}
            """

            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Create content about: {topic}"},
                ],
                "max_tokens": 400,
                "temperature": 0.7,
            }

            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"].strip()
                
                # Fallback translation if content appears to be in English and target is not English
                if language != 'en' and self.deepl_configured:
                    # Simple check if content contains English words (basic heuristic)
                    english_indicators = ['the', 'and', 'for', 'with', 'this', 'that', 'your', 'you', 'are', 'is']
                    content_lower = content.lower()
                    english_word_count = sum(1 for word in english_indicators if word in content_lower)
                    
                    # If content seems to be in English, translate it
                    if english_word_count >= 2:
                        translated_content, translation_status = self.translate_content(content, language)
                        return translated_content, f"Generated with OpenAI + {translation_status}"
                
                return content, f"Content generated with OpenAI GPT-3.5 in {language.upper()}"
            else:
                return None, f"OpenAI API error: {response.status_code}"

        except Exception as e:
            return None, f"OpenAI error: {str(e)}"

    def generate_with_ollama(self, topic, platform, audience, tone="profesional", language="es"):
        """Generate content with local Ollama"""
        try:
            # Language-specific prompt instructions
            language_prompts = {
                'es': f"Crea contenido en español para {platform} sobre: {topic}",
                'en': f"Create English content for {platform} about: {topic}",
                'fr': f"Créez du contenu en français pour {platform} à propos de: {topic}",
                'de': f"Erstellen Sie deutschen Inhalt für {platform} über: {topic}",
                'it': f"Crea contenuto in italiano per {platform} su: {topic}",
                'pt': f"Crie conteúdo em português para {platform} sobre: {topic}",
                'zh': f"为{platform}创建关于{topic}的中文内容"
            }
            
            base_prompt = language_prompts.get(language, f"Create content for {platform} about: {topic}")
            
            prompt = f"""
            {base_prompt}
            Audience: {audience}
            Tone: {tone}
            Language: {language}
            
            Requirements:
            - Original and attractive content
            - Optimized for {platform}
            - Include relevant emojis
            - Add appropriate hashtags
            - Generate engagement
            - Write in {language} language
            
            Respond only with the content, no explanations.
            """

            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "llama2", "prompt": prompt, "stream": False},
                timeout=30,
            )

            if response.status_code == 200:
                content = response.json()["response"]
                return content.strip(), f"Content generated with Ollama Llama2 in {language.upper()}"
            else:
                return None, "Error connecting to Ollama"

        except requests.exceptions.ConnectionError:
            return None, "Ollama is not running. Install and run: ollama run llama2"
        except Exception as e:
            return None, f"Ollama error: {str(e)}"

    def generate_demo_content(self, topic, platform, audience, tone="profesional", language="es"):
        """Generate enhanced demo content with multi-language support"""
        
        def clean_hashtag(text):
            if not text:
                return "Content"
            return "".join(
                word.capitalize()
                for word in str(text).replace(" ", "").replace(",", "").replace(".", "")
                if word.isalnum()
            )[:20]

        topic_hashtag = clean_hashtag(topic)
        
        # Demo templates by platform and language
        templates = {
            "es": {
                "twitter": f"🚀 Descubre todo sobre {topic}! Perfecto para {audience} que buscan innovar. ¿Qué opinas? 💭 #{topic_hashtag} #Innovation #Marketing",
                "blog": f"# Todo lo que necesitas saber sobre {topic}\n\n¿Te has preguntado cómo {topic} puede transformar tu estrategia? En este artículo exploramos las mejores prácticas para {audience}.\n\n✨ Descubre técnicas probadas\n🎯 Estrategias efectivas\n📈 Resultados medibles\n\n#{topic_hashtag} #Blog #Estrategia",
                "instagram": f"✨ {topic} está revolucionando la forma en que {audience} trabajan! 🚀\n\n💡 Tips clave:\n• Innovación constante\n• Resultados medibles\n• Estrategia clara\n\n¿Cuál es tu experiencia? ¡Compártela en comentarios! 👇\n\n#{topic_hashtag} #Instagram #Innovation #Success #Marketing #Business",
                "linkedin": f"La importancia de {topic} en el desarrollo profesional de {audience}\n\nEn el panorama actual, dominar {topic} se ha vuelto fundamental para el crecimiento profesional. Las organizaciones líderes están adoptando estas estrategias para:\n\n✅ Mejorar la eficiencia\n✅ Impulsar la innovación\n✅ Generar resultados sostenibles\n\n¿Cómo está implementando tu organización estas prácticas?\n\n#{topic_hashtag} #LinkedIn #Professional #Business #Innovation"
            },
            "en": {
                "twitter": f"🚀 Discover everything about {topic}! Perfect for {audience} looking to innovate. What do you think? 💭 #{topic_hashtag} #Innovation #Marketing",
                "blog": f"# Everything you need to know about {topic}\n\nHave you wondered how {topic} can transform your strategy? In this article we explore best practices for {audience}.\n\n✨ Discover proven techniques\n🎯 Effective strategies\n📈 Measurable results\n\n#{topic_hashtag} #Blog #Strategy",
                "instagram": f"✨ {topic} is revolutionizing how {audience} work! 🚀\n\n💡 Key tips:\n• Constant innovation\n• Measurable results\n• Clear strategy\n\nWhat's your experience? Share in comments! 👇\n\n#{topic_hashtag} #Instagram #Innovation #Success #Marketing #Business",
                "linkedin": f"The importance of {topic} in professional development for {audience}\n\nIn today's landscape, mastering {topic} has become fundamental for professional growth. Leading organizations are adopting these strategies to:\n\n✅ Improve efficiency\n✅ Drive innovation\n✅ Generate sustainable results\n\nHow is your organization implementing these practices?\n\n#{topic_hashtag} #LinkedIn #Professional #Business #Innovation"
            },
            "fr": {
                "twitter": f"🚀 Découvrez tout sur {topic}! Parfait pour {audience} qui cherchent à innover. Qu'en pensez-vous? 💭 #{topic_hashtag} #Innovation #Marketing",
                "blog": f"# Tout ce que vous devez savoir sur {topic}\n\nVous êtes-vous déjà demandé comment {topic} peut transformer votre stratégie? Dans cet article, nous explorons les meilleures pratiques pour {audience}.\n\n✨ Découvrez des techniques éprouvées\n🎯 Stratégies efficaces\n📈 Résultats mesurables\n\n#{topic_hashtag} #Blog #Stratégie",
                "instagram": f"✨ {topic} révolutionne la façon dont {audience} travaillent! 🚀\n\n💡 Conseils clés:\n• Innovation constante\n• Résultats mesurables\n• Stratégie claire\n\nQuelle est votre expérience? Partagez en commentaires! 👇\n\n#{topic_hashtag} #Instagram #Innovation #Success #Marketing #Business",
                "linkedin": f"L'importance de {topic} dans le développement professionnel pour {audience}\n\nDans le paysage actuel, maîtriser {topic} est devenu fondamental pour la croissance professionnelle. Les organisations leaders adoptent ces stratégies pour:\n\n✅ Améliorer l'efficacité\n✅ Stimuler l'innovation\n✅ Générer des résultats durables\n\nComment votre organisation met-elle en œuvre ces pratiques?\n\n#{topic_hashtag} #LinkedIn #Professional #Business #Innovation"
            },
            "de": {
                "twitter": f"🚀 Entdecken Sie alles über {topic}! Perfekt für {audience}, die innovieren möchten. Was denken Sie? 💭 #{topic_hashtag} #Innovation #Marketing",
                "blog": f"# Alles was Sie über {topic} wissen müssen\n\nHaben Sie sich jemals gefragt, wie {topic} Ihre Strategie transformieren kann? In diesem Artikel erkunden wir bewährte Praktiken für {audience}.\n\n✨ Entdecken Sie bewährte Techniken\n🎯 Effektive Strategien\n📈 Messbare Ergebnisse\n\n#{topic_hashtag} #Blog #Strategie",
                "instagram": f"✨ {topic} revolutioniert die Art, wie {audience} arbeiten! 🚀\n\n💡 Wichtige Tipps:\n• Konstante Innovation\n• Messbare Ergebnisse\n• Klare Strategie\n\nWas ist Ihre Erfahrung? Teilen Sie in den Kommentaren! 👇\n\n#{topic_hashtag} #Instagram #Innovation #Success #Marketing #Business",
                "linkedin": f"Die Bedeutung von {topic} in der beruflichen Entwicklung für {audience}\n\nIn der heutigen Landschaft ist die Beherrschung von {topic} für das berufliche Wachstum von grundlegender Bedeutung geworden. Führende Organisationen setzen diese Strategien ein, um:\n\n✅ Effizienz zu verbessern\n✅ Innovation voranzutreiben\n✅ Nachhaltige Ergebnisse zu erzielen\n\nWie setzt Ihre Organisation diese Praktiken um?\n\n#{topic_hashtag} #LinkedIn #Professional #Business #Innovation"
            },
            "it": {
                "twitter": f"🚀 Scopri tutto su {topic}! Perfetto per {audience} che vogliono innovare. Cosa ne pensi? 💭 #{topic_hashtag} #Innovation #Marketing",
                "blog": f"# Tutto quello che devi sapere su {topic}\n\nTi sei mai chiesto come {topic} può trasformare la tua strategia? In questo articolo esploriamo le migliori pratiche per {audience}.\n\n✨ Scopri tecniche collaudate\n🎯 Strategie efficaci\n📈 Risultati misurabili\n\n#{topic_hashtag} #Blog #Strategia",
                "instagram": f"✨ {topic} sta rivoluzionando il modo in cui {audience} lavorano! 🚀\n\n💡 Suggerimenti chiave:\n• Innovazione costante\n• Risultati misurabili\n• Strategia chiara\n\nQual è la tua esperienza? Condividi nei commenti! 👇\n\n#{topic_hashtag} #Instagram #Innovation #Success #Marketing #Business",
                "linkedin": f"L'importanza di {topic} nello sviluppo professionale per {audience}\n\nNel panorama attuale, padroneggiare {topic} è diventato fondamentale per la crescita professionale. Le organizzazioni leader stanno adottando queste strategie per:\n\n✅ Migliorare l'efficienza\n✅ Guidare l'innovazione\n✅ Generare risultati sostenibili\n\nCome sta implementando queste pratiche la tua organizzazione?\n\n#{topic_hashtag} #LinkedIn #Professional #Business #Innovation"
            },
            "pt": {
                "twitter": f"🚀 Descubra tudo sobre {topic}! Perfeito para {audience} que procuram inovar. O que você acha? 💭 #{topic_hashtag} #Innovation #Marketing",
                "blog": f"# Tudo o que você precisa saber sobre {topic}\n\nJá se perguntou como {topic} pode transformar sua estratégia? Neste artigo exploramos as melhores práticas para {audience}.\n\n✨ Descubra técnicas comprovadas\n🎯 Estratégias eficazes\n📈 Resultados mensuráveis\n\n#{topic_hashtag} #Blog #Estratégia",
                "instagram": f"✨ {topic} está revolucionando a forma como {audience} trabalham! 🚀\n\n💡 Dicas importantes:\n• Inovação constante\n• Resultados mensuráveis\n• Estratégia clara\n\nQual é sua experiência? Compartilhe nos comentários! 👇\n\n#{topic_hashtag} #Instagram #Innovation #Success #Marketing #Business",
                "linkedin": f"A importância de {topic} no desenvolvimento profissional para {audience}\n\nNo cenário atual, dominar {topic} tornou-se fundamental para o crescimento profissional. Organizações líderes estão adotando essas estratégias para:\n\n✅ Melhorar a eficiência\n✅ Impulsionar a inovação\n✅ Gerar resultados sustentáveis\n\nComo sua organização está implementando essas práticas?\n\n#{topic_hashtag} #LinkedIn #Professional #Business #Innovation"
            },
            "zh": {
                "twitter": f"🚀 发现关于{topic}的一切！非常适合寻求创新的{audience}。你怎么看？💭 #{topic_hashtag} #Innovation #Marketing",
                "blog": f"# 关于{topic}你需要知道的一切\n\n你是否想过{topic}如何改变你的策略？在这篇文章中，我们探索{audience}的最佳实践。\n\n✨ 发现经过验证的技术\n🎯 有效策略\n📈 可衡量的结果\n\n#{topic_hashtag} #Blog #策略",
                "instagram": f"✨ {topic}正在革命性地改变{audience}的工作方式！🚀\n\n💡 关键提示：\n• 持续创新\n• 可衡量的结果\n• 清晰的策略\n\n你的经验是什么？在评论中分享！👇\n\n#{topic_hashtag} #Instagram #Innovation #Success #Marketing #Business",
                "linkedin": f"{topic}在{audience}职业发展中的重要性\n\n在当今的环境中，掌握{topic}已经成为职业发展的基础。领先的组织正在采用这些策略来：\n\n✅ 提高效率\n✅ 推动创新\n✅ 产生可持续的结果\n\n你的组织如何实施这些实践？\n\n#{topic_hashtag} #LinkedIn #Professional #Business #Innovation"
            }
        }
        
        # Get template for language and platform
        lang_templates = templates.get(language, templates["en"])
        content = lang_templates.get(platform.lower(), lang_templates["twitter"])
        
        return content, f"Demo content for {platform} (Language: {language})"


# ===============================
# INITIALIZE SESSION STATE
# ===============================

if "content_generator" not in st.session_state:
    st.session_state.content_generator = ContentGenerator()
if "generated_content" not in st.session_state:
    st.session_state.generated_content = None
if "selected_platform" not in st.session_state:
    st.session_state.selected_platform = "Twitter"
if "selected_language" not in st.session_state:
    st.session_state.selected_language = "es"

# ===============================
# MAIN INTERFACE
# ===============================

# Hero Section
st.markdown("""
<div class="hero-section">
    <h1>🧠 Generador de Contenido IA</h1>
    <p>Crea contenido atractivo y optimizado para cualquier plataforma con inteligencia artificial</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for configuration
with st.sidebar:
    st.markdown("#### 📊 API Configuration & Status")
    
    # Load environment variables and show their status
    env_vars = {}
    try:
        # Force reload environment variables
        dotenv.load_dotenv(override=True)
        env_vars = {
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
            "GROQ_API_KEY": os.getenv("GROQ_API_KEY", ""), 
            "UNSPLASH_ACCESS_KEY": os.getenv("UNSPLASH_ACCESS_KEY", ""),  # Note: using UNSPLASH_ACCESS_KEY
            "DEEPL_API_KEY": os.getenv("DEEPL_API_KEY", ""),
            "HUGGINGFACE_API_KEY": os.getenv("HUGGINGFACE_API_KEY", ""),
            "LANGSMITH_API_KEY": os.getenv("LANGSMITH_API_KEY", ""),
        }
        
        # Debug: Print loaded values (masked)
        st.write("**🔍 Debug - Environment Variables:**")
        for key, value in env_vars.items():
            masked_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            status = "✅" if value else "❌"
            st.write(f"{status} {key}: {masked_value if value else 'Not found'}")
            
    except Exception as e:
        st.error(f"Error loading .env: {str(e)}")
        st.write(f"Current working directory: {os.getcwd()}")
        st.write(f".env file exists: {os.path.exists('.env')}")

    st.markdown("---")

    # API key inputs with auto-filled values from .env (but masked)
    st.markdown("**🔑 API Keys (Auto-filled from .env if available):**")
    
    openai_key_input = st.text_input(
        "OpenAI API Key", 
        type="password", 
        value=env_vars.get("OPENAI_API_KEY", ""),
        help="Auto-filled from OPENAI_API_KEY in .env"
    )
    
    groq_key_input = st.text_input(
        "Groq API Key", 
        type="password", 
        value=env_vars.get("GROQ_API_KEY", ""),
        help="Auto-filled from GROQ_API_KEY in .env"
    )
    
    unsplash_key_input = st.text_input(
        "Unsplash API Key", 
        type="password", 
        value=env_vars.get("UNSPLASH_ACCESS_KEY", ""),  # Using UNSPLASH_ACCESS_KEY
        help="Auto-filled from UNSPLASH_ACCESS_KEY in .env"
    )
    
    deepl_key_input = st.text_input(
        "DeepL API Key", 
        type="password", 
        value=env_vars.get("DEEPL_API_KEY", ""),
        help="Auto-filled from DEEPL_API_KEY in .env - Used for translation"
    )

    # Configure APIs with all keys including DeepL
    st.session_state.content_generator.configure_apis(
        openai_key=openai_key_input,
        groq_key=groq_key_input,
        unsplash_key=unsplash_key_input,
        deepl_key=deepl_key_input,
    )

    # Show API status
    st.markdown("**📊 API Status:**")
    generator = st.session_state.content_generator
    
    status_items = [
        ("OpenAI", generator.api_configured, "🤖"),
        ("Groq", generator.groq_configured, "⚡"),
        ("Unsplash", generator.unsplash_configured, "📸"),
        ("DeepL", generator.deepl_configured, "🌐"),
    ]
    
    for name, configured, icon in status_items:
        status = "✅ Ready" if configured else "❌ Not configured"
        color = "api-configured" if configured else "api-not-configured"
        st.markdown(f'<div class="api-status {color}">{icon} {name}: {status}</div>', unsafe_allow_html=True)

    # Language selection
    # Language selection with more options
    supported_languages = {
        "es": "🇪🇸 Español",
        "en": "🇺🇸 English", 
        "fr": "🇫🇷 Français",
        "de": "🇩🇪 Deutsch",
        "it": "🇮🇹 Italiano",
        "pt": "🇵🇹 Português",
        "zh": "🇨🇳 中文 (Chinese)",
        "ja": "🇯🇵 日本語 (Japanese)",
        "ko": "🇰🇷 한국어 (Korean)",
        "ru": "🇷🇺 Русский (Russian)",
        "ar": "🇸🇦 العربية (Arabic)",
        "hi": "🇮🇳 हिंदी (Hindi)",
        "nl": "🇳🇱 Nederlands (Dutch)",
        "sv": "🇸🇪 Svenska (Swedish)",
        "da": "🇩🇰 Dansk (Danish)",
        "no": "🇳🇴 Norsk (Norwegian)",
        "fi": "🇫🇮 Suomi (Finnish)",
        "pl": "🇵🇱 Polski (Polish)",
        "cs": "🇨🇿 Čeština (Czech)",
        "hu": "🇭🇺 Magyar (Hungarian)",
        "tr": "🇹🇷 Türkçe (Turkish)",
        "uk": "🇺🇦 Українська (Ukrainian)",
    }

    selected_lang = st.selectbox(
        "🌐 Language / Idioma",
        options=list(supported_languages.keys()),
        format_func=lambda k: supported_languages[k],
        index=list(supported_languages.keys()).index(st.session_state.selected_language) if st.session_state.selected_language in supported_languages else 0
    )
    st.session_state.selected_language = selected_lang
    
    # Show language support info
    if selected_lang != 'en':
        if st.session_state.content_generator.deepl_configured:
            st.success(f"✅ {supported_languages[selected_lang]} supported with AI + DeepL translation")
        else:
            st.info(f"ℹ️ {supported_languages[selected_lang]} supported with AI direct generation")
            st.warning("💡 For better translation quality, configure DeepL API key")
    else:
        st.info("✅ English is the primary AI language (best results)")

    # AI Model selection
    st.markdown("### 🤖 AI Model")
    
    available_models = ["Demo Inteligente"]
    if st.session_state.content_generator.groq_configured:
        available_models.append("Groq Llama3 (Gratis)")
    if st.session_state.content_generator.api_configured:
        available_models.append("OpenAI GPT-3.5")
    available_models.append("Ollama Local")
    
    ai_model = st.selectbox("Select AI Model", available_models)

    # Image generation toggle
    generate_images = st.checkbox(
        "📸 Generate Images", 
        value=st.session_state.content_generator.unsplash_configured,
        disabled=not st.session_state.content_generator.unsplash_configured
    )

    # Cost information
    st.markdown("### 💰 Costs")
    if ai_model == "Demo Inteligente":
        st.info("🆓 Completely free")
    elif ai_model == "Groq Llama3 (Gratis)":
        st.success("🚀 Free + Ultra fast")
        st.info("14,400 tokens/minute free")
    elif ai_model == "OpenAI GPT-3.5":
        st.info("💸 ~$0.002 per 1K tokens")
    elif ai_model == "Ollama Local":
        st.info("🆓 Free (requires installation)")

    if st.session_state.content_generator.unsplash_configured:
        st.info("📸 Unsplash: 50 downloads/hour free")

# Main layout
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📝 Create Content")

    # Main form
    with st.form("content_form"):
        # Topic input
        topic = st.text_input(
            "💡 Topic",
            placeholder="E.g: Artificial Intelligence, Digital Marketing, Productivity...",
            help="Describe the main topic of your content",
        )

        # Platform selection with visual cards
        st.markdown("#### 📱 Platform")

        platforms = [
            {"name": "Twitter", "icon": "🐦", "desc": "Concise and viral tweets"},
            {"name": "Blog", "icon": "📝", "desc": "Informative articles"},
            {"name": "Instagram", "icon": "📸", "desc": "Visual posts with hashtags"},
            {"name": "LinkedIn", "icon": "💼", "desc": "Professional content"},
        ]

        platform_cols = st.columns(4)
        platform_selected = None

        for i, platform_data in enumerate(platforms):
            with platform_cols[i]:
                if st.form_submit_button(
                    f"{platform_data['icon']}\n{platform_data['name']}\n{platform_data['desc']}",
                    help=f"Optimize for {platform_data['name']}",
                    use_container_width=True,
                ):
                    st.session_state.selected_platform = platform_data["name"]
                    platform_selected = platform_data["name"]

        # Show selected platform
        if st.session_state.selected_platform:
            selected_platform_data = next(
                p for p in platforms if p["name"] == st.session_state.selected_platform
            )
            st.success(
                f"✅ Selected platform: **{selected_platform_data['icon']} {selected_platform_data['name']}**"
            )

        # Additional inputs
        col_a, col_b = st.columns(2)

        with col_a:
            audience = st.text_input(
                "🎯 Audience",
                placeholder="E.g: teenagers, marketers, entrepreneurs...",
                help="Define your target audience",
            )

        with col_b:
            tone = st.selectbox(
                "🎭 Tone",
                ["profesional", "casual", "divertido", "inspiracional", "educativo"],
                help="Select the content tone",
            )

        # Generation button
        generate_button = st.form_submit_button("🚀 Generate Content", type="primary")

        # Generation logic
        if generate_button:
            if not topic:
                st.error("⚠️ Please enter a topic")
            elif not st.session_state.selected_platform:
                st.error("⚠️ Please select a platform")
            else:
                # Show progress
                progress_container = st.container()

                with progress_container:
                    st.markdown("### 🤖 Generating content...")

                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    # Process steps
                    steps = [
                        ("🧠 Analyzing topic and audience...", 20),
                        ("✍️ Generating optimized content...", 40),
                        (("🖼️ Searching for perfect image..." if generate_images else "🎨 Applying platform style..."), 60),
                        ("🎨 Finalizing optimization...", 80),
                        ("✅ Content ready!", 100),
                    ]

                    for step_text, progress in steps:
                        status_text.markdown(
                            f'<div class="progress-step">{step_text}</div>',
                            unsafe_allow_html=True,
                        )
                        progress_bar.progress(progress)
                        time.sleep(0.8)

                    # Generate content according to selected model
                    generator = st.session_state.content_generator
                    platform = st.session_state.selected_platform
                    language = st.session_state.selected_language

                    if ai_model == "Groq Llama3 (Gratis)" and generator.groq_configured:
                        content, status = generator.generate_with_groq(
                            topic, platform, audience, tone, language
                        )
                    elif ai_model == "OpenAI GPT-3.5" and generator.api_configured:
                        content, status = generator.generate_with_openai(
                            topic, platform, audience, tone, language
                        )
                    elif ai_model == "Ollama Local":
                        content, status = generator.generate_with_ollama(
                            topic, platform, audience, tone, language
                        )
                    else:  # Demo Inteligente
                        content, status = generator.generate_demo_content(
                            topic, platform, audience, tone, language
                        )

                    # Search for Unsplash image if configured
                    image_data = None
                    image_status = ""
                    search_keyword_used = ""

                    if generate_images and generator.unsplash_configured and content:
                        status_text.markdown(
                            '<div class="progress-step">🧠 Analyzing content to find perfect image...</div>',
                            unsafe_allow_html=True,
                        )

                        # Use intelligent search
                        image_data, image_status = generator.search_unsplash_image_intelligent(
                            content=content,
                            topic=topic,
                            platform=platform,
                        )

                        if image_data:
                            search_keyword_used = "Intelligent content analysis"
                        else:
                            search_keyword_used = "No results found"

                    if content:
                        # Save result
                        result_data = {
                            "topic": topic,
                            "platform": platform,
                            "audience": audience,
                            "tone": tone,
                            "language": language,
                            "content": content,
                            "status": status,
                            "model": ai_model,
                            "image_data": image_data,
                            "image_status": image_status,
                            "search_keyword_used": search_keyword_used,
                            "timestamp": datetime.now(),
                        }

                        st.session_state.generated_content = result_data

                        status_text.success("✅ Content generated successfully!")
                        progress_bar.empty()
                        st.balloons()
                    else:
                        status_text.error(f"❌ Error: {status}")
                        progress_bar.empty()

with col2:
    st.markdown("### 💡 Suggestions")

    # Dynamic tips according to platform
    platform_tips = {
        "Twitter": "🐦 Keep the message concise and use trending hashtags",
        "Blog": "📝 Include attractive titles and clear structure",
        "Instagram": "📸 Use eye-catching emojis and popular hashtags",
        "LinkedIn": "💼 Focus on professional value and networking",
    }

    current_tip = platform_tips.get(
        st.session_state.selected_platform,
        "💡 Select a platform to see specific tips",
    )
    st.info(current_tip)

    # Quick templates
    st.markdown("#### 📄 Quick Templates")

    quick_topics = [
        "🔥 Trends 2025",
        "💡 Productivity tips",
        "🚀 Tech innovation",
        "📈 Growth strategies",
        "🎯 Effective marketing",
    ]

    for topic_template in quick_topics:
        if st.button(
            topic_template, use_container_width=True, key=f"template_{topic_template}"
        ):
            # Auto-fill the topic (this would need to be implemented in the form)
            st.session_state.quick_topic = topic_template.split(" ", 1)[1]  # Remove emoji

# Show generated content
if st.session_state.generated_content:
    content_data = st.session_state.generated_content

    st.markdown("---")
    st.markdown("### 📊 Generated Content")

    # Metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Platform", content_data["platform"])
    with col2:
        st.metric("AI Model", content_data["model"].split()[0])
    with col3:
        st.metric("Characters", len(content_data["content"]))
    with col4:
        st.metric("Words", len(content_data["content"].split()))

    # Final content
    st.markdown(
        f"""
    <div class="generated-content">
        <h4>🎯 Content for {content_data['platform']} ({content_data.get('language', 'es')})</h4>
        <div style="background: white; padding: 1.5rem; border-radius: 8px; margin: 1rem 0; border: 1px solid #e1e5e9;">
            {content_data['content'].replace(chr(10), '<br>')}
        </div>
        <small>✨ {content_data['status']}</small>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Show Unsplash image if exists
    if content_data.get("image_data"):
        st.markdown("#### 📸 Unsplash Image")

        image_data = content_data["image_data"]

        col_img1, col_img2 = st.columns([2, 1])

        with col_img1:
            st.image(
                image_data["url"],
                caption=f"📷 Photo by {image_data['author']} on Unsplash",
                use_column_width=True,
            )

        with col_img2:
            st.markdown("**Image Details:**")
            st.write(f"**Author:** [{image_data['author']}]({image_data['author_url']})")
            if image_data["description"]:
                st.write(f"**Description:** {image_data['description'][:100]}...")
            st.write(f"**Status:** {content_data.get('image_status', 'Image found')}")

            # Download button
            if st.button("📥 Download Original Image", use_container_width=True):
                st.info("💡 Right-click on the image and select 'Save image as...'")

    elif content_data.get("image_status"):
        st.markdown("#### 📸 Image Status")
        if "No results" in content_data["image_status"]:
            st.warning(f"⚠️ {content_data['image_status']}")
            st.info("💡 Try with a more specific topic or verify your Unsplash API key")
        else:
            st.info(f"ℹ️ {content_data['image_status']}")

    # Action buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📋 Copy Content", use_container_width=True):
            st.success("✅ Content copied!")
            st.code(content_data["content"])

    with col2:
        if st.button("🔄 Regenerate", use_container_width=True):
            st.session_state.generated_content = None
            st.info("🔄 Click 'Generate Content' to create a new version")

    with col3:
        if st.button("📤 Share", use_container_width=True):
            st.info("📤 Share function coming soon")

    # Show process details
    with st.expander("🔍 View Process Details"):
        st.markdown(
            f"""
        **📝 Parameters used:**
        - **Topic:** {content_data['topic']}
        - **Platform:** {content_data['platform']}
        - **Audience:** {content_data['audience']}
        - **Tone:** {content_data['tone']}
        - **Language:** {content_data.get('language', 'es')}
        - **Model:** {content_data['model']}
        - **Timestamp:** {content_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
        
        **📸 Image information:**
        - **Status:** {content_data.get('image_status', 'No image')}
        - **Method:** {content_data.get('search_keyword_used', 'N/A')}
        - **Source:** {"Unsplash" if content_data.get('image_data') else "Not applicable"}
        """
        )

        # Show intelligent keyword analysis
        if st.button("🧠 View Keyword Analysis", key="show_analysis"):
            generator = st.session_state.content_generator
            if generator.unsplash_configured:
                try:
                    extracted_concepts = generator.extract_visual_concepts_from_content(
                        content_data["content"], content_data["topic"]
                    )
                    st.success(f"🎯 **Automatically extracted concepts:** {extracted_concepts}")
                    st.info("💡 These concepts are generated by analyzing real content, not using static dictionaries")
                except Exception as e:
                    st.error(f"Analysis error: {str(e)}")
            else:
                st.warning("⚠️ Configure Unsplash to see intelligent analysis")

        if content_data.get("image_data"):
            image_data = content_data["image_data"]
            st.markdown(
                f"""
            **🖼️ Unsplash image details:**
            - **Author:** {image_data['author']}
            - **Description:** {image_data.get('description', 'No description')}
            - **Resolution:** {image_data.get('width', 'N/A')} x {image_data.get('height', 'N/A')}
            - **URL:** [View on Unsplash]({image_data['author_url']})
            """
            )

# Footer with improved information
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 🚀 Upcoming Features
    - Automatic scheduling
    - Multiple variations
    - Engagement analysis
    - Image editor
    - Multi-language support
    """)

with col2:
    st.markdown("""
    ### 🔧 Supported APIs
    - Groq Llama3 (Ultra fast)
    - OpenAI GPT-3.5/4
    - Ollama (Local)
    - Unsplash (Images)
    - Environment variables
    """)

with col3:
    st.markdown("""
    ### 📊 Platforms
    - Twitter/X
    - Instagram
    - LinkedIn
    - Blog/Website
    - Multi-language content
    """)

# Additional information
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9em;">
    <p>🧠 <strong>AI Content Generator</strong> - Create engaging content optimized for any platform</p>
    <p>Made with ❤️ using Streamlit | Version 2.0 | Multi-language support</p>
</div>
""", unsafe_allow_html=True)