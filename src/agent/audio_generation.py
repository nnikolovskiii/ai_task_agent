import wave

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm)


def generate_audio_output(response_text:str):
    client = genai.Client()

    response_text = remove_markdown(response_text)

    response = client.models.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents=response_text,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name='Aoede',
                    )
                )
            ),
        )
    )

    data = response.candidates[0].content.parts[0].inline_data.data

    file_name = 'out.wav'
    wave_file(file_name, data)


import re


def remove_markdown(text):
    # Remove headers (e.g., # Header)
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)

    # Remove bold and italic markers (**, __, *, _)
    text = re.sub(r'(\*\*|__)(.*?)\1', r'\2', text)
    text = re.sub(r'(\*|_)(.*?)\1', r'\2', text)

    # Remove strikethrough (~~text~~)
    text = re.sub(r'~~(.*?)~~', r'\1', text)

    # Remove inline links: [text](url)
    text = re.sub(r'$$(.*?)$$$(.*?)$', r'\1', text)

    # Remove reference-style links: [text][id] and then [*]: url
    text = re.sub(r'$$(.*?)$$$\w+$', r'\1', text)
    text = re.sub(r'$\w+$$.*?$', '', text, flags=re.DOTALL)

    # Remove images: ![alt](url)
    text = re.sub(r'!\s*$$.*?$$$.*?$', '', text)

    # Remove blockquotes
    text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)

    # Remove unordered list markers (-, *, +)
    text = re.sub(r'^[\-\*\+]\s+', '', text, flags=re.MULTILINE)

    # Remove ordered list markers (e.g., 1.)
    text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)

    # Remove code blocks (fenced with ``` or ~~~)
    text = re.sub(r'```.*?$.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'~~~.*?$.*?~~~', '', text, flags=re.DOTALL)

    # Remove inline code (`code`)
    text = re.sub(r'(.*?)', r'\1', text)

    # Remove horizontal rules
    text = re.sub(r'^\s*[-*_]\s*[-*_]\s*[-*_]\s*$', '', text, flags=re.MULTILINE)

    # Remove extra newlines and trailing spaces
    text = re.sub(r'\n\s*\n', '\n\n', text)

    return text.strip()
