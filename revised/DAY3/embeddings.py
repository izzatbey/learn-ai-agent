from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

input = "anjing tersebut lucu sekali dan sedang bermain bola di taman"

response = client.embeddings.create(
    model="text-embedding-3-small",
    input=input
)

print(f'Text: {input}')
print(f'Dimension: {len(response.data[0].embedding)}')
print(f'Embedding: {response.data[0].embedding[:10]}')