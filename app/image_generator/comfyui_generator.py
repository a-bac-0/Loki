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
        try:
            with open(workflow_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise ValueError(f"Error al cargar el flujo de trabajo: {str(e)}")
    
    def _find_prompt_node(self, workflow):
        """Encuentra el nodo de prompt en el flujo de trabajo
        
        Args:
            workflow (dict): El flujo de trabajo de ComfyUI
            
        Returns:
            tuple: (node_id, input_name) del nodo de prompt, o (None, None) si no se encuentra
        """
        for node_id, node in workflow.get("nodes", {}).items():
            if node.get("type") == "CLIPTextEncode":
                for input_name, input_value in node.get("inputs", {}).items():
                    if input_name == "text" and isinstance(input_value, str):
                        return node_id, input_name
        return None, None
    
    def update_prompt(self, workflow, prompt):
        """Actualiza el prompt en el flujo de trabajo
        
        Args:
            workflow (dict): El flujo de trabajo de ComfyUI
            prompt (str): El nuevo prompt a utilizar
            
        Returns:
            dict: El flujo de trabajo actualizado
        """
        node_id, location = self._find_prompt_node(workflow)
        
        if node_id is None or location is None:
            raise ValueError("No se encontró un nodo de prompt en el flujo de trabajo")
        
        # Crear una copia del flujo de trabajo para no modificar el original
        updated_workflow = json.loads(json.dumps(workflow))
        
        # Actualizar el prompt según el tipo de ubicación encontrada
        if isinstance(location, int):  # Es un índice de widget
            if "widgets_values" not in updated_workflow["nodes"][node_id]:
                updated_workflow["nodes"][node_id]["widgets_values"] = []
            
            # Asegurarse de que hay suficientes elementos en la lista
            while len(updated_workflow["nodes"][node_id]["widgets_values"]) <= location:
                updated_workflow["nodes"][node_id]["widgets_values"].append("")
            
            # Actualizar el prompt en widgets_values
            updated_workflow["nodes"][node_id]["widgets_values"][location] = prompt
            print(f"Prompt actualizado en nodo {node_id}, widget_index {location}")
        else:  # Es un nombre de input
            # Actualizar el prompt en inputs
            updated_workflow["nodes"][node_id]["inputs"][location] = prompt
            print(f"Prompt actualizado en nodo {node_id}, input {location}")
        
        return updated_workflow
    
    def queue_prompt(self, workflow):
        """Envía un flujo de trabajo a la cola de ComfyUI
        
        Args:
            workflow (dict): El flujo de trabajo a enviar
            
        Returns:
            str: El ID del prompt en la cola
        """
        try:
            prompt_payload = {
                "prompt": workflow,
                "client_id": self.client_id
            }
            
            response = requests.post(
                f"{self.base_url}/prompt", 
                json=prompt_payload,
                timeout=30
            )
            
            if response.status_code != 200:
                raise ValueError(f"Error al enviar el prompt: {response.text}")
            
            return response.json().get("prompt_id")
            
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error de conexión con ComfyUI: {str(e)}")
    
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
        """Genera una imagen a partir de un prompt de texto
        
        Args:
            prompt (str): El prompt de texto para generar la imagen
            workflow_file (str, optional): Ruta al archivo JSON del flujo de trabajo
            workflow_data (dict, optional): Datos del flujo de trabajo ya cargados
            
        Returns:
            dict: Información de la imagen generada
        """
        # Verificar que el servidor esté activo
        if not self.check_server_status():
            raise ConnectionError("El servidor de ComfyUI no está disponible")
        
        # Cargar el flujo de trabajo
        if workflow_data is None:
            if workflow_file is None:
                raise ValueError("Debe proporcionar un archivo de flujo de trabajo o datos de flujo de trabajo")
            workflow = self.load_workflow(workflow_file)
        else:
            workflow = workflow_data
        
        # Actualizar el prompt en el flujo de trabajo
        updated_workflow = self.update_prompt(workflow, prompt)
        
        # Enviar el flujo de trabajo a la cola
        prompt_id = self.queue_prompt(updated_workflow)
        
        # Esperar y obtener la imagen generada
        return self.get_image(prompt_id)