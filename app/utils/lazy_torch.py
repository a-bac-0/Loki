# app/utils/lazy_torch.py

"""
Sistema de importación retrasada para PyTorch que evita conflictos con Streamlit
"""

import os
import sys
import warnings
from typing import Tuple, Any, Optional

# Variable global para almacenar PyTorch una vez importado
_torch_module: Optional[Any] = None
_torch_available: bool = False
_torch_error: Optional[str] = None

def setup_torch_environment():
    """Configurar el entorno para PyTorch antes de la importación"""
    # Variables de entorno críticas
    os.environ['PYTORCH_DISABLE_WATCHER'] = '1'
    os.environ['TORCH_LOGS'] = ''
    os.environ['TORCH_LOG_LEVEL'] = 'ERROR'
    os.environ['TORCH_DISABLE_LOG_INIT'] = '1'
    os.environ['STREAMLIT_DISABLE_WATCHER'] = '1'
    
    # Variables para resolver conflictos de Triton
    os.environ['TRITON_CACHE_DIR'] = os.path.join(os.getcwd(), '.triton_cache')
    os.environ['TORCH_LIBRARY_ALLOW_MULTI'] = '1'  # Permitir múltiples registros
    os.environ['DISABLE_TRITON_REGISTER'] = '1'    # Deshabilitar registro de Triton
    
    # Configurar warnings
    warnings.filterwarnings('ignore', category=UserWarning, module='torch')
    warnings.filterwarnings('ignore', category=FutureWarning, module='torch')
    warnings.filterwarnings('ignore', category=RuntimeWarning, module='torch')
    warnings.filterwarnings('ignore', message='.*get_log_level_pairs.*')
    warnings.filterwarnings('ignore', message='.*There is no current event loop.*')
    warnings.filterwarnings('ignore', message='.*TORCH_LIBRARY.*')
    warnings.filterwarnings('ignore', message='.*triton.*')

def patch_torch_logging_advanced():
    """Parche avanzado para el sistema de logging de PyTorch"""
    try:
        # Interceptar la función problemática antes de que se ejecute
        import torch._logging._internal as torch_internal
        
        # Guardar la función original
        original_init_logs = getattr(torch_internal, '_init_logs', None)
        
        def safe_init_logs():
            """Versión segura de _init_logs"""
            try:
                if original_init_logs:
                    # Intentar ejecutar la función original
                    original_init_logs()
            except AttributeError as e:
                if 'get_log_level_pairs' in str(e):
                    # Error conocido, ignorar silenciosamente
                    pass
                else:
                    # Otro error de atributo, re-lanzar
                    raise
            except Exception:
                # Cualquier otro error, ignorar para no bloquear la aplicación
                pass
        
        # Reemplazar la función problemática
        torch_internal._init_logs = safe_init_logs
        
        return True
        
    except ImportError:
        # torch._logging._internal no disponible
        return True
    except Exception as e:
        print(f"⚠️ Error aplicando parche de logging: {e}")
        return False

def get_torch() -> Tuple[Any, bool, Optional[str]]:
    """
    Obtener PyTorch con importación retrasada y manejo de errores
    
    Returns:
        tuple: (torch_module, is_available, error_message)
    """
    global _torch_module, _torch_available, _torch_error
    
    # Si ya se intentó importar, devolver el resultado cached
    if _torch_module is not None or _torch_error is not None:
        return _torch_module, _torch_available, _torch_error
    
    try:
        # Configurar entorno
        setup_torch_environment()
        
        # Aplicar parche de logging
        patch_torch_logging_advanced()
        
        # Limpiar importaciones previas de PyTorch/Triton si existen
        modules_to_clear = []
        for module_name in list(sys.modules.keys()):
            if any(name in module_name.lower() for name in ['torch', 'triton', '_C']):
                modules_to_clear.append(module_name)
        
        # Eliminar módulos conflictivos (solo si no son críticos)
        for module_name in modules_to_clear:
            if 'torch' not in module_name or '_C' in module_name:
                try:
                    del sys.modules[module_name]
                except:
                    pass
        
        # Importar PyTorch con máxima supresión de warnings y errores
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            
            # Intentar importación controlada
            try:
                import torch
            except RuntimeError as e:
                if 'TORCH_LIBRARY' in str(e) or 'triton' in str(e).lower():
                    # Error conocido de Triton, intentar con configuración CPU-only
                    os.environ['CUDA_VISIBLE_DEVICES'] = ''  # Forzar CPU temporalmente
                    try:
                        import torch
                        # Restaurar GPU si está disponible
                        if 'CUDA_VISIBLE_DEVICES' in os.environ:
                            del os.environ['CUDA_VISIBLE_DEVICES']
                    except Exception:
                        # Si falla completamente, mantener CPU-only
                        import torch
                else:
                    # Otro tipo de error, re-lanzar
                    raise
            
            # Configurar PyTorch para máxima compatibilidad
            torch.set_num_threads(1)
            torch.set_grad_enabled(False)  # Deshabilitar gradientes por defecto
            
            # Configurar backends si están disponibles
            if hasattr(torch.backends, 'cudnn'):
                try:
                    torch.backends.cudnn.benchmark = False
                    torch.backends.cudnn.deterministic = True
                except:
                    pass  # Ignorar errores de configuración de CUDNN
            
            # Cache el módulo
            _torch_module = torch
            _torch_available = True
            _torch_error = None
            
            return torch, True, None
            
    except Exception as e:
        error_msg = f"Error importando PyTorch: {str(e)}"
        _torch_module = None
        _torch_available = False
        _torch_error = error_msg
        
        return None, False, error_msg

def is_torch_available() -> bool:
    """Verificar si PyTorch está disponible sin importarlo"""
    _, available, _ = get_torch()
    return available

def get_torch_info() -> dict:
    """Obtener información sobre PyTorch"""
    torch_module, available, error = get_torch()
    
    if not available:
        return {
            'available': False,
            'error': error,
            'version': None,
            'cuda_available': False,
            'device_count': 0
        }
    
    try:
        info = {
            'available': True,
            'error': None,
            'version': torch_module.__version__,
            'cuda_available': torch_module.cuda.is_available(),
            'device_count': torch_module.cuda.device_count() if torch_module.cuda.is_available() else 0
        }
        
        if info['cuda_available']:
            info['gpu_name'] = torch_module.cuda.get_device_name(0)
            info['gpu_memory'] = torch_module.cuda.get_device_properties(0).total_memory / (1024**3)
        
        return info
        
    except Exception as e:
        return {
            'available': True,
            'error': f"Error obteniendo info: {str(e)}",
            'version': getattr(torch_module, '__version__', 'Unknown'),
            'cuda_available': False,
            'device_count': 0
        }
