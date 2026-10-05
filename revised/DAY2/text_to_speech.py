from openai import OpenAI
from dotenv import load_dotenv
import os
import time

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

text = "Hello, welcome to the world of text-to-speech conversion using OpenAI!"
audio_file = "./output/generated_tts_" + str(int(time.time())) + ".mp3"

with client.audio.speech.with_streaming_response.create(
    model="gpt-4o-mini-tts",
    voice="alloy",
    input=text,
) as response:
    response.stream_to_file(audio_file)