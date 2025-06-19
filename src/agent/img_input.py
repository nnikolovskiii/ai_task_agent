from PIL import Image
from google import genai

client = genai.Client(api_key="GEMINI_API_KEY")


def multimodal_generation(image_file: str, instruction: str):
    image = Image.open(image_file)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[image, instruction]
    )
    return response
