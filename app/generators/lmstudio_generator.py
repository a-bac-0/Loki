# app/generators/lmstudio_generator.py
import json
import time
from typing import Dict, List, Optional, Tuple, Union

import requests


class LMStudioGenerator:
    """Clase para interactuar con LM Studio para generar texto y prompts visuales"""

    def __init__(self, base_url="http://127.0.0.1:1234"):
        """Inicializa el generador de LM Studio

        Args:
            base_url (str): URL base de la API de LM Studio
        """
        self.base_url = base_url
        self.api_endpoint = f"{base_url}/v1/chat/completions"

    def check_server_status(self) -> bool:
        """Verifica si el servidor de LM Studio está en funcionamiento

        Returns:
            bool: True si el servidor está activo, False en caso contrario
        """
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def generate_content(
        self, topic: str, platform: str, audience: str, tone: str = "profesional"
    ) -> Tuple[Optional[str], str]:
        """Genera contenido para una plataforma específica

        Args:
            topic (str): Tema sobre el que generar contenido
            platform (str): Plataforma para la que optimizar el contenido
            audience (str): Audiencia objetivo
            tone (str): Tono del contenido

        Returns:
            Tuple[Optional[str], str]: (contenido generado, mensaje de estado)
        """
        if not self.check_server_status():
            return (
                None,
                "LM Studio no está disponible. Asegúrate de que esté ejecutándose en http://127.0.0.1:1234",
            )

        platform_instructions = {
            "twitter": "Crea un tweet atractivo y conciso (máximo 280 caracteres)",
            "blog": "Crea una introducción engaging para un artículo de blog",
            "instagram": "Crea un post visual para Instagram con emojis y hashtags",
            "linkedin": "Crea un post profesional para LinkedIn",
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

        try:
            payload = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Crea contenido sobre: {topic}"},
                ],
                "temperature": 0.7,
                "max_tokens": 500,
                "stream": False,
            }

            response = requests.post(self.api_endpoint, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"].strip()
                return content, "Contenido generado con LM Studio (Gemma 3)"
            else:
                return (
                    None,
                    f"Error en API de LM Studio: {response.status_code} - {response.text}",
                )

        except requests.exceptions.Timeout:
            return None, "Timeout conectando con LM Studio"
        except Exception as e:
            return None, f"Error con LM Studio: {str(e)}"

    def generate_image_prompt(
        self, content: str, topic: str, style: str = "realistic"
    ) -> Tuple[Optional[str], str]:
        """Genera un prompt optimizado para la generación de imágenes

        Args:
            content (str): Contenido de texto generado
            topic (str): Tema principal
            style (str): Estilo visual deseado

        Returns:
            Tuple[Optional[str], str]: (prompt para imagen, mensaje de estado)
        """
        if not self.check_server_status():
            return (
                None,
                "LM Studio no está disponible. Asegúrate de que esté ejecutándose en http://127.0.0.1:1234",
            )

        system_prompt = f"""
        Eres un experto en crear prompts para modelos de generación de imágenes como Stable Diffusion.
        
        Tu tarea es crear un prompt detallado y descriptivo para generar una imagen que acompañe al siguiente contenido.
        
        Instrucciones para crear el prompt visual:
        1. Analiza el contenido y extrae los conceptos visuales clave
        2. Crea un prompt descriptivo y detallado (entre 30-80 palabras)
        3. Incluye elementos visuales concretos, no conceptos abstractos
        4. Especifica el estilo visual: {style}
        5. Incluye detalles sobre iluminación, perspectiva y ambiente
        6. NO incluyas texto o palabras dentro de la imagen
        7. Evita mencionar logos o marcas específicas
        
        Responde SOLO con el prompt para la imagen, sin explicaciones adicionales.
        """

        try:
            payload = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"Contenido: {content}\n\nTema principal: {topic}\n\nCrea un prompt visual detallado para generar una imagen que acompañe este contenido.",
                    },
                ],
                "temperature": 0.7,
                "max_tokens": 300,
                "stream": False,
            }

            response = requests.post(self.api_endpoint, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()
                prompt = result["choices"][0]["message"]["content"].strip()
                return prompt, "Prompt visual generado con LM Studio (Gemma 3)"
            else:
                return (
                    None,
                    f"Error en API de LM Studio: {response.status_code} - {response.text}",
                )

        except requests.exceptions.Timeout:
            return None, "Timeout conectando con LM Studio"
        except Exception as e:
            return None, f"Error con LM Studio: {str(e)}"

    def analyze_content_for_keywords(
        self, content: str, topic: str
    ) -> Tuple[Optional[List[str]], str]:
        """Analiza el contenido para extraer palabras clave relevantes

        Args:
            content (str): Contenido de texto generado
            topic (str): Tema principal

        Returns:
            Tuple[Optional[List[str]], str]: (lista de palabras clave, mensaje de estado)
        """
        if not self.check_server_status():
            return (
                None,
                "LM Studio no está disponible. Asegúrate de que esté ejecutándose en http://127.0.0.1:1234",
            )

        system_prompt = f"""
        Eres un experto en análisis de contenido y extracción de palabras clave.
        
        Tu tarea es analizar el siguiente contenido y extraer exactamente 5 palabras clave o frases cortas que:
        1. Representen los conceptos visuales más importantes
        2. Sean concretas y descriptivas (evita conceptos abstractos)
        3. Puedan usarse para buscar imágenes relevantes
        4. Estén directamente relacionadas con el tema y contenido
        
        Responde SOLO con las 5 palabras clave separadas por comas, sin explicaciones adicionales.
        """

        try:
            payload = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"Contenido: {content}\n\nTema principal: {topic}\n\nExtrae exactamente 5 palabras clave o frases cortas que representen los conceptos visuales más importantes.",
                    },
                ],
                "temperature": 0.3,
                "max_tokens": 100,
                "stream": False,
            }

            response = requests.post(self.api_endpoint, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()
                keywords_text = result["choices"][0]["message"]["content"].strip()
                keywords = [kw.strip() for kw in keywords_text.split(",") if kw.strip()]
                return keywords, "Palabras clave extraídas con LM Studio (Gemma 3)"
            else:
                return (
                    None,
                    f"Error en API de LM Studio: {response.status_code} - {response.text}",
                )

        except requests.exceptions.Timeout:
            return None, "Timeout conectando con LM Studio"
        except Exception as e:
            return None, f"Error con LM Studio: {str(e)}"
