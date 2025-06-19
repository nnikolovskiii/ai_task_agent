import os

from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)


def transcribe_audio_file(audio_file):
    myfile = client.files.upload(file=audio_file)
    prompt = 'Generate a transcript of the speech.'

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[prompt, myfile]
    )

    return response.text
