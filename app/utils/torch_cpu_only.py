# app/utils/torch_cpu_only.py

"""
Sistema PyTorch exclusivamente CPU para evitar todos los conflictos GPU/Triton
"""

import os
import sys
import warnings

def force_cpu_environment():
    """Forzar entorno CPU-only antes de cualquier importación"""
    # Deshabilitar completamente CUDA
    os.environ['CUDA_VISIBLE_DEVICES'] = ''
    os.environ['CUDA_LAUNCH_BLOCKING'] = '1'
    
    # Deshabilitar Triton completamente
    os.environ['TRITON_DISABLE'] = '1'
    os.environ['TRITON_CACHE_DIR'] = ''
    
    # Configuración PyTorch básica
    os.environ['PYTORCH_DISABLE_WATCHER'] = '1'
    os.environ['TORCH_LOGS'] = ''
    os.environ['TORCH_LOG_LEVEL'] = 'ERROR'
    
    # Forzar CPU backend
    os.environ['TORCH_DEVICE'] = 'cpu'
    os.environ['TORCH_BACKEND'] = 'cpu'

def import_torch_cpu_only():
    """Importar PyTorch exclusivamente para CPU"""
    try:
        # Configurar entorno antes de importar
        force_cpu_environment()
        
        # Limpiar cualquier importación previa problemática
        modules_to_remove = [name for name in sys.modules.keys() 
                           if any(x in name.lower() for x in ['torch', 'triton', '_C'])]
        
        for module_name in modules_to_remove:
            if module_name in sys.modules:
                try:
                    del sys.modules[module_name]
                except:
                    pass
        
        # Importar con supresión total de warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            
            # Importación básica
            import torch
            
            # Verificar que está en modo CPU
            if torch.cuda.is_available():
                print("⚠️ CUDA detectado pero será ignorado (modo CPU-only)")
            
            # Configuración básica para CPU
            torch.set_num_threads(1)
            torch.set_grad_enabled(False)
            
            return torch, True, None
            
    except Exception as e:
        return None, False, f"Error CPU-only: {str(e)}"

class CPUOnlyImageGenerator:
    """Generador de imágenes simplificado para CPU"""
    
    def __init__(self):
        torch, success, error = import_torch_cpu_only()
        
        if not success:
            raise ImportError(f"No se pudo inicializar PyTorch CPU-only: {error}")
        
        self.torch = torch
        self.device = "cpu"
        self.pipe = None
        
        print("🖥️ Generador de imágenes inicializado (CPU-only)")
        self._setup_basic_pipeline()
    
    def _setup_basic_pipeline(self):
        """Configurar pipeline básico para CPU"""
        try:
            from diffusers import StableDiffusionPipeline
            
            # Usar modelo más pequeño para CPU
            model_id = "runwayml/stable-diffusion-v1-5"
            
            self.pipe = StableDiffusionPipeline.from_pretrained(
                model_id,
                torch_dtype=self.torch.float32,  # float32 para CPU
                safety_checker=None,
                requires_safety_checker=False,
                use_safetensors=True
            )
            
            self.pipe = self.pipe.to(self.device)
            self.pipe.enable_attention_slicing()  # Reducir uso de memoria
            
            print("✅ Pipeline CPU configurado correctamente")
            
        except Exception as e:
            print(f"❌ Error configurando pipeline: {e}")
            self.pipe = None
    
    def generate_optimized(self, prompt, width=512, height=512, num_inference_steps=20):
        """Generar imagen optimizada para CPU"""
        if not self.pipe:
            raise RuntimeError("Pipeline no inicializado")
        
        try:
            # Configuración optimizada para CPU
            image = self.pipe(
                prompt,
                width=width,
                height=height,
                num_inference_steps=num_inference_steps,
                guidance_scale=7.5
            ).images[0]
            
            # Información básica
            rag_info = {
                'confidence': 1.0,
                'enhancements_applied': []
            }
            
            return image, prompt, rag_info
            
        except Exception as e:
            raise RuntimeError(f"Error generando imagen: {e}")

def is_cpu_torch_available():
    """Verificar si PyTorch CPU-only está disponible"""
    _, available, _ = import_torch_cpu_only()
    return available
