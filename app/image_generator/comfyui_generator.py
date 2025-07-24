# app/image_generator/comfyui_generator.py
import requests
import json
import time
import os
import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

class ComfyUIGenerator:
    """Generador de imágenes usando ComfyUI - Versión completamente corregida"""
    
    def __init__(self, base_url="http://127.0.0.1:8000", output_dir="images_generated"):
        """Inicializa el generador de ComfyUI
        
        Args:
            base_url (str): URL base de la API de ComfyUI
            output_dir (str): Directorio donde se guardarán las imágenes generadas
        """
        self.base_url = base_url
        self.client_id = f"loki_{int(time.time())}"
        self.output_dir = output_dir
        
        # Crear directorio de salida si no existe
        os.makedirs(self.output_dir, exist_ok=True)
        
        print(f"✅ ComfyUIGenerator inicializado")
        print(f"   Base URL: {self.base_url}")
        print(f"   Client ID: {self.client_id}")
        print(f"   Output Dir: {self.output_dir}")
    
    def check_server_status(self) -> bool:
        """Verifica si el servidor de ComfyUI está en funcionamiento"""
        try:
            print("🔍 Verificando estado del servidor ComfyUI...")
            response = requests.get(f"{self.base_url}/system_stats", timeout=10)
            if response.status_code == 200:
                print("✅ Servidor ComfyUI disponible")
                return True
            else:
                print(f"❌ Servidor responde con código {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Error al conectar con ComfyUI: {e}")
            return False
        except Exception as e:
            print(f"❌ Error inesperado verificando servidor: {e}")
            return False
    
    def load_workflow(self, workflow_file: str) -> Optional[Dict[str, Any]]:
        """Carga un flujo de trabajo desde un archivo JSON
        
        Args:
            workflow_file (str): Ruta al archivo JSON del flujo de trabajo
            
        Returns:
            dict: El flujo de trabajo cargado como un diccionario
        """
        print(f"📂 Cargando workflow desde: {workflow_file}")
        
        if not os.path.exists(workflow_file):
            print(f"❌ ERROR: El archivo no existe: {workflow_file}")
            return None
            
        try:
            with open(workflow_file, 'r', encoding='utf-8') as f:
                workflow_data = json.load(f)
            
            print(f"✅ Workflow cargado exitosamente")
            self._log_workflow_info(workflow_data)
            
            return workflow_data
            
        except json.JSONDecodeError as e:
            print(f"❌ Error al parsear JSON: {e}")
            return None
        except Exception as e:
            print(f"❌ Error al cargar workflow: {e}")
            return None
    
    def _log_workflow_info(self, workflow_data: Dict[str, Any]):
        """Registra información del workflow para debugging"""
        if isinstance(workflow_data.get('nodes'), list):
            print(f"📊 Formato: UI (array de nodos)")
            print(f"📊 Número de nodos: {len(workflow_data['nodes'])}")
        elif isinstance(workflow_data.get('nodes'), dict):
            print(f"📊 Formato: API (diccionario de nodos)")
            print(f"📊 Número de nodos: {len(workflow_data['nodes'])}")
        else:
            # Es directamente el diccionario de nodos
            if isinstance(workflow_data, dict) and all(
                isinstance(v, dict) and 'class_type' in v 
                for v in workflow_data.values() if isinstance(v, dict)
            ):
                print(f"📊 Formato: API directo (diccionario de nodos)")
                print(f"📊 Número de nodos: {len(workflow_data)}")
    
    def convert_ui_to_api_format(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convierte workflow de formato UI a formato API"""
        # Si no tiene nodos o ya está en formato API, devolverlo tal como está
        if 'nodes' not in workflow_data:
            # Probablemente ya es el diccionario de nodos directamente
            return {"nodes": workflow_data}
        
        if isinstance(workflow_data['nodes'], dict):
            # Ya está en formato API
            return workflow_data
        
        if not isinstance(workflow_data['nodes'], list):
            print("❌ Formato de nodos no reconocido")
            return workflow_data
        
        print("🔄 Convirtiendo workflow de formato UI a formato API...")
        
        api_nodes = {}
        
        # Convertir cada nodo del array al formato API
        for node in workflow_data['nodes']:
            node_id = str(node['id'])
            
            # Crear estructura básica del nodo para API
            api_node = {
                "class_type": node['type'],
                "inputs": {}
            }
            
            # Procesar widgets_values según el tipo de nodo
            if 'widgets_values' in node and node['widgets_values']:
                self._process_widgets_values(api_node, node)
            
            # Procesar las conexiones de entrada
            if 'inputs' in node:
                self._process_input_connections(api_node, node, workflow_data.get('links', []))
            
            api_nodes[node_id] = api_node
        
        print(f"✅ Conversión completada. Nodos procesados: {len(api_nodes)}")
        return {"nodes": api_nodes}
    
    def _process_widgets_values(self, api_node: Dict[str, Any], ui_node: Dict[str, Any]):
        """Procesa widgets_values según el tipo de nodo"""
        node_type = ui_node['type']
        widgets_values = ui_node['widgets_values']
        
        if node_type == 'CLIPTextEncode':
            # Para CLIPTextEncode, el primer widget_value es el texto
            api_node["inputs"]["text"] = widgets_values[0] if widgets_values else ""
        
        elif node_type == 'CheckpointLoaderSimple':
            # Para CheckpointLoaderSimple, el primer widget_value es el nombre del checkpoint
            api_node["inputs"]["ckpt_name"] = widgets_values[0] if widgets_values else ""
        
        elif node_type == 'EmptyLatentImage':
            # Para EmptyLatentImage: [width, height, batch_size]
            if len(widgets_values) >= 3:
                api_node["inputs"]["width"] = widgets_values[0]
                api_node["inputs"]["height"] = widgets_values[1]
                api_node["inputs"]["batch_size"] = widgets_values[2]
        
        elif node_type == 'KSampler':
            # Para KSampler: [seed, randomize, steps, cfg, sampler_name, scheduler, denoise]
            if len(widgets_values) >= 7:
                api_node["inputs"]["seed"] = widgets_values[0]
                api_node["inputs"]["steps"] = widgets_values[2]
                api_node["inputs"]["cfg"] = widgets_values[3]
                api_node["inputs"]["sampler_name"] = widgets_values[4]
                api_node["inputs"]["scheduler"] = widgets_values[5]
                api_node["inputs"]["denoise"] = widgets_values[6]
        
        elif node_type == 'SaveImage':
            # Para SaveImage: [filename_prefix]
            api_node["inputs"]["filename_prefix"] = widgets_values[0] if widgets_values else "ComfyUI"
        
        else:
            # Para otros tipos de nodos, mantener widgets_values como está
            if widgets_values:
                api_node["inputs"]["widgets_values"] = widgets_values
    
    def _process_input_connections(self, api_node: Dict[str, Any], ui_node: Dict[str, Any], links: List):
        """Procesa las conexiones de entrada del nodo"""
        if 'inputs' not in ui_node:
            return
        
        for input_conn in ui_node['inputs']:
            if 'link' not in input_conn or input_conn['link'] is None:
                continue
            
            link_id = input_conn['link']
            input_name = input_conn['name']
            
            # Buscar el link correspondiente
            for link in links:
                if link[0] == link_id:
                    source_node_id = str(link[1])
                    source_output_index = link[2]
                    api_node["inputs"][input_name] = [source_node_id, source_output_index]
                    break
    
    def update_prompt_in_workflow(self, workflow_data: Dict[str, Any], new_prompt: str) -> Dict[str, Any]:
        """Actualiza el prompt en el workflow (maneja todos los formatos)"""
        print(f"🔄 Actualizando prompt en el workflow...")
        print(f"📝 Nuevo prompt: {new_prompt[:100]}...")
        
        # Detectar y convertir formato si es necesario
        if isinstance(workflow_data.get('nodes'), list):
            print("🔄 Detectado formato UI, convirtiendo a API...")
            workflow_data = self.convert_ui_to_api_format(workflow_data)
        
        # Obtener nodos del workflow
        if 'nodes' in workflow_data:
            nodes = workflow_data['nodes']
        else:
            # Asumir que workflow_data ya es el diccionario de nodos
            nodes = workflow_data
            workflow_data = {"nodes": nodes}
        
        # Buscar y actualizar nodos CLIPTextEncode
        updated = False
        for node_id, node_data in nodes.items():
            if node_data.get('class_type') == 'CLIPTextEncode':
                current_text = node_data.get('inputs', {}).get('text', '')
                
                print(f"🔍 Nodo {node_id} - Texto actual: '{current_text[:50]}...'")
                
                # Solo actualizar si no es un prompt negativo
                if not self._is_negative_prompt(current_text):
                    print(f"✅ Actualizando prompt en nodo {node_id}")
                    node_data['inputs']['text'] = new_prompt
                    updated = True
                    break
                else:
                    print(f"⏭️ Nodo {node_id} es prompt negativo, omitiendo")
        
        if updated:
            print("✅ Prompt actualizado exitosamente")
        else:
            print("⚠️ No se encontró nodo de prompt positivo para actualizar")
        
        return workflow_data
    
    def _is_negative_prompt(self, text: str) -> bool:
        """Determina si un texto es un prompt negativo"""
        if not text:
            return False
        
        negative_indicators = [
            'text', 'watermark', 'bad quality', 'blurry', 
            'low quality', 'worst quality', 'low resolution',
            'bad anatomy', 'bad hands', 'missing fingers',
            'deformed', 'ugly', 'poorly drawn', 'distorted'
        ]
        
        text_lower = text.lower().strip()
        return any(indicator in text_lower for indicator in negative_indicators)
    
    def validate_workflow(self, workflow_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Valida que el workflow tenga la estructura correcta para la API"""
        if 'nodes' not in workflow_data:
            return False, "El workflow no contiene nodos"
        
        nodes = workflow_data['nodes']
        
        if isinstance(nodes, list):
            return False, "El workflow está en formato UI, necesita conversión"
        
        if not isinstance(nodes, dict):
            return False, "Los nodos no están en formato de diccionario"
        
        for node_id, node_data in nodes.items():
            if not isinstance(node_data, dict):
                return False, f"Nodo {node_id} no es un diccionario"
            
            if 'class_type' not in node_data:
                return False, f"Nodo {node_id} no tiene class_type"
            
            if 'inputs' not in node_data:
                return False, f"Nodo {node_id} no tiene inputs"
            
            if node_id.startswith('#'):
                return False, f"ID de nodo inválido: {node_id}"
        
        return True, "Workflow válido"
    
    def queue_prompt(self, workflow_data: Dict[str, Any]) -> str:
        """Envía el workflow a la cola de ComfyUI"""
        print("📤 Enviando workflow a la cola de ComfyUI...")
        
        # Validar workflow antes de enviar
        is_valid, message = self.validate_workflow(workflow_data)
        if not is_valid:
            print(f"❌ Workflow inválido: {message}")
            
            # Intentar convertir si es necesario
            if isinstance(workflow_data.get('nodes'), list):
                print("🔄 Intentando conversión automática...")
                workflow_data = self.convert_ui_to_api_format(workflow_data)
                
                # Validar nuevamente después de la conversión
                is_valid, message = self.validate_workflow(workflow_data)
                if not is_valid:
                    raise ValueError(f"Workflow inválido después de conversión: {message}")
            else:
                raise ValueError(f"Workflow inválido: {message}")
        
        self.client_id = f"loki_{int(time.time())}"
        
        # Preparar payload para ComfyUI
        prompt_data = {
            "prompt": workflow_data['nodes'],
            "client_id": self.client_id
        }
        
        try:
            print(f"🆔 Client ID: {self.client_id}")
            print(f"📊 Número de nodos: {len(workflow_data['nodes'])}")
            
            # Mostrar estructura del workflow
            print("\n📋 Estructura del workflow:")
            for node_id, node_data in workflow_data['nodes'].items():
                class_type = node_data.get('class_type', 'Unknown')
                print(f"  • Nodo {node_id}: {class_type}")
                
                # Mostrar información adicional para nodos importantes
                if class_type == 'CLIPTextEncode':
                    text = node_data.get('inputs', {}).get('text', '')
                    text_preview = (text[:50] + "...") if len(text) > 50 else text
                    print(f"    └─ Texto: '{text_preview}'")
                elif class_type == 'CheckpointLoaderSimple':
                    ckpt = node_data.get('inputs', {}).get('ckpt_name', '')
                    print(f"    └─ Checkpoint: {ckpt}")
            
            print(f"\n📡 Enviando solicitud POST a {self.base_url}/prompt")
            
            response = requests.post(
                f"{self.base_url}/prompt",
                json=prompt_data,
                timeout=30
            )
            
            print(f"📨 Respuesta recibida. Status code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                prompt_id = result.get('prompt_id')
                print(f"✅ Prompt enviado exitosamente. ID: {prompt_id}")
                return prompt_id
            else:
                error_detail = response.text
                print(f"❌ ERROR: Status code {response.status_code}")
                print(f"📄 Respuesta: {error_detail}")
                raise ValueError(f"Error al enviar el prompt: {error_detail}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
            raise ValueError(f"Error de conexión con ComfyUI: {e}")
        except Exception as e:
            print(f"❌ ERROR inesperado en queue_prompt: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            raise ValueError(f"Error al enviar el prompt: {e}")
    
    def wait_for_completion(self, prompt_id: str, timeout: int = 300) -> bool:
        """Espera a que se complete la generación"""
        print(f"⏳ Esperando completación del prompt {prompt_id}...")
        start_time = time.time()
        last_check = 0
        
        while time.time() - start_time < timeout:
            try:
                # Mostrar progreso cada 10 segundos
                if time.time() - last_check > 10:
                    elapsed = int(time.time() - start_time)
                    print(f"⌛ Esperando... ({elapsed}s transcurridos)")
                    last_check = time.time()
                
                response = requests.get(f"{self.base_url}/history/{prompt_id}", timeout=10)
                if response.status_code == 200:
                    history = response.json()
                    if prompt_id in history:
                        print("✅ Generación completada")
                        return True
                
                time.sleep(2)
                
            except Exception as e:
                print(f"⚠️ Error verificando estado: {e}")
                time.sleep(5)
        
        print(f"⏰ Timeout después de {timeout} segundos")
        return False
    
    def get_generated_images(self, prompt_id: str) -> List[Dict[str, Any]]:
        """Obtiene las imágenes generadas"""
        try:
            print(f"📸 Obteniendo imágenes generadas para prompt {prompt_id}...")
            
            response = requests.get(f"{self.base_url}/history/{prompt_id}")
            if response.status_code != 200:
                print(f"❌ Error obteniendo historial: {response.status_code}")
                return []
            
            history = response.json()
            if prompt_id not in history:
                print(f"❌ Prompt {prompt_id} no encontrado en historial")
                return []
            
            outputs = history[prompt_id].get('outputs', {})
            images = []
            
            for node_id, output in outputs.items():
                if 'images' in output:
                    for image_info in output['images']:
                        image_data = {
                            'filename': image_info['filename'],
                            'subfolder': image_info.get('subfolder', ''),
                            'type': image_info.get('type', 'output'),
                            'node_id': node_id
                        }
                        images.append(image_data)
                        print(f"✅ Imagen encontrada: {image_data['filename']}")
            
            print(f"📊 Total de imágenes encontradas: {len(images)}")
            return images
            
        except Exception as e:
            print(f"❌ Error obteniendo imágenes: {e}")
            return []
    
    def download_image(self, image_info: Dict[str, Any]) -> Optional[str]:
        """Descarga una imagen y la guarda localmente"""
        try:
            filename = image_info['filename']
            subfolder = image_info.get('subfolder', '')
            img_type = image_info.get('type', 'output')
            
            # Construir URL de descarga
            if subfolder:
                image_url = f"{self.base_url}/view?filename={filename}&subfolder={subfolder}&type={img_type}"
            else:
                image_url = f"{self.base_url}/view?filename={filename}&type={img_type}"
            
            print(f"📥 Descargando imagen: {filename}")
            
            response = requests.get(image_url, timeout=30)
            if response.status_code == 200:
                # Generar nombre local único
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                local_filename = f"comfyui_{timestamp}.png"
                local_path = os.path.join(self.output_dir, local_filename)
                
                # Guardar archivo
                with open(local_path, "wb") as f:
                    f.write(response.content)
                
                print(f"✅ Imagen guardada: {local_path}")
                return local_path
            else:
                print(f"❌ Error descargando imagen: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error descargando imagen: {e}")
            return None
    
    def generate_image(self, prompt: str, workflow_file: str = None, workflow_data: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Genera una imagen a partir de un prompt de texto
        
        Args:
            prompt (str): El prompt de texto para generar la imagen
            workflow_file (str, optional): Ruta al archivo JSON del flujo de trabajo
            workflow_data (dict, optional): Datos del flujo de trabajo ya cargados
            
        Returns:
            dict: Información de la imagen generada
        """
        print("\n" + "="*80)
        print("🎨 INICIANDO GENERACIÓN DE IMAGEN CON COMFYUI")
        print(f"📝 Prompt: {prompt[:100]}...")
        if workflow_file:
            print(f"📄 Workflow file: {workflow_file}")
        if workflow_data:
            print("📄 Workflow data: Proporcionado")
        print("="*80)
        
        try:
            # 1. Verificar servidor
            if not self.check_server_status():
                raise ValueError("Servidor ComfyUI no disponible")
            
            # 2. Cargar o usar workflow
            if workflow_data is None and workflow_file:
                workflow_data = self.load_workflow(workflow_file)
                if not workflow_data:
                    raise ValueError("No se pudo cargar el workflow")
            elif workflow_data is None:
                raise ValueError("Debe proporcionar workflow_file o workflow_data")
            else:
                print("✅ Usando workflow proporcionado")
                self._log_workflow_info(workflow_data)
            
            # 3. Actualizar prompt
            updated_workflow = self.update_prompt_in_workflow(workflow_data, prompt)
            
            # 4. Enviar a cola
            prompt_id = self.queue_prompt(updated_workflow)
            
            # 5. Esperar completación
            if not self.wait_for_completion(prompt_id):
                raise ValueError("Timeout esperando completación")
            
            # 6. Obtener imágenes
            images = self.get_generated_images(prompt_id)
            if not images:
                raise ValueError("No se generaron imágenes")
            
            # 7. Descargar primera imagen
            local_path = None
            if images:
                local_path = self.download_image(images[0])
            
            result = {
                'prompt_id': prompt_id,
                'images': images,
                'local_path': local_path,
                'filename': images[0]['filename'] if images else None,
                'status': 'success',
                'message': f'Generación completada exitosamente con {len(images)} imagen(es)'
            }
            
            print(f"✅ Generación exitosa. Imágenes: {len(images)}")
            if local_path:
                print(f"📂 Imagen guardada en: {local_path}")
            
            return result
            
        except Exception as e:
            print(f"❌ ERROR en generate_image: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            
            return {
                'error': str(e),
                'status': 'failed',
                'prompt_id': None,
                'images': [],
                'local_path': None,
                'filename': None
            }