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


client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash-preview-tts",
    contents="Здраво, како можам да ти помогнам?",
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
