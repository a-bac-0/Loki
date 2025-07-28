# app/utils/image_generator.py

import os
import warnings
import time
from PIL import Image
import numpy as np

# Usar importación retrasada de PyTorch
try:
    from .lazy_torch import get_torch, is_torch_available, get_torch_info
except ImportError:
    # Fallback al sistema simple
    from .simple_torch import get_simple_torch as get_torch, is_simple_torch_available as is_torch_available
    
    def get_torch_info():
        torch, available, error = get_torch()
        if available:
            return {'available': True, 'cuda_available': torch.cuda.is_available() if torch else False}
        else:
            return {'available': False, 'error': error}

# No importar PyTorch directamente aquí - se hará bajo demanda
torch = None

try:
    from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
    from transformers import pipeline
    import faiss
    from sentence_transformers import SentenceTransformer
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    DEPENDENCIES_AVAILABLE = False
    print(f"⚠️ Dependencias de imagen no disponibles: {e}")

class OptimizedGPUImageGenerator:
    """Generador de imágenes optimizado para GPU con sistema RAG integrado"""
    
    def __init__(self):
        """Inicializar el generador con configuración optimizada"""
        # Importar PyTorch bajo demanda
        global torch
        torch, torch_available, torch_error = get_torch()
        
        if not torch_available:
            raise ImportError(f"PyTorch no disponible: {torch_error}")
        
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError("Las dependencias requeridas no están disponibles")
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.pipe = None
        self.rag_model = None
        self.rag_index = None
        self.rag_prompts = []
        
        print(f"🎮 Inicializando generador en: {self.device}")
        
        # Configurar modelo de difusión
        self._setup_diffusion_model()
        
        # Configurar sistema RAG interno
        self._setup_rag_system()
    
    def _setup_diffusion_model(self):
        """Configurar el pipeline de Stable Diffusion"""
        try:
            # Usar modelo optimizado para GPU/CPU
            model_id = "runwayml/stable-diffusion-v1-5"
            
            # Configuración específica según dispositivo
            if self.device == "cuda":
                # Configuración optimizada para GPU
                self.pipe = StableDiffusionPipeline.from_pretrained(
                    model_id,
                    torch_dtype=torch.float16,
                    use_safetensors=True,
                    variant="fp16"
                )
                
                # Optimizaciones para memoria GPU
                self.pipe.enable_attention_slicing()
                self.pipe.enable_xformers_memory_efficient_attention()
                
                # Scheduler optimizado
                self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(
                    self.pipe.scheduler.config
                )
                
            else:
                # Configuración para CPU
                self.pipe = StableDiffusionPipeline.from_pretrained(
                    model_id,
                    torch_dtype=torch.float32,
                    use_safetensors=True
                )
                
                # Optimizaciones para CPU
                self.pipe.enable_attention_slicing()
            
            self.pipe = self.pipe.to(self.device)
            
            # Configurar safety checker más permisivo
            self.pipe.safety_checker = None
            self.pipe.requires_safety_checker = False
            
            print(f"✅ Modelo de difusión cargado en {self.device}")
            
        except Exception as e:
            print(f"❌ Error configurando modelo de difusión: {e}")
            raise e
    
    def _setup_rag_system(self):
        """Configurar sistema RAG interno para mejora de prompts"""
        try:
            # Modelo ligero para embeddings
            self.rag_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Base de conocimientos de prompts de alta calidad
            self.rag_prompts = [
                "highly detailed digital art, professional illustration, masterpiece quality",
                "photorealistic rendering, sharp focus, vivid colors, perfect lighting",
                "artistic composition, creative design, modern aesthetic",
                "professional photography style, studio lighting, high resolution",
                "concept art style, detailed textures, atmospheric lighting",
                "minimalist design, clean composition, elegant simplicity",
                "futuristic style, technological aesthetic, innovation theme",
                "natural lighting, realistic materials, authentic details",
                "corporate professional style, business presentation quality",
                "social media optimized, eye-catching design, viral potential"
            ]
            
            # Crear índice FAISS para búsqueda rápida
            embeddings = self.rag_model.encode(self.rag_prompts)
            
            # Configurar índice FAISS
            dimension = embeddings.shape[1]
            self.rag_index = faiss.IndexFlatIP(dimension)  # Producto interno para similaridad
            
            # Normalizar embeddings para uso con producto interno
            faiss.normalize_L2(embeddings)
            self.rag_index.add(embeddings.astype('float32'))
            
            print("✅ Sistema RAG interno configurado")
            
        except Exception as e:
            print(f"⚠️ Error configurando RAG interno: {e}")
            # Continuar sin RAG si falla
            self.rag_model = None
            self.rag_index = None
    
    def _enhance_prompt_with_rag(self, user_prompt, k=3):
        """Mejorar el prompt del usuario usando el sistema RAG interno"""
        if not self.rag_model or not self.rag_index:
            return user_prompt, 0.0, []
        
        try:
            # Crear embedding del prompt del usuario
            user_embedding = self.rag_model.encode([user_prompt])
            faiss.normalize_L2(user_embedding)
            
            # Buscar prompts similares
            scores, indices = self.rag_index.search(user_embedding.astype('float32'), k)
            
            # Obtener mejores coincidencias
            enhancements = []
            total_confidence = 0.0
            
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if score > 0.1:  # Umbral mínimo de relevancia
                    enhancement = {
                        'name': f"Enhancement {i+1}",
                        'prompt': self.rag_prompts[idx],
                        'confidence': float(score)
                    }
                    enhancements.append(enhancement)
                    total_confidence += score
            
            # Crear prompt mejorado
            if enhancements:
                # Seleccionar las mejores mejoras
                best_enhancements = [e['prompt'] for e in enhancements[:2]]
                enhanced_prompt = f"{user_prompt}, {', '.join(best_enhancements)}"
                
                # Calcular confianza promedio
                avg_confidence = total_confidence / len(enhancements)
            else:
                enhanced_prompt = user_prompt
                avg_confidence = 0.0
            
            return enhanced_prompt, avg_confidence, enhancements
            
        except Exception as e:
            print(f"⚠️ Error en mejora RAG: {e}")
            return user_prompt, 0.0, []
    
    def generate_optimized(self, prompt, width=512, height=512, num_inference_steps=25, guidance_scale=7.5):
        """Generar imagen con optimizaciones y mejoras RAG"""
        if not self.pipe:
            raise RuntimeError("El modelo de difusión no está inicializado")
        
        start_time = time.time()
        
        try:
            # Mejorar prompt con RAG
            enhanced_prompt, rag_confidence, rag_enhancements = self._enhance_prompt_with_rag(prompt)
            
            # Configurar parámetros según dispositivo
            if self.device == "cuda":
                # GPU: mayor calidad
                generator = torch.Generator(device=self.device).manual_seed(42)
                num_inference_steps = min(num_inference_steps, 30)  # Limitar para memoria
            else:
                # CPU: velocidad optimizada
                generator = torch.Generator().manual_seed(42)
                num_inference_steps = min(num_inference_steps, 20)  # Menos pasos para CPU
            
            # Generar imagen
            with torch.inference_mode():
                result = self.pipe(
                    prompt=enhanced_prompt,
                    width=width,
                    height=height,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    generator=generator,
                    negative_prompt="blurry, low quality, distorted, ugly, bad anatomy"
                )
            
            image = result.images[0]
            generation_time = time.time() - start_time
            
            # Información de generación
            rag_info = {
                'confidence': rag_confidence,
                'enhancements_applied': rag_enhancements,
                'original_prompt': prompt,
                'enhanced_prompt': enhanced_prompt,
                'generation_time': generation_time,
                'device_used': self.device,
                'resolution': f"{width}x{height}"
            }
            
            print(f"✅ Imagen generada en {generation_time:.2f}s ({self.device})")
            
            return image, enhanced_prompt, rag_info
            
        except torch.cuda.OutOfMemoryError:
            # Manejo específico de memoria GPU
            print("⚠️ Memoria GPU insuficiente, liberando caché...")
            torch.cuda.empty_cache()
            
            # Reintentar con configuración reducida
            return self._generate_fallback(prompt, width//2, height//2, num_inference_steps//2)
            
        except Exception as e:
            print(f"❌ Error generando imagen: {e}")
            raise e
    
    def _generate_fallback(self, prompt, width, height, steps):
        """Generación de respaldo con configuración reducida"""
        try:
            print(f"🔄 Reintentando con resolución reducida: {width}x{height}")
            
            enhanced_prompt, rag_confidence, rag_enhancements = self._enhance_prompt_with_rag(prompt)
            
            with torch.inference_mode():
                result = self.pipe(
                    prompt=enhanced_prompt,
                    width=width,
                    height=height,
                    num_inference_steps=steps,
                    guidance_scale=6.0,  # Reducir guidance
                    negative_prompt="blurry, low quality"
                )
            
            image = result.images[0]
            
            rag_info = {
                'confidence': rag_confidence,
                'enhancements_applied': rag_enhancements,
                'fallback_mode': True,
                'original_resolution': f"{width*2}x{height*2}",
                'actual_resolution': f"{width}x{height}"
            }
            
            return image, enhanced_prompt, rag_info
            
        except Exception as e:
            print(f"❌ Error en generación de respaldo: {e}")
            raise e
    
    def cleanup(self):
        """Limpiar recursos de memoria"""
        try:
            if hasattr(self, 'pipe') and self.pipe:
                del self.pipe
                
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                
            print("🧹 Recursos de memoria liberados")
            
        except Exception as e:
            print(f"⚠️ Error limpiando recursos: {e}")
    
    def __del__(self):
        """Destructor para limpieza automática"""
        try:
            self.cleanup()
        except:
            pass
