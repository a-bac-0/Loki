# app/agents/content_visual_agent.py
import json
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

# Importar los generadores
from app.generators.lmstudio_generator import LMStudioGenerator
from app.image_generator.comfyui_generator import ComfyUIGenerator


class ContentVisualAgent:
    """Agente que integra la generación de texto con LM Studio y la generación de imágenes con ComfyUI"""

    def __init__(
        self,
        lmstudio_url="http://127.0.0.1:1234",
        comfyui_url="http://127.0.0.1:8000",
        workflow_file=os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "data",
            "examples",
            "flujo-imagen-post.json",
        ),
        output_dir="images_generated",
    ):
        """Inicializa el agente de contenido visual

        Args:
            lmstudio_url (str): URL de la API de LM Studio
            comfyui_url (str): URL de la API de ComfyUI
            workflow_file (str, optional): Ruta al archivo JSON del flujo de trabajo de ComfyUI
            output_dir (str): Directorio donde se guardarán las imágenes generadas
        """

        print(f"Inicializando ContentVisualAgent con flujo de trabajo: {workflow_file}")
        self.lmstudio_generator = LMStudioGenerator(base_url=lmstudio_url)
        self.comfyui_generator = ComfyUIGenerator(
            base_url=comfyui_url, output_dir=output_dir
        )
        self.workflow_file = workflow_file
        self.workflow_data = None

        # Cargar el flujo de trabajo si se proporciona
        if workflow_file and os.path.exists(workflow_file):
            print(f"Cargando flujo de trabajo desde: {workflow_file}")
            self.load_workflow(workflow_file)

    def load_workflow(self, workflow_file):
        """Carga un flujo de trabajo de ComfyUI desde un archivo JSON

        Args:
            workflow_file (str): Ruta al archivo JSON del flujo de trabajo

        Returns:
            bool: True si se cargó correctamente, False en caso contrario
        """
        try:
            self.workflow_data = self.comfyui_generator.load_workflow(workflow_file)
            self.workflow_file = workflow_file
            return True
        except Exception as e:
            print(f"Error al cargar el flujo de trabajo: {str(e)}")
            return False

    def check_services(self) -> Dict[str, bool]:
        """Verifica si los servicios están disponibles

        Returns:
            Dict[str, bool]: Estado de cada servicio
        """
        return {
            "lmstudio": self.lmstudio_generator.check_server_status(),
            "comfyui": self.comfyui_generator.check_server_status(),
        }

    def generate_content(
        self, topic: str, platform: str, audience: str, tone: str = "profesional"
    ) -> Tuple[Optional[str], str]:
        """Genera contenido de texto usando LM Studio

        Args:
            topic (str): Tema sobre el que generar contenido
            platform (str): Plataforma para la que optimizar el contenido
            audience (str): Audiencia objetivo
            tone (str): Tono del contenido

        Returns:
            Tuple[Optional[str], str]: (contenido generado, mensaje de estado)
        """
        return self.lmstudio_generator.generate_content(topic, platform, audience, tone)

    def generate_image_prompt(
        self, content: str, topic: str, style: str = "realistic"
    ) -> Tuple[Optional[str], str]:
        """Genera un prompt para imagen usando LM Studio

        Args:
            content (str): Contenido de texto generado
            topic (str): Tema principal
            style (str): Estilo visual deseado

        Returns:
            Tuple[Optional[str], str]: (prompt para imagen, mensaje de estado)
        """
        return self.lmstudio_generator.generate_image_prompt(content, topic, style)

    def generate_image(self, prompt: str) -> Tuple[Optional[Dict[str, Any]], str]:
        """Genera una imagen usando ComfyUI

        Args:
            prompt (str): Prompt para generar la imagen

        Returns:
            Tuple[Optional[Dict[str, Any]], str]: (datos de la imagen generada, mensaje de estado)
        """
        try:
            if not self.workflow_data and not self.workflow_file:
                return None, "No se ha cargado un flujo de trabajo de ComfyUI"

            # Pasar tanto workflow_data como workflow_file para mayor robustez
            image_data = self.comfyui_generator.generate_image(
                prompt=prompt,
                workflow_data=self.workflow_data,
                workflow_file=self.workflow_file,
            )

            return image_data, "Imagen generada correctamente"

        except Exception as e:
            return None, f"Error al generar la imagen: {str(e)}"

    def generate_complete_content(
        self,
        topic: str,
        platform: str,
        audience: str,
        tone: str = "profesional",
        image_style: str = "realistic",
        status_callback=None,
    ) -> Dict[str, Any]:
        """Genera contenido completo (texto e imagen) en un solo proceso

        Args:
            topic (str): Tema sobre el que generar contenido
            platform (str): Plataforma para la que optimizar el contenido
            audience (str): Audiencia objetivo
            tone (str): Tono del contenido
            image_style (str): Estilo visual para la imagen

        Returns:
            Dict[str, Any]: Resultado completo con texto e imagen
        """
        result = {
            "topic": topic,
            "platform": platform,
            "audience": audience,
            "tone": tone,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "steps": [],
        }

        # Paso 1: Verificar servicios
        if status_callback:
            status_callback("Verificando servicios...")
        services_status = self.check_services()
        result["steps"].append(
            {
                "step": "check_services",
                "status": "success" if all(services_status.values()) else "error",
                "details": services_status,
            }
        )

        if not all(services_status.values()):
            result["error"] = "Algunos servicios no están disponibles"
            return result

        # Paso 2: Generar contenido de texto
        if status_callback:
            status_callback("Generando contenido de texto...")
        content, content_status = self.generate_content(topic, platform, audience, tone)
        result["steps"].append(
            {
                "step": "generate_content",
                "status": "success" if content else "error",
                "details": content_status,
            }
        )

        if not content:
            result["error"] = content_status
            return result

        result["content"] = content

        # Paso 3: Generar prompt para imagen
        if status_callback:
            status_callback("Generando prompt para imagen...")
        image_prompt, prompt_status = self.generate_image_prompt(
            content, topic, image_style
        )
        result["steps"].append(
            {
                "step": "generate_image_prompt",
                "status": "success" if image_prompt else "error",
                "details": prompt_status,
            }
        )

        if not image_prompt:
            # Podemos continuar sin imagen si falla este paso
            result["image_prompt_error"] = prompt_status
            result["success"] = True  # Éxito parcial (tenemos contenido)
            return result

        result["image_prompt"] = image_prompt

        # Paso 4: Generar imagen
        if status_callback:
            status_callback("Generando imagen con ComfyUI...")
        image_data, image_status = self.generate_image(image_prompt)
        result["steps"].append(
            {
                "step": "generate_image",
                "status": "success" if image_data else "error",
                "details": image_status,
            }
        )

        if not image_data:
            # Podemos continuar sin imagen si falla este paso
            result["image_error"] = image_status
            result["success"] = True  # Éxito parcial (tenemos contenido)
            return result

        result["image_data"] = image_data
        # Añadir la ruta de la imagen directamente en el resultado para facilitar su acceso
        if "local_path" in image_data:
            result["image_path"] = image_data["local_path"]
        result["success"] = True

        if status_callback:
            status_callback("¡Contenido visual generado con éxito!")

        return result

    def extract_keywords(self, content: str, topic: str) -> List[str]:
        """Extrae palabras clave del contenido para búsqueda de imágenes alternativa

        Args:
            content (str): Contenido de texto generado
            topic (str): Tema principal

        Returns:
            List[str]: Lista de palabras clave
        """
        keywords, status = self.lmstudio_generator.analyze_content_for_keywords(
            content, topic
        )
        return keywords if keywords else []
