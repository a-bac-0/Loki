# ima_imagen: Generación de imágenes con Stable Diffusion

Este proyecto permite generar imágenes a partir de texto usando el modelo Stable Diffusion 2.1 de HuggingFace Diffusers.

## Requisitos
- Python 3.10
- Tarjeta NVIDIA compatible con CUDA (opcional, recomendado para mejor rendimiento)

## Instalación

1. **Clona el repositorio y entra en la carpeta del proyecto:**
   ```sh
   cd image_generator
   ```

2. **Crea y activa un entorno virtual (opcional pero recomendado):**
   ```sh
   python -m venv .venv
   .venv\Scripts\activate  # En Windows
   # source .venv/bin/activate  # En Linux/Mac
   ```

3. **Instala las dependencias:**
   ```sh
   pip install -r requirements.txt
   ```

4. **(Opcional, para GPU NVIDIA) Instala PyTorch con soporte CUDA:**
   ```sh
   pip install torch==2.2.2+cu118 torchvision==0.17.2+cu118 torchaudio==2.2.2+cu118 --extra-index-url https://download.pytorch.org/whl/cu118
   ```

5. **(Opcional, para GPU NVIDIA) Instala CUDA Toolkit 11.8:**
   Descarga e instala desde: https://developer.nvidia.com/cuda-11-8-0-download-archive


## Uso

### Ver información de la GPU

Puedes ejecutar el script `gpu_info.py` para ver si tu sistema detecta la GPU y consultar el uso de memoria:
```sh
python gpu_info.py
```

### Generar una imagen

1. Edita el archivo `run_image_generator.py` para cambiar el prompt o los parámetros de la imagen (tamaño, pasos, etc).
2. Ejecuta el script:
   ```sh
   python run_image_generator.py
   ```
3. El resultado se guardará como un archivo PNG con la fecha y hora en la carpeta del proyecto.

## Notas
- Si ves el mensaje "CUDA no está disponible. Se usará CPU.", tu GPU no está siendo detectada. Revisa la instalación de drivers y CUDA Toolkit.
- Los valores de `height` y `width` deben ser múltiplos de 8.
- Para mejores resultados, usa imágenes de al menos 256x256 o 512x512.

---

Proyecto para generación de imágenes IA - Juan Carlos Macías



