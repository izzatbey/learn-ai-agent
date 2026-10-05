from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Jelaskan kepada saya tentang AI dalam bahasa Indonesia."}
    ],
    stream=True,
)

full_response = ""

for chunk in response:
    if chunk.choices[0].delta.content is not None:
        content = chunk.choices[0].delta.content
        print(content, end='', flush=True)
        full_response += content
        
print("\n\nFull Response:")
print(full_response)