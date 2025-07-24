# app/image_generator/comfyui_generator.py
import requests
import json
import time
import os
import base64
from datetime import datetime
from pathlib import Path

class ComfyUIGenerator:
    """Clase para interactuar con ComfyUI para generar imágenes a partir de texto"""
    
    def __init__(self, base_url="http://127.0.0.1:8000", output_dir="images_generated"):
        """Inicializa el generador de ComfyUI
        
        Args:
            base_url (str): URL base de la API de ComfyUI
            output_dir (str): Directorio donde se guardarán las imágenes generadas
        """
        self.base_url = base_url
        self.client_id = self._get_client_id()
        self.output_dir = output_dir
        
        # Crear directorio de salida si no existe
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _get_client_id(self):
        """Obtiene un ID de cliente único para la sesión"""
        return f"loki_{int(time.time())}"
    
    def check_server_status(self):
        """Verifica si el servidor de ComfyUI está en funcionamiento
        
        Returns:
            bool: True si el servidor está activo, False en caso contrario
        """
        try:
            response = requests.get(f"{self.base_url}/system_stats", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def load_workflow(self, workflow_file):
        """Carga un flujo de trabajo desde un archivo JSON
        
        Args:
            workflow_file (str): Ruta al archivo JSON del flujo de trabajo
            
        Returns:
            dict: El flujo de trabajo cargado como un diccionario
        """
        print(f"Cargando flujo de trabajo desde archivo: {workflow_file}")
        
        if not os.path.exists(workflow_file):
            print(f"ERROR: El archivo de flujo de trabajo no existe: {workflow_file}")
            raise FileNotFoundError(f"El archivo de flujo de trabajo no existe: {workflow_file}")
            
        try:
            with open(workflow_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"Contenido leído del archivo. Tamaño: {len(content)} caracteres")
                
                try:
                    workflow = json.loads(content)
                    print(f"JSON cargado correctamente. Tipo: {type(workflow)}")
                    
                    # Validar que el workflow es un diccionario
                    if not isinstance(workflow, dict):
                        print(f"ERROR: El contenido del archivo no es un diccionario JSON válido, es {type(workflow)}")
                        print(f"Primeros 100 caracteres del contenido: {content[:100]}...")
                        raise ValueError(f"El flujo de trabajo debe ser un diccionario JSON, no {type(workflow)}")
                    
                    # Validar que el workflow tiene la estructura esperada
                    if "nodes" not in workflow:
                        print(f"ADVERTENCIA: El flujo de trabajo no contiene la clave 'nodes'")
                        print(f"Claves disponibles: {list(workflow.keys())}")
                    else:
                        # Verificar si nodes es un diccionario y convertirlo si es necesario
                        if not isinstance(workflow["nodes"], dict):
                            print(f"ADVERTENCIA: workflow['nodes'] no es un diccionario, es {type(workflow['nodes'])}")
                            
                            # Intentar convertir nodes a un diccionario si es una lista
                            if isinstance(workflow["nodes"], list):
                                print(f"Intentando convertir workflow['nodes'] de lista a diccionario...")
                                try:
                                    # Crear un diccionario a partir de la lista, usando índices como claves
                                    nodes_dict = {}
                                    for i, node in enumerate(workflow["nodes"]):
                                        if isinstance(node, dict) and "id" in node:
                                            # Si el nodo tiene un ID, usarlo como clave STRING
                                            nodes_dict[str(node["id"])] = node
                                            print(f"Nodo con ID {node['id']} convertido a clave string '{str(node['id'])}' en el diccionario")
                                        else:
                                            # Si no tiene ID, usar el índice como clave
                                            nodes_dict[str(i)] = node
                                            print(f"Nodo sin ID en posición {i} añadido con clave '{str(i)}' al diccionario")
                                    
                                    print(f"Conversión exitosa: {len(nodes_dict)} nodos convertidos")
                                    print(f"Claves en el diccionario: {list(nodes_dict.keys())}")
                                    workflow["nodes"] = nodes_dict
                                except Exception as e:
                                    print(f"ERROR al convertir nodes de lista a diccionario: {str(e)}")
                                    print(f"Continuando con el workflow original...")
                            else:
                                print(f"ADVERTENCIA: workflow['nodes'] no es ni un diccionario ni una lista, es {type(workflow['nodes'])}")
                    
                    return workflow
                    
                except json.JSONDecodeError as e:
                    print(f"ERROR: El archivo no contiene JSON válido: {str(e)}")
                    print(f"Primeros 100 caracteres del contenido: {content[:100]}...")
                    raise ValueError(f"El archivo no contiene JSON válido: {str(e)}")
                    
        except Exception as e:
            print(f"ERROR al cargar el flujo de trabajo: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            raise ValueError(f"Error al cargar el flujo de trabajo: {str(e)}")
    
    def _find_prompt_node(self, workflow):
        """Encuentra el nodo de prompt en el flujo de trabajo
        
        Args:
            workflow (dict): El flujo de trabajo de ComfyUI
            
        Returns:
            tuple: (node_id, location) del nodo de prompt, donde location puede ser un índice de widget o un nombre de input
        """
        print(f"Buscando nodo de prompt en el flujo de trabajo. Tipo de workflow: {type(workflow)}")
        
        if not isinstance(workflow, dict):
            print(f"ERROR: El flujo de trabajo no es un diccionario, es {type(workflow)}")
            print(f"Contenido del workflow: {workflow}")
            raise ValueError(f"El flujo de trabajo debe ser un diccionario, no {type(workflow)}")
        
        if "nodes" not in workflow:
            print(f"ERROR: El flujo de trabajo no contiene la clave 'nodes'")
            print(f"Claves disponibles: {list(workflow.keys())}")
            raise ValueError("El flujo de trabajo no contiene la clave 'nodes'")
        
        # Verificar si nodes es un diccionario
        if not isinstance(workflow["nodes"], dict):
            print(f"ERROR: workflow['nodes'] no es un diccionario, es {type(workflow['nodes'])}")
            print(f"Contenido de nodes: {workflow['nodes']}")
            raise ValueError(f"El flujo de trabajo debe tener 'nodes' como diccionario, no {type(workflow['nodes'])}")
            
        # Primero buscar en CLIPTextEncode con widgets_values
        # Asegurarse de que workflow["nodes"] es un diccionario antes de iterar
        if not isinstance(workflow["nodes"], dict):
            # Si llegamos aquí, significa que la validación anterior no lanzó una excepción
            # Intentar convertir a diccionario para continuar
            try:
                nodes_dict = {}
                if isinstance(workflow["nodes"], list):
                    for i, node in enumerate(workflow["nodes"]):
                        if isinstance(node, dict) and "id" in node:
                            nodes_dict[node["id"]] = node
                        else:
                            nodes_dict[str(i)] = node
                    workflow["nodes"] = nodes_dict
                    print(f"Convertido workflow['nodes'] de lista a diccionario con {len(nodes_dict)} elementos")
                else:
                    # Si no es lista ni diccionario, crear un diccionario vacío
                    workflow["nodes"] = {}
                    print(f"Creado diccionario vacío para workflow['nodes']")
            except Exception as e:
                print(f"ERROR al convertir workflow['nodes']: {str(e)}")
                # Continuar con un diccionario vacío
                workflow["nodes"] = {}
        
        for node_id, node in workflow.get("nodes", {}).items():
            print(f"Analizando nodo {node_id}, tipo: {node.get('type')}")
            
            if node.get("type") == "CLIPTextEncode":
                # Primero buscar en widgets_values (más común en flujos de trabajo exportados)
                if "widgets_values" in node and isinstance(node["widgets_values"], list):
                    print(f"Nodo {node_id} tiene widgets_values: {node['widgets_values']}")
                    for i, value in enumerate(node["widgets_values"]):
                        if isinstance(value, str) and len(value) > 5:  # Probablemente un prompt
                            print(f"Encontrado prompt en widgets_values[{i}]: {value[:30]}...")
                            # Devolver el ID del nodo como está en el diccionario (clave)
                            return node_id, i
                
                # Luego buscar en inputs (más común en flujos de trabajo API)
                if "inputs" in node and isinstance(node["inputs"], dict):
                    print(f"Nodo {node_id} tiene inputs: {node['inputs']}")
                    for input_name, input_value in node["inputs"].items():
                        if input_name == "text" and isinstance(input_value, str):
                            print(f"Encontrado prompt en input '{input_name}': {input_value[:30]}...")
                            # Devolver el ID del nodo como está en el diccionario (clave)
                            return node_id, input_name
        
        # Búsqueda general de cualquier nodo con un valor de texto largo en widgets_values
        print("No se encontró nodo CLIPTextEncode con prompt, buscando en cualquier nodo...")
        # No necesitamos verificar de nuevo si workflow["nodes"] es un diccionario
        # ya que lo hicimos en la primera iteración
        for node_id, node in workflow.get("nodes", {}).items():
            if "widgets_values" in node and isinstance(node["widgets_values"], list):
                for i, value in enumerate(node["widgets_values"]):
                    if isinstance(value, str) and len(value) > 20:  # Probablemente un prompt
                        print(f"Encontrado posible prompt en nodo {node_id}, widgets_values[{i}]: {value[:30]}...")
                        # Devolver el ID del nodo como está en el diccionario (clave)
                        return node_id, i
        
        print("No se encontró ningún nodo con prompt en el flujo de trabajo")
        return None, None
    
    def update_prompt(self, workflow, prompt):
        """Actualiza el prompt en el flujo de trabajo
        
        Args:
            workflow (dict): El flujo de trabajo de ComfyUI
            prompt (str): El nuevo prompt a utilizar
            
        Returns:
            dict: El flujo de trabajo actualizado
        """
        print(f"Actualizando prompt en el flujo de trabajo. Nuevo prompt: {prompt[:50]}...")
        
        try:
            node_id, location = self._find_prompt_node(workflow)
            
            if node_id is None or location is None:
                print("ERROR: No se encontró un nodo de prompt en el flujo de trabajo")
                raise ValueError("No se encontró un nodo de prompt en el flujo de trabajo")
            
            print(f"Nodo encontrado: {node_id}, Ubicación: {location} (tipo: {type(location)})")
            
            # Crear una copia del flujo de trabajo para no modificar el original
            updated_workflow = json.loads(json.dumps(workflow))
            
            # Verificar si el nodo existe en el diccionario
            if node_id not in updated_workflow["nodes"]:
                print(f"ERROR: El nodo con ID {node_id} no existe en el diccionario de nodos")
                print(f"IDs disponibles: {list(updated_workflow['nodes'].keys())}")
                
                # Intentar convertir el ID numérico a string si es necesario
                str_node_id = str(node_id)
                if str_node_id in updated_workflow["nodes"]:
                    print(f"Encontrado nodo con ID string '{str_node_id}', usando este ID")
                    node_id = str_node_id
                else:
                    # Buscar el nodo por su ID numérico en los valores
                    found = False
                    for key, node in updated_workflow["nodes"].items():
                        if isinstance(node, dict) and node.get("id") == node_id:
                            print(f"Encontrado nodo con ID {node_id} usando la clave {key}")
                            node_id = key
                            found = True
                            break
                    
                    if not found:
                        print(f"ERROR: No se pudo encontrar el nodo con ID {node_id}")
                        raise ValueError(f"No se pudo encontrar el nodo con ID {node_id}")
            
            # Actualizar el prompt según el tipo de ubicación encontrada
            if isinstance(location, int):  # Es un índice de widget
                print(f"Actualizando prompt en widgets_values[{location}]")
                
                if "widgets_values" not in updated_workflow["nodes"][node_id]:
                    print(f"Creando lista widgets_values en nodo {node_id}")
                    updated_workflow["nodes"][node_id]["widgets_values"] = []
                
                # Asegurarse de que hay suficientes elementos en la lista
                while len(updated_workflow["nodes"][node_id]["widgets_values"]) <= location:
                    updated_workflow["nodes"][node_id]["widgets_values"].append("")
                    
                print(f"Estado de widgets_values antes de actualizar: {updated_workflow['nodes'][node_id]['widgets_values']}")
                
                # Actualizar el prompt en widgets_values
                try:
                    updated_workflow["nodes"][node_id]["widgets_values"][location] = prompt
                    print(f"Prompt actualizado en nodo {node_id}, widget_index {location}")
                except Exception as e:
                    print(f"ERROR al actualizar widgets_values[{location}]: {str(e)}")
                    print(f"Tipo de widgets_values: {type(updated_workflow['nodes'][node_id]['widgets_values'])}")
                    print(f"Contenido de widgets_values: {updated_workflow['nodes'][node_id]['widgets_values']}")
                    raise ValueError(f"Error al actualizar el prompt en widgets_values: {str(e)}")
            else:  # Es un nombre de input
                # Actualizar el prompt en inputs
                try:
                    if "inputs" not in updated_workflow["nodes"][node_id]:
                        print(f"Creando diccionario inputs en nodo {node_id}")
                        updated_workflow["nodes"][node_id]["inputs"] = {}
                    
                    updated_workflow["nodes"][node_id]["inputs"][location] = prompt
                    print(f"Prompt actualizado en nodo {node_id}, input {location}")
                except Exception as e:
                    print(f"ERROR al actualizar inputs[{location}]: {str(e)}")
                    print(f"Tipo de inputs: {type(updated_workflow['nodes'][node_id].get('inputs', 'No existe'))}")
                    print(f"Contenido de inputs: {updated_workflow['nodes'][node_id].get('inputs', 'No existe')}")
                    raise ValueError(f"Error al actualizar el prompt en inputs: {str(e)}")
            
            return updated_workflow
            
        except Exception as e:
            print(f"ERROR GENERAL en update_prompt: {str(e)}")
            print(f"Tipo de workflow: {type(workflow)}")
            if isinstance(workflow, dict):
                print(f"Claves en workflow: {list(workflow.keys())}")
                if "nodes" in workflow:
                    print(f"Número de nodos: {len(workflow['nodes'])}")
                    # Verificar si nodes es un diccionario antes de usar values()
                    if isinstance(workflow['nodes'], dict):
                        print(f"Tipos de nodos: {[node.get('type', 'desconocido') for node in workflow['nodes'].values()]}")
                    else:
                        print(f"ADVERTENCIA: workflow['nodes'] no es un diccionario, es {type(workflow['nodes'])}")
                        print(f"Contenido de nodes: {workflow['nodes']}")
            raise
    
    def queue_prompt(self, workflow):
        """Envía un flujo de trabajo a la cola de ComfyUI
        
        Args:
            workflow (dict): El flujo de trabajo a enviar
            
        Returns:
            str: El ID del prompt en la cola
        """
        print(f"Enviando flujo de trabajo a la cola de ComfyUI...")
        
        if not isinstance(workflow, dict):
            print(f"ERROR: El flujo de trabajo no es un diccionario, es {type(workflow)}")
            print(f"Contenido del workflow: {workflow}")
            raise ValueError(f"El flujo de trabajo debe ser un diccionario, no {type(workflow)}")
        
        try:
            prompt_payload = {
                "prompt": workflow,
                "client_id": self.client_id
            }
            
            print(f"Enviando solicitud POST a {self.base_url}/prompt")
            print(f"Client ID: {self.client_id}")
            print(f"Tamaño del payload: {len(str(prompt_payload))} caracteres")
            
            response = requests.post(
                f"{self.base_url}/prompt", 
                json=prompt_payload,
                timeout=30
            )
            
            print(f"Respuesta recibida. Status code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"ERROR: Status code {response.status_code}")
                print(f"Respuesta: {response.text}")
                raise ValueError(f"Error al enviar el prompt: {response.text}")
            
            response_data = response.json()
            print(f"Respuesta JSON: {response_data}")
            
            prompt_id = response_data.get("prompt_id")
            if not prompt_id:
                print(f"ERROR: No se recibió prompt_id en la respuesta")
                print(f"Respuesta completa: {response_data}")
                raise ValueError("No se recibió prompt_id en la respuesta")
                
            print(f"Prompt ID recibido: {prompt_id}")
            return prompt_id
            
        except requests.exceptions.RequestException as e:
            print(f"ERROR de conexión: {str(e)}")
            raise ConnectionError(f"Error de conexión con ComfyUI: {str(e)}")
        except Exception as e:
            print(f"ERROR inesperado en queue_prompt: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            raise
    
    def get_image(self, prompt_id, max_wait_time=120):
        """Espera y obtiene la imagen generada
        
        Args:
            prompt_id (str): ID del prompt en la cola
            max_wait_time (int): Tiempo máximo de espera en segundos
            
        Returns:
            dict: Información de la imagen generada incluyendo la ruta local
        """
        start_time = time.time()
        image_data = None
        
        while time.time() - start_time < max_wait_time:
            try:
                # Verificar el estado de la generación
                history_response = requests.get(
                    f"{self.base_url}/history/{prompt_id}",
                    timeout=10
                )
                
                if history_response.status_code != 200:
                    time.sleep(1)
                    continue
                
                history_data = history_response.json()
                
                # Buscar nodos de salida con imágenes
                for node_id, node_output in history_data.get(prompt_id, {}).get("outputs", {}).items():
                    if "images" in node_output:
                        for img in node_output["images"]:
                            # Obtener la imagen
                            image_data = {
                                "filename": img.get("filename"),
                                "type": img.get("type"),
                                "node_id": node_id
                            }
                            
                            # Descargar la imagen
                            image_url = f"{self.base_url}/view?filename={img.get('filename')}&type={img.get('type')}"
                            img_response = requests.get(image_url, timeout=30)
                            
                            if img_response.status_code == 200:
                                # Guardar la imagen localmente
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                local_filename = f"comfyui_{timestamp}.png"
                                local_path = os.path.join(self.output_dir, local_filename)
                                
                                with open(local_path, "wb") as f:
                                    f.write(img_response.content)
                                
                                image_data["local_path"] = local_path
                                image_data["url"] = image_url
                                return image_data
                
                # Si no hay imágenes todavía, esperar un poco
                time.sleep(2)
                
            except Exception as e:
                print(f"Error al obtener la imagen: {str(e)}")
                time.sleep(2)
        
        raise TimeoutError(f"Tiempo de espera agotado después de {max_wait_time} segundos")
    
    def generate_image(self, prompt, workflow_file=None, workflow_data=None):
        print(f"--------ESTE ES EL Prompt: {prompt}...")
        """Genera una imagen a partir de un prompt de texto
        
        Args:
            prompt (str): El prompt de texto para generar la imagen
            workflow_file (str, optional): Ruta al archivo JSON del flujo de trabajo
            workflow_data (dict, optional): Datos del flujo de trabajo ya cargados
            
        Returns:
            dict: Información de la imagen generada
        """
        print("\n" + "="*80)
        print(f"INICIANDO GENERACIÓN DE IMAGEN CON COMFYUI")
        print(f"Prompt: {prompt[:100]}...")
        print(f"Workflow file: {workflow_file}")
        print(f"Workflow data: {'Proporcionado' if workflow_data else 'No proporcionado'}")
        if workflow_data is not None:
            print(f"Tipo de workflow_data: {type(workflow_data)}")
            if isinstance(workflow_data, list):
                print(f"ADVERTENCIA: workflow_data es una lista, no un diccionario")
                print(f"Longitud de la lista: {len(workflow_data)}")
                print(f"Primeros elementos: {workflow_data[:3] if len(workflow_data) > 0 else 'Lista vacía'}")
            elif isinstance(workflow_data, dict):
                print(f"Claves en workflow_data: {list(workflow_data.keys())}")
                if "nodes" in workflow_data:
                    print(f"Número de nodos: {len(workflow_data['nodes'])}")
        print("="*80)
        
        try:
            # Verificar que el servidor esté activo
            print("Verificando estado del servidor ComfyUI...")
            if not self.check_server_status():
                print("ERROR: El servidor de ComfyUI no está disponible")
                raise ConnectionError("El servidor de ComfyUI no está disponible")
            print("✅ Servidor ComfyUI disponible")
            
            # Cargar el flujo de trabajo
            print("Cargando flujo de trabajo...")
            workflow = None
            
            if workflow_data is not None:
                print("Usando datos de flujo de trabajo proporcionados")
                print(f"Tipo de workflow_data: {type(workflow_data)}")
                
                # Si workflow_data es una lista, intentar convertirlo a diccionario
                if isinstance(workflow_data, list):
                    print(f"ADVERTENCIA: workflow_data es una lista, intentando convertir a diccionario")
                    print(f"Contenido de workflow_data: {workflow_data}")
                    
                    # Si es una lista con un solo elemento y ese elemento es un diccionario, usar ese elemento
                    if len(workflow_data) == 1 and isinstance(workflow_data[0], dict):
                        print(f"Usando el primer elemento de la lista como workflow")
                        workflow = workflow_data[0]
                    else:
                        print(f"ERROR: No se puede convertir workflow_data a diccionario")
                        raise ValueError(f"workflow_data es una lista y no se puede convertir a diccionario")
                else:
                    workflow = workflow_data
            elif workflow_file is not None:
                print(f"Cargando flujo de trabajo desde archivo: {workflow_file}")
                if not os.path.exists(workflow_file):
                    print(f"ERROR: El archivo de flujo de trabajo no existe: {workflow_file}")
                    raise FileNotFoundError(f"El archivo de flujo de trabajo no existe: {workflow_file}")
                
                workflow = self.load_workflow(workflow_file)
                print(f"Flujo de trabajo cargado desde archivo. Tipo: {type(workflow)}")
            else:
                print("ERROR: No se proporcionó ni workflow_file ni workflow_data")
                raise ValueError("Debe proporcionar un archivo de flujo de trabajo o datos de flujo de trabajo")
            
            # Validar que el workflow es un diccionario
            if not isinstance(workflow, dict):
                print(f"ERROR: El flujo de trabajo no es un diccionario, es {type(workflow)}")
                print(f"Contenido del workflow: {workflow}")
                raise ValueError(f"El flujo de trabajo debe ser un diccionario, no {type(workflow)}")
            
            # Validar que el workflow tiene la estructura esperada
            if "nodes" not in workflow:
                print(f"ADVERTENCIA: El flujo de trabajo no contiene la clave 'nodes'")
                print(f"Claves disponibles: {list(workflow.keys())}")
                if len(workflow.keys()) == 0:
                    print(f"ERROR: El flujo de trabajo está vacío")
                    raise ValueError("El flujo de trabajo está vacío")
            
            # Verificar si nodes es un diccionario y convertirlo si es necesario
            if not isinstance(workflow["nodes"], dict):
                print(f"ADVERTENCIA: workflow['nodes'] no es un diccionario, es {type(workflow['nodes'])}")
                
                # Intentar convertir nodes a un diccionario si es una lista
                if isinstance(workflow["nodes"], list):
                    print(f"Intentando convertir workflow['nodes'] de lista a diccionario...")
                    try:
                        # Crear un diccionario a partir de la lista, usando índices como claves
                        nodes_dict = {}
                        for i, node in enumerate(workflow["nodes"]):
                            if isinstance(node, dict) and "id" in node:
                                # Si el nodo tiene un ID, usarlo como clave STRING
                                nodes_dict[str(node["id"])] = node
                                print(f"Nodo con ID {node['id']} convertido a clave string '{str(node['id'])}' en el diccionario")
                            else:
                                # Si no tiene ID, usar el índice como clave
                                nodes_dict[str(i)] = node
                                print(f"Nodo sin ID en posición {i} añadido con clave '{str(i)}' al diccionario")
                        
                        print(f"Conversión exitosa: {len(nodes_dict)} nodos convertidos")
                        print(f"Claves en el diccionario: {list(nodes_dict.keys())}")
                        workflow["nodes"] = nodes_dict
                    except Exception as e:
                        print(f"ERROR al convertir nodes de lista a diccionario: {str(e)}")
                        raise ValueError(f"No se pudo convertir workflow['nodes'] de lista a diccionario: {str(e)}")
                else:
                    print(f"ERROR: workflow['nodes'] no es ni un diccionario ni una lista")
                    raise ValueError(f"El flujo de trabajo debe tener 'nodes' como diccionario, no {type(workflow['nodes'])}")
            
            print(f"Estructura de workflow['nodes'] validada: es un diccionario con {len(workflow['nodes'])} nodos")
            
            # Actualizar el prompt en el flujo de trabajo
            print("Actualizando prompt en el flujo de trabajo...")
            try:
                updated_workflow = self.update_prompt(workflow, prompt)
                print("✅ Prompt actualizado en el flujo de trabajo")
            except Exception as e:
                print(f"ERROR al actualizar el prompt: {str(e)}")
                print(f"Tipo de error: {type(e).__name__}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
                raise ValueError(f"Error al actualizar el prompt: {str(e)}")
            
            # Enviar el flujo de trabajo a la cola
            print("Enviando flujo de trabajo a la cola de ComfyUI...")
            try:
                prompt_id = self.queue_prompt(updated_workflow)
                print(f"✅ Flujo de trabajo enviado. Prompt ID: {prompt_id}")
            except Exception as e:
                print(f"ERROR al enviar el flujo de trabajo a la cola: {str(e)}")
                print(f"Tipo de error: {type(e).__name__}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
                raise ValueError(f"Error al enviar el flujo de trabajo a la cola: {str(e)}")
            
            # Esperar y obtener la imagen generada
            print("Esperando generación de imagen...")
            try:
                image_data = self.get_image(prompt_id)
                print(f"✅ Imagen generada: {image_data.get('local_path', 'No disponible')}")
                return image_data
            except Exception as e:
                print(f"ERROR al obtener la imagen generada: {str(e)}")
                print(f"Tipo de error: {type(e).__name__}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
                raise ValueError(f"Error al obtener la imagen generada: {str(e)}")
            
        except Exception as e:
            print(f"❌ ERROR en generate_image: {str(e)}")
            print(f"Tipo de error: {type(e).__name__}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            raise