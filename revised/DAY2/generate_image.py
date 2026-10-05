from openai import OpenAI
from dotenv import load_dotenv
import os
import requests
import time

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
image_url = "https://media.istockphoto.com/id/517188688/photo/mountain-landscape.jpg?s=612x612&w=0&k=20&c=A63koPKaCyIwQWOTFBRWXj_PwCrR4cEoOw2S9Q7yVl8="

prompt = 'A cyberpunk city scenery at night with neon lights and flying cars, in the style of Blade Runner'

response = client.images.generate(
    model="dall-e-3",
    prompt=prompt,
    size="1024x1024",
    quality="standard",
    n=1
)

image_url = response.data[0].url
print("Generated Image URL:", response.data[0].url)

image_data = requests.get(image_url).content
file_name = "./output/generated_image_" + str(int(time.time())) + ".png"

with open(file_name, "wb") as f:
    f.write(image_data)

print(f"Image saved as {file_name}")