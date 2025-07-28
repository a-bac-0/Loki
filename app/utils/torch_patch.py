# app/utils/torch_patch.py

"""
Parche temporal para resolver conflictos entre PyTorch y Streamlit
"""

import os
import sys
import warnings

def patch_torch_logging():
    """Aplicar parche para resolver el error de get_log_level_pairs"""
    try:
        # Configurar variables de entorno antes de importar torch
        os.environ['TORCH_LOGS'] = ''
        os.environ['TORCH_LOG_LEVEL'] = 'ERROR'
        os.environ['TORCH_DISABLE_LOG_INIT'] = '1'
        
        # Suprimir warnings específicos de logging
        warnings.filterwarnings('ignore', message='.*get_log_level_pairs.*')
        
        # Monkeypatching más agresivo - interceptar la importación
        import sys
        
        # Verificar si torch ya está importado
        if 'torch' in sys.modules:
            # Si ya está importado, aplicar parche a módulos existentes
            try:
                torch_logging = sys.modules.get('torch._logging._internal')
                if torch_logging and hasattr(torch_logging, 'log_state'):
                    log_state = torch_logging.log_state
                    if isinstance(log_state, dict) and not hasattr(log_state, 'get_log_level_pairs'):
                        class LogStateWrapper(dict):
                            def get_log_level_pairs(self):
                                return []
                        torch_logging.log_state = LogStateWrapper(log_state)
            except Exception:
                pass
        
        # También modificar el entorno para futuras importaciones
        original_init_logs = None
        
        def patched_init_logs():
            """Versión parcheada de _init_logs que no falla"""
            try:
                # Intentar la función original si existe
                if original_init_logs:
                    original_init_logs()
            except AttributeError:
                # Ignorar el error específico de get_log_level_pairs
                pass
            except Exception:
                # Ignorar otros errores de logging
                pass
        
        # Aplicar el parche a nivel de módulo
        try:
            import torch._logging._internal as torch_logging_module
            if hasattr(torch_logging_module, '_init_logs'):
                original_init_logs = torch_logging_module._init_logs
                torch_logging_module._init_logs = patched_init_logs
        except ImportError:
            pass
        
        return True
        
    except Exception as e:
        print(f"⚠️ Error aplicando parche PyTorch: {e}")
        return False

def safe_torch_import():
    """Importar PyTorch de manera segura con parches aplicados"""
    try:
        # Aplicar parche antes de importar
        patch_torch_logging()
        
        # Suprimir todos los warnings durante la importación
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            import torch
            
            # Configurar PyTorch para evitar conflictos
            torch.set_num_threads(1)
            if hasattr(torch.backends, 'cudnn'):
                torch.backends.cudnn.benchmark = False
                torch.backends.cudnn.deterministic = True
        
        return torch, True
        
    except Exception as e:
        print(f"❌ Error importando PyTorch: {e}")
        return None, False
