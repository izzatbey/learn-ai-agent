from openai import OpenAI
from dotenv import load_dotenv
import os
import base64

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
image_path = "DAY2\img-1.jpg"


def decode_image(image_path):
    with open(image_path, "rb") as file:
        return base64.b64encode(file.read()).decode()

# print(decode_image(image_path))
base64_image = decode_image(image_path)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Please describe this following image."
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpg;base64,{base64_image}"
                    }
                }
            ]
        }
    ]
)

print(response.choices[0].message.content)