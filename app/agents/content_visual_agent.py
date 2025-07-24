# app/agents/content_visual_agent.py
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Union, Any

# Importar los generadores
from app.generators.lmstudio_generator import LMStudioGenerator
from app.image_generator.comfyui_generator import ComfyUIGenerator

class ContentVisualAgent:
    """Agente que integra la generación de texto con LM Studio y la generación de imágenes con ComfyUI"""
    
    def __init__(self, 
                lmstudio_url="http://127.0.0.1:1234", 
                comfyui_url="http://127.0.0.1:8000",
                workflow_file = os.path.join(os.path.dirname(__file__), "..", "..",'data', "examples", "flujo-imagen-post.json"),
                output_dir="images_generated"):
        """Inicializa el agente de contenido visual
        
        Args:
            lmstudio_url (str): URL de la API de LM Studio
            comfyui_url (str): URL de la API de ComfyUI
            workflow_file (str, optional): Ruta al archivo JSON del flujo de trabajo de ComfyUI
            output_dir (str): Directorio donde se guardarán las imágenes generadas
        """

        print("\n" + "="*80)
        print(f"INICIALIZANDO CONTENT VISUAL AGENT")
        print(f"LM Studio URL: {lmstudio_url}")
        print(f"ComfyUI URL: {comfyui_url}")
        print(f"Workflow file: {workflow_file}")
        print(f"Output dir: {output_dir}")
        print("="*80)
        
        self.lmstudio_generator = LMStudioGenerator(base_url=lmstudio_url)
        self.comfyui_generator = ComfyUIGenerator(base_url=comfyui_url, output_dir=output_dir)
        self.workflow_file = workflow_file
        self.workflow_data = None
        
        # Cargar el flujo de trabajo si se proporciona
        if workflow_file:
            if os.path.exists(workflow_file):
                print(f"✅ Archivo de flujo de trabajo encontrado: {workflow_file}")
                try:
                    print(f"Cargando flujo de trabajo...")
                    success = self.load_workflow(workflow_file)
                    if success:
                        print(f"✅ Flujo de trabajo cargado correctamente")
                        print(f"Tipo de workflow_data: {type(self.workflow_data)}")
                        if isinstance(self.workflow_data, dict) and "nodes" in self.workflow_data:
                            print(f"Número de nodos: {len(self.workflow_data['nodes'])}")
                    else:
                        print(f"❌ Error al cargar el flujo de trabajo")
                except Exception as e:
                    print(f"❌ Excepción al cargar el flujo de trabajo: {str(e)}")
                    import traceback
                    print(f"Traceback: {traceback.format_exc()}")
            else:
                print(f"❌ Archivo de flujo de trabajo no encontrado: {workflow_file}")
        else:
            print(f"⚠️ No se proporcionó archivo de flujo de trabajo")
    
    def load_workflow(self, workflow_file):
        """Carga un flujo de trabajo de ComfyUI desde un archivo JSON
        
        Args:
            workflow_file (str): Ruta al archivo JSON del flujo de trabajo
            
        Returns:
            bool: True si se cargó correctamente, False en caso contrario
        """
        print(f"\nCargando flujo de trabajo desde: {workflow_file}")
        
        if not os.path.exists(workflow_file):
            print(f"❌ ERROR: El archivo de flujo de trabajo no existe: {workflow_file}")
            return False
            
        try:
            print(f"Llamando a comfyui_generator.load_workflow...")
            workflow_data = self.comfyui_generator.load_workflow(workflow_file)
            
            print(f"Flujo de trabajo cargado. Tipo: {type(workflow_data)}")
            
            # Validar el formato del workflow_data
            if isinstance(workflow_data, dict):
                print(f"✅ workflow_data es un diccionario")
                if "nodes" in workflow_data:
                    print(f"✅ workflow_data contiene la clave 'nodes'")
                    print(f"Número de nodos: {len(workflow_data['nodes'])}")
                else:
                    print(f"⚠️ workflow_data no contiene la clave 'nodes'")
                    print(f"Claves disponibles: {list(workflow_data.keys())}")
            elif isinstance(workflow_data, list):
                print(f"⚠️ workflow_data es una lista, no un diccionario")
                print(f"Longitud de la lista: {len(workflow_data)}")
                if len(workflow_data) > 0:
                    print(f"Primer elemento tipo: {type(workflow_data[0])}")
                    
                    # Si es una lista con un solo elemento y ese elemento es un diccionario, usar ese elemento
                    if len(workflow_data) == 1 and isinstance(workflow_data[0], dict):
                        print(f"Corrigiendo workflow_data: usando el primer elemento de la lista")
                        workflow_data = workflow_data[0]
                        print(f"Nuevo tipo de workflow_data: {type(workflow_data)}")
                        if "nodes" in workflow_data:
                            print(f"✅ workflow_data corregido contiene la clave 'nodes'")
                            print(f"Número de nodos: {len(workflow_data['nodes'])}")
            else:
                print(f"❌ workflow_data no es ni un diccionario ni una lista, es {type(workflow_data)}")
                
            self.workflow_data = workflow_data
            self.workflow_file = workflow_file
            return True
            
        except Exception as e:
            print(f"❌ ERROR al cargar el flujo de trabajo: {str(e)}")
            print(f"Tipo de error: {type(e).__name__}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return False
    
    def check_services(self) -> Dict[str, bool]:
        """Verifica si los servicios están disponibles
        
        Returns:
            Dict[str, bool]: Estado de cada servicio
        """
        return {
            "lmstudio": self.lmstudio_generator.check_server_status(),
            "comfyui": self.comfyui_generator.check_server_status()
        }
    
    def generate_content(self, 
                        topic: str, 
                        platform: str, 
                        audience: str, 
                        tone: str = "profesional") -> Tuple[Optional[str], str]:
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
    
    def generate_image_prompt(self, 
                             content: str, 
                             topic: str, 
                             style: str = "realistic") -> Tuple[Optional[str], str]:
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
        print("\n" + "-"*80)
        print(f"GENERANDO IMAGEN CON COMFYUI")
        print(f"Prompt: {prompt[:100]}...")
        print(f"Workflow file disponible: {'Sí' if self.workflow_file else 'No'}")
        print(f"Workflow data disponible: {'Sí' if self.workflow_data else 'No'}")
        
        if self.workflow_data:
            print(f"Tipo de workflow_data: {type(self.workflow_data)}")
            if isinstance(self.workflow_data, list):
                print(f"ADVERTENCIA: workflow_data es una lista, no un diccionario")
                print(f"Longitud de la lista: {len(self.workflow_data)}")
                print(f"Primeros elementos: {self.workflow_data[:3] if len(self.workflow_data) > 0 else 'Lista vacía'}")
                
                # Intentar corregir el problema si es una lista con un solo elemento diccionario
                if len(self.workflow_data) == 1 and isinstance(self.workflow_data[0], dict):
                    print(f"Corrigiendo workflow_data: usando el primer elemento de la lista")
                    self.workflow_data = self.workflow_data[0]
                    print(f"Nuevo tipo de workflow_data: {type(self.workflow_data)}")
        print("-"*80)
        
        try:
            if not self.workflow_data and not self.workflow_file:
                print("❌ No se ha cargado un flujo de trabajo de ComfyUI")
                return None, "No se ha cargado un flujo de trabajo de ComfyUI"
            
            # Verificar y preparar workflow_data si existe
            workflow_data_to_use = None
            if self.workflow_data:
                if isinstance(self.workflow_data, dict):
                    print("✅ Usando workflow_data (diccionario)")
                    workflow_data_to_use = self.workflow_data
                elif isinstance(self.workflow_data, list) and len(self.workflow_data) > 0:
                    print(f"⚠️ workflow_data es una lista, intentando usar el primer elemento")
                    if isinstance(self.workflow_data[0], dict):
                        print("✅ Usando primer elemento de la lista como workflow_data")
                        workflow_data_to_use = self.workflow_data[0]
                    else:
                        print(f"❌ El primer elemento de la lista no es un diccionario, es {type(self.workflow_data[0])}")
                else:
                    print(f"❌ workflow_data no es utilizable: {type(self.workflow_data)}")
            
            # Verificar workflow_file si existe
            workflow_file_to_use = None
            if self.workflow_file and os.path.exists(self.workflow_file):
                print(f"✅ Usando workflow_file: {self.workflow_file}")
                workflow_file_to_use = self.workflow_file
            elif self.workflow_file:
                print(f"❌ El archivo workflow_file no existe: {self.workflow_file}")
            
            # Pasar tanto workflow_data como workflow_file para mayor robustez
            print("Llamando a comfyui_generator.generate_image...")
            image_data = self.comfyui_generator.generate_image(
                prompt=prompt,
                workflow_data=workflow_data_to_use,
                workflow_file=workflow_file_to_use
            )
            
            print(f"✅ Imagen generada correctamente")
            if image_data and "local_path" in image_data:
                print(f"Ruta de la imagen: {image_data['local_path']}")
            
            return image_data, "Imagen generada correctamente"
            
        except Exception as e:
            print(f"❌ ERROR en generate_image: {str(e)}")
            print(f"Tipo de error: {type(e).__name__}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return None, f"Error al generar la imagen: {str(e)}"
    
    def generate_complete_content(self, 
                                 topic: str, 
                                 platform: str, 
                                 audience: str, 
                                 tone: str = "profesional",
                                 image_style: str = "realistic",
                                 status_callback=None) -> Dict[str, Any]:
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
            "steps": []
        }
        
        # Paso 1: Verificar servicios
        if status_callback:
            status_callback("Verificando servicios...")
        services_status = self.check_services()
        result["steps"].append({
            "step": "check_services",
            "status": "success" if all(services_status.values()) else "error",
            "details": services_status
        })
        
        if not all(services_status.values()):
            result["error"] = "Algunos servicios no están disponibles"
            return result
        
        # Paso 2: Generar contenido de texto
        if status_callback:
            status_callback("Generando contenido de texto...")
        content, content_status = self.generate_content(topic, platform, audience, tone)
        result["steps"].append({
            "step": "generate_content",
            "status": "success" if content else "error",
            "details": content_status
        })
        
        if not content:
            result["error"] = content_status
            return result
        
        result["content"] = content
        
        # Paso 3: Generar prompt para imagen
        if status_callback:
            status_callback("Generando prompt para imagen...")
        image_prompt, prompt_status = self.generate_image_prompt(content, topic, image_style)
        result["steps"].append({
            "step": "generate_image_prompt",
            "status": "success" if image_prompt else "error",
            "details": prompt_status
        })
        
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
        result["steps"].append({
            "step": "generate_image",
            "status": "success" if image_data else "error",
            "details": image_status
        })
        
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
        keywords, status = self.lmstudio_generator.analyze_content_for_keywords(content, topic)
        return keywords if keywords else []