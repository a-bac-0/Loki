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
                 workflow_file=None,
                 output_dir="images_generated"):
        """Inicializa el agente de contenido visual
        
        Args:
            lmstudio_url (str): URL de la API de LM Studio
            comfyui_url (str): URL de la API de ComfyUI
            workflow_file (str, optional): Ruta al archivo JSON del flujo de trabajo de ComfyUI
            output_dir (str): Directorio donde se guardarán las imágenes generadas
        """
        print("\n" + "="*80)
        print("🚀 INICIALIZANDO CONTENT VISUAL AGENT")
        print(f"📡 LM Studio URL: {lmstudio_url}")
        print(f"📡 ComfyUI URL: {comfyui_url}")
        print(f"📂 Output Dir: {output_dir}")
        print("="*80)
        
        # Inicializar generadores
        self.lmstudio_generator = LMStudioGenerator(base_url=lmstudio_url)
        self.comfyui_generator = ComfyUIGenerator(base_url=comfyui_url, output_dir=output_dir)
        
        # Configurar workflow por defecto si no se proporciona
        if workflow_file is None:
            workflow_file = os.path.join(
                os.path.dirname(__file__), "..", "..", 
                'data', "examples", "flujo-imagen-post.json"
            )
        
        self.workflow_file = workflow_file
        self.workflow_data = None
        
        # Cargar workflow si existe
        if workflow_file and os.path.exists(workflow_file):
            print(f"📄 Workflow file: {workflow_file}")
            self._load_and_validate_workflow()
        else:
            print(f"⚠️ Workflow file no encontrado: {workflow_file}")
            print("   El workflow se cargará cuando sea necesario")
    
    def _load_and_validate_workflow(self):
        """Carga y valida el workflow de ComfyUI"""
        try:
            print("📂 Cargando workflow...")
            self.workflow_data = self.comfyui_generator.load_workflow(self.workflow_file)
            
            if self.workflow_data:
                print("✅ Workflow cargado correctamente")
                
                # Validar estructura
                if isinstance(self.workflow_data, dict):
                    if "nodes" in self.workflow_data:
                        nodes = self.workflow_data["nodes"]
                        if isinstance(nodes, dict):
                            print(f"📊 Workflow válido: {len(nodes)} nodos en formato API")
                        elif isinstance(nodes, list):
                            print(f"📊 Workflow en formato UI: {len(nodes)} nodos (se convertirá automáticamente)")
                        else:
                            print(f"⚠️ Formato de nodos desconocido: {type(nodes)}")
                    else:
                        print("⚠️ Workflow no contiene clave 'nodes'")
                else:
                    print(f"⚠️ Workflow no es un diccionario: {type(self.workflow_data)}")
            else:
                print("❌ Error al cargar workflow")
                
        except Exception as e:
            print(f"❌ Excepción al cargar workflow: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            self.workflow_data = None
    
    def check_services(self) -> Dict[str, bool]:
        """Verifica si los servicios están disponibles
        
        Returns:
            Dict[str, bool]: Estado de cada servicio
        """
        print("🔍 Verificando estado de servicios...")
        
        services_status = {
            "lmstudio": self.lmstudio_generator.check_server_status(),
            "comfyui": self.comfyui_generator.check_server_status()
        }
        
        for service, status in services_status.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {service.upper()}: {'Disponible' if status else 'No disponible'}")
        
        return services_status
    
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
        print(f"📝 Generando contenido de texto...")
        print(f"   Tema: {topic}")
        print(f"   Plataforma: {platform}")
        print(f"   Audiencia: {audience}")
        print(f"   Tono: {tone}")
        
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
        print(f"🎨 Generando prompt para imagen...")
        print(f"   Contenido: {content[:100]}...")
        print(f"   Tema: {topic}")
        print(f"   Estilo: {style}")
        
        return self.lmstudio_generator.generate_image_prompt(content, topic, style)
    
    def generate_image(self, prompt: str) -> Tuple[Optional[Dict[str, Any]], str]:
        """Genera una imagen usando ComfyUI
        
        Args:
            prompt (str): Prompt para generar la imagen
            
        Returns:
            Tuple[Optional[Dict[str, Any]], str]: (datos de la imagen generada, mensaje de estado)
        """
        print("\n" + "-"*80)
        print("🖼️ GENERANDO IMAGEN CON COMFYUI")
        print(f"📝 Prompt: {prompt[:100]}...")
        print("-"*80)
        
        try:
            # Verificar que tenemos un workflow disponible
            if not self.workflow_data and not self.workflow_file:
                error_msg = "No hay workflow disponible para generar imagen"
                print(f"❌ {error_msg}")
                return None, error_msg
            
            # Si no tenemos workflow_data pero sí workflow_file, intentar cargar
            if not self.workflow_data and self.workflow_file:
                if os.path.exists(self.workflow_file):
                    print("🔄 Cargando workflow desde archivo...")
                    self._load_and_validate_workflow()
                    if not self.workflow_data:
                        error_msg = f"No se pudo cargar workflow desde {self.workflow_file}"
                        print(f"❌ {error_msg}")
                        return None, error_msg
                else:
                    error_msg = f"Archivo de workflow no encontrado: {self.workflow_file}"
                    print(f"❌ {error_msg}")
                    return None, error_msg
            
            # Generar imagen
            print("🎨 Iniciando generación de imagen...")
            result = self.comfyui_generator.generate_image(
                prompt=prompt,
                workflow_file=self.workflow_file if not self.workflow_data else None,
                workflow_data=self.workflow_data
            )
            
            if result and result.get('status') == 'success':
                print("✅ Imagen generada correctamente")
                if result.get('local_path'):
                    print(f"📂 Imagen guardada en: {result['local_path']}")
                return result, "Imagen generada correctamente"
            else:
                error_msg = result.get('error', 'Error desconocido') if result else 'Error desconocido'
                print(f"❌ Error en generación: {error_msg}")
                return None, f"Error al generar imagen: {error_msg}"
                
        except Exception as e:
            error_msg = f"Excepción al generar imagen: {str(e)}"
            print(f"❌ {error_msg}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return None, error_msg
    
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
            status_callback (callable, optional): Callback para reportar progreso
            
        Returns:
            Dict[str, Any]: Resultado completo con texto e imagen
        """
        print("\n" + "="*80)
        print("🚀 GENERANDO CONTENIDO VISUAL COMPLETO")
        print(f"📋 Tema: {topic}")
        print(f"📱 Plataforma: {platform}")
        print(f"👥 Audiencia: {audience}")
        print(f"🎭 Tono: {tone}")
        print(f"🎨 Estilo imagen: {image_style}")
        print("="*80)
        
        result = {
            "topic": topic,
            "platform": platform,
            "audience": audience,
            "tone": tone,
            "image_style": image_style,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "steps": []
        }
        
        try:
            # Paso 1: Verificar servicios
            if status_callback:
                status_callback("🔍 Verificando servicios...")
            
            print("\n🔍 PASO 1: Verificando servicios...")
            services_status = self.check_services()
            result["steps"].append({
                "step": "check_services",
                "status": "success" if all(services_status.values()) else "error",
                "details": services_status,
                "timestamp": datetime.now().isoformat()
            })
            
            if not all(services_status.values()):
                error_msg = "Algunos servicios no están disponibles"
                result["error"] = error_msg
                print(f"❌ {error_msg}")
                return result
            
            print("✅ Todos los servicios están disponibles")
            
            # Paso 2: Generar contenido de texto
            if status_callback:
                status_callback("📝 Generando contenido de texto...")
            
            print("\n📝 PASO 2: Generando contenido de texto...")
            content, content_status = self.generate_content(topic, platform, audience, tone)
            result["steps"].append({
                "step": "generate_content",
                "status": "success" if content else "error",
                "details": content_status,
                "timestamp": datetime.now().isoformat()
            })
            
            if not content:
                result["error"] = content_status
                print(f"❌ Error generando contenido: {content_status}")
                return result
            
            result["content"] = content
            print(f"✅ Contenido generado: {len(content)} caracteres")
            
            # Paso 3: Generar prompt para imagen
            if status_callback:
                status_callback("🎨 Generando prompt para imagen...")
            
            print("\n🎨 PASO 3: Generando prompt para imagen...")
            image_prompt, prompt_status = self.generate_image_prompt(content, topic, image_style)
            result["steps"].append({
                "step": "generate_image_prompt",
                "status": "success" if image_prompt else "error",
                "details": prompt_status,
                "timestamp": datetime.now().isoformat()
            })
            
            if not image_prompt:
                # Podemos continuar sin imagen si falla este paso
                result["image_prompt_error"] = prompt_status
                result["success"] = True  # Éxito parcial (tenemos contenido)
                print(f"⚠️ Error generando prompt de imagen: {prompt_status}")
                print("✅ Completado con éxito parcial (solo texto)")
                return result
            
            result["image_prompt"] = image_prompt
            print(f"✅ Prompt de imagen generado: {image_prompt[:100]}...")
            
            # Paso 4: Generar imagen
            if status_callback:
                status_callback("🖼️ Generando imagen con ComfyUI...")
            
            print("\n🖼️ PASO 4: Generando imagen...")
            image_data, image_status = self.generate_image(image_prompt)
            result["steps"].append({
                "step": "generate_image",
                "status": "success" if image_data else "error",
                "details": image_status,
                "timestamp": datetime.now().isoformat()
            })
            
            if not image_data:
                # Podemos continuar sin imagen si falla este paso
                result["image_error"] = image_status
                result["success"] = True  # Éxito parcial (tenemos contenido)
                print(f"⚠️ Error generando imagen: {image_status}")
                print("✅ Completado con éxito parcial (solo texto)")
                return result
            
            result["image_data"] = image_data
            
            # Añadir información de imagen para fácil acceso
            if image_data.get('local_path'):
                result["image_path"] = image_data["local_path"]
            if image_data.get('filename'):
                result["image_filename"] = image_data["filename"]
            
            result["success"] = True
            
            print("✅ Contenido visual generado completamente")
            if result.get("image_path"):
                print(f"📂 Imagen guardada en: {result['image_path']}")
            
            if status_callback:
                status_callback("✅ ¡Contenido visual generado con éxito!")
            
            return result
            
        except Exception as e:
            error_msg = f"Error inesperado en generate_complete_content: {str(e)}"
            result["error"] = error_msg
            print(f"❌ {error_msg}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return result
    
    def extract_keywords(self, content: str, topic: str) -> List[str]:
        """Extrae palabras clave del contenido para búsqueda de imágenes alternativa
        
        Args:
            content (str): Contenido de texto generado
            topic (str): Tema principal
            
        Returns:
            List[str]: Lista de palabras clave
        """
        print(f"🔍 Extrayendo palabras clave...")
        print(f"   Contenido: {content[:100]}...")
        print(f"   Tema: {topic}")
        
        try:
            keywords, status = self.lmstudio_generator.analyze_content_for_keywords(content, topic)
            if keywords:
                print(f"✅ Palabras clave extraídas: {keywords}")
                return keywords
            else:
                print(f"⚠️ No se pudieron extraer palabras clave: {status}")
                return []
        except Exception as e:
            print(f"❌ Error extrayendo palabras clave: {e}")
            return []
    
    def get_workflow_info(self) -> Dict[str, Any]:
        """Obtiene información sobre el workflow actual
        
        Returns:
            Dict[str, Any]: Información del workflow
        """
        info = {
            "workflow_file": self.workflow_file,
            "workflow_loaded": self.workflow_data is not None,
            "workflow_valid": False,
            "nodes_count": 0,
            "format": "unknown"
        }
        
        if self.workflow_data:
            info["workflow_valid"] = True
            
            if isinstance(self.workflow_data, dict):
                if "nodes" in self.workflow_data:
                    nodes = self.workflow_data["nodes"]
                    if isinstance(nodes, dict):
                        info["format"] = "api"
                        info["nodes_count"] = len(nodes)
                    elif isinstance(nodes, list):
                        info["format"] = "ui"
                        info["nodes_count"] = len(nodes)
                else:
                    # Posiblemente es directamente el diccionario de nodos
                    info["format"] = "api_direct"
                    info["nodes_count"] = len(self.workflow_data)
        
        return info
    
    def reload_workflow(self, workflow_file: str = None) -> bool:
        """Recarga el workflow desde archivo
        
        Args:
            workflow_file (str, optional): Nueva ruta de archivo (usa la actual si no se proporciona)
            
        Returns:
            bool: True si se recargó correctamente
        """
        if workflow_file:
            self.workflow_file = workflow_file
        
        if not self.workflow_file:
            print("❌ No hay archivo de workflow especificado")
            return False
        
        print(f"🔄 Recargando workflow desde: {self.workflow_file}")
        
        try:
            self._load_and_validate_workflow()
            success = self.workflow_data is not None
            
            if success:
                print("✅ Workflow recargado correctamente")
            else:
                print("❌ Error al recargar workflow")
            
            return success
            
        except Exception as e:
            print(f"❌ Excepción al recargar workflow: {e}")
            return False
    
    def __str__(self) -> str:
        """Representación en string del agente"""
        workflow_info = self.get_workflow_info()
        services = self.check_services()
        
        return f"""ContentVisualAgent:
  LM Studio: {'✅' if services.get('lmstudio') else '❌'}
  ComfyUI: {'✅' if services.get('comfyui') else '❌'}
  Workflow: {'✅' if workflow_info['workflow_loaded'] else '❌'} ({workflow_info['format']}, {workflow_info['nodes_count']} nodos)
  Output Dir: {self.comfyui_generator.output_dir}"""