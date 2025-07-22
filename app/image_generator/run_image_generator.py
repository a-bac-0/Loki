
from image_generator import ImageGeneratorAI
from datetime import datetime
import os

if __name__ == "__main__":
    # Crear carpeta de salida si no existe (relativa al proyecto)
    output_dir = os.path.join(os.path.dirname(__file__), "..", "imagenes_IA")
    os.makedirs(output_dir, exist_ok=True)

    prompt = "A commercial airplane flying high above snow-capped mountains, with scattered fluffy clouds in the sky. The scene is bright and clear, with natural daylight illuminating the landscape. A sense of freedom and adventure in the atmosphere."
    width = 512
    height = 512
    num_inference_steps = 15
    guidance_scale = 7.5

    generator = ImageGeneratorAI()
    image, gen_time = generator.generate(
        prompt,
        width=width,
        height=height,
        num_inference_steps=num_inference_steps,
        guidance_scale=guidance_scale
    )
    filename = os.path.join(output_dir, f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    image.save(filename)
    print(f"Imagen guardada como {filename}")
    generator.cleanup()
