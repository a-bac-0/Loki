import torch

if torch.cuda.is_available():
    print(f"CUDA disponible: {torch.cuda.get_device_name(0)}")
    print(f"Cantidad de GPUs detectadas: {torch.cuda.device_count()}")
    props = torch.cuda.get_device_properties(0)
    print(f"Memoria total: {props.total_memory // (1024**2)} MB")
    print(f"Memoria libre (PyTorch): {torch.cuda.memory_reserved(0) // (1024**2)} MB")
    print(f"Memoria usada (PyTorch): {torch.cuda.memory_allocated(0) // (1024**2)} MB")
    print("Nota: Estos valores solo reflejan la memoria reservada/ocupada por PyTorch.")
    print("Para ver la memoria real libre/ocupada de la GPU, usa el comando 'nvidia-smi' en la terminal.")
    print(f"Capacidad de cómputo: {props.major}.{props.minor}")

    # Prueba de carga: crear un tensor grande en la GPU
    print("\n--- Prueba de carga de GPU con PyTorch ---")
    x = torch.randn((4096, 4096), device='cuda')
    print(f"Memoria usada tras crear tensor: {torch.cuda.memory_allocated(0) // (1024**2)} MB")
    del x
    torch.cuda.empty_cache()
    print(f"Memoria usada tras liberar tensor: {torch.cuda.memory_allocated(0) // (1024**2)} MB")
    print(f"Capacidad de cómputo: {props.major}.{props.minor}")
else:
    print("CUDA no está disponible. No se detectó GPU compatible.")
