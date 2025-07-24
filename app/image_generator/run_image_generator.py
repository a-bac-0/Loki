
from image_generator import ImageGeneratorAI
from postprocess_image import postprocess_image
from datetime import datetime
import os

if __name__ == "__main__":
    # Crear carpeta de salida si no existe (relativa al proyecto)
    output_dir = os.path.join(os.path.dirname(__file__), "..", "imagenes_IA")
    os.makedirs(output_dir, exist_ok=True)

    #prompt = "A commercial airplane flying high above snow-capped mountains, with scattered fluffy clouds in the sky. The scene is bright and clear, with natural daylight illuminating the landscape. A sense of freedom and adventure in the atmosphere."
    #prompt="Una composición vibrante y colorida de alimentos saludables dispuestos sobre una superficie de madera clara con luz natural suave. Incluye un tazón con bayas frescas (fresas, arándanos, frambuesas), un puñado de nueces mixtas, rodajas de aguacate sobre pan integral tostado, pepino en rodajas y unas hojas verdes brillantes. El estilo debe ser 'flat lay' o 'top-down', con una estética moderna y minimalista. La iluminación es suave y difusa, creando sombras sutiles que resaltan las texturas de los alimentos.  El fondo debe estar ligeramente desenfocado para enfocar la atención en los alimentos. Paleta de colores: tonos verdes, rojos, púrpuras y marrones cálidos. Resolución ultra alta (8k). Estilo fotográfico profesional."
    #prompt= "Un cebra, con su pelaje en blanco y negro a rayas distintivas, está cruzando un río turbio lleno de cocodrilos acechantes. Los cocodrilos están parcialmente sumergidos en el agua, mostrando sus ojos y dientes, creando una sensación de tensión y peligro. El agua es marrón y reflectante, capturando la luz del sol. La escena se desarrolla en la sabana africana durante el atardecer, con un cielo dramático lleno de nubes naranjas y púrpuras. El estilo debe ser realista y detallado, como una fotografía de naturaleza salvaje. Iluminación dorada y cálida que enfatiza las texturas del pelaje del cebra y los dientes de los cocodrilos. Resolución ultra alta (8k).  Composición dinámica con el cebra en movimiento, transmitiendo velocidad y determinación."
    prompt="Ozzy Osbourne performing live on stage at a rock concert, wearing gothic black leather clothes with silver chains, dramatic stage lighting with blue and red spotlights, energetic pose, long dark hair blowing in the wind, intense facial expression, crowd in the background, photorealistic, ultra-detailed, 4K resolution, cinematic style, capturing the essence of a legendary rock performance."
    width = 512
    height = 512
    num_inference_steps = 20
    guidance_scale = 8

    generator = ImageGeneratorAI()
    image, gen_time = generator.generate(
        prompt,
        width=width,
        height=height,
        num_inference_steps=num_inference_steps,
        guidance_scale=guidance_scale
    )
    
    # Guardar la imagen original en su propia carpeta
    base_name = f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    image_folder = os.path.join(output_dir, base_name)
    os.makedirs(image_folder, exist_ok=True)
    filename = os.path.join(image_folder, f"{base_name}.png")
    image.save(filename)
    print(f"Imagen guardada como {filename}")

    # Postprocesar la imagen generada
    print("Procesando mejoras automáticas...")
    postprocess_image(filename, output_dir=output_dir)

    generator.cleanup()
