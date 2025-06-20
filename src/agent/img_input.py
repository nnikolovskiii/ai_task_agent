from PIL import Image
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client()


def multimodal_generation(image_file: str, instruction: str):
    image = Image.open(image_file)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[image, instruction]
    )
    return response
