from openai import OpenAI
from dotenv import load_dotenv
import os
import time

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

audio_path = "./output/generated_tts_1.mp3"

with open(audio_path, "rb") as f:
    result = client.audio.transcriptions.create(
        model="whisper-1",
        file=f,
        response_format="text"
    )
    
print("Transcribed Text:", result)