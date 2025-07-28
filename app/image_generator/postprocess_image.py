from PIL import Image, ImageEnhance, ImageFilter
import os
import sys



def postprocess_image(image_path, output_dir=None):
    image = Image.open(image_path)
    basename = os.path.splitext(os.path.basename(image_path))[0]
    if output_dir is None:
        output_dir = os.path.dirname(image_path)


    # Tabla de dimensiones por red social y tipo
    SIZES = {
        'instagram': {
            'cuadrada': (1080, 1080),
            'horizontal': (1080, 566),
            'vertical': (1080, 1350),
            'historias': (1080, 1920),
            'perfil': (320, 320),
        },
        'facebook': {
            'perfil': (320, 320),
            'portada': (820, 312),
            'cuadrada': (1200, 1200),
            'horizontal': (1200, 630),
            'historias': (1080, 1920),
        },
        'twitter': {
            'perfil': (400, 400),
            'cabecera': (1500, 500),
            'post': (1200, 675),
        },
        'linkedin': {
            'perfil': (400, 400),
            'fondo': (1584, 396),
            'publicacion': (1200, 627),
        },
        'tiktok': {
            'perfil': (200, 200),
            'historias': (1080, 1920),
        },
        'youtube': {
            'perfil': (800, 800),
            'banner': (2560, 1440),
            'miniatura': (1280, 720),
        },
    }

    # Carpeta base para la imagen
    base_folder = os.path.join(output_dir, basename)
    os.makedirs(base_folder, exist_ok=True)

    # Para cada red y tipo, crear subcarpeta y guardar la imagen
    for red, tipos in SIZES.items():
        red_folder = os.path.join(base_folder, red)
        os.makedirs(red_folder, exist_ok=True)
        for tipo, (w, h) in tipos.items():
            # Redimensionar manteniendo la relación, luego recortar si es necesario
            # Primero, escalar para cubrir el área (cover)
            aspect_target = w / h
            aspect_img = image.width / image.height
            if aspect_img > aspect_target:
                # Imagen más ancha que el target: escalar alto, recortar ancho
                scale = h / image.height
                new_width = int(image.width * scale)
                img_resized = image.resize((new_width, h), Image.LANCZOS)
                left = (new_width - w) // 2
                img_final = img_resized.crop((left, 0, left + w, h))
            else:
                # Imagen más alta que el target: escalar ancho, recortar alto
                scale = w / image.width
                new_height = int(image.height * scale)
                img_resized = image.resize((w, new_height), Image.LANCZOS)
                top = (new_height - h) // 2
                img_final = img_resized.crop((0, top, w, top + h))
            img_final.save(os.path.join(red_folder, f"{tipo}_{w}x{h}.png"))

    print(f"Procesamiento completado. Imágenes guardadas en: {base_folder}")
