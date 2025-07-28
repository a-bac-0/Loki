# app/utils/simple_torch.py

"""
Sistema simplificado de PyTorch sin dependencias GPU problemáticas
"""

import os
import warnings
import sys

def setup_cpu_only_torch():
    """Configurar PyTorch para usar solo CPU y evitar conflictos"""
    # Forzar CPU-only desde el inicio
    os.environ['CUDA_VISIBLE_DEVICES'] = ''
    os.environ['PYTORCH_DISABLE_WATCHER'] = '1'
    os.environ['TORCH_LOGS'] = ''
    os.environ['TORCH_LOG_LEVEL'] = 'ERROR'
    
    # Suprimir warnings
    warnings.filterwarnings('ignore', category=UserWarning, module='torch')
    warnings.filterwarnings('ignore', category=FutureWarning, module='torch')
    warnings.filterwarnings('ignore', category=RuntimeWarning, module='torch')

def get_simple_torch():
    """Importar PyTorch de forma simple (CPU-only)"""
    try:
        setup_cpu_only_torch()
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            import torch
            
            # Configurar para CPU
            torch.set_num_threads(1)
            torch.set_grad_enabled(False)
            
            return torch, True, None
            
    except Exception as e:
        return None, False, str(e)

def is_simple_torch_available():
    """Verificar si PyTorch está disponible (versión simple)"""
    _, available, _ = get_simple_torch()
    return available
