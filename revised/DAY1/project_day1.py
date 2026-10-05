from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# CONSTANTS
SYSPROMPT = "You are a helpful assistant."
SYSPROMPT_SUMMARIZE = "You are a helpful assistant that summarizes conversation history into a concise format."
MAX_HISTORY = 4 * 2 + 1

#GLOBAL VARIABLES
history = [
    {"role": "system", "content": SYSPROMPT},
]

def get_model_response(messages):
    full_response = ""
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        stream=True,
    )
    
    for chunk in response:
            content  = chunk.choices[0].delta.content
            if content is not None:
                # print(content, end='', flush=True)
                full_response += content
    
    return full_response


def main():
    while True:
        user_chat = input("You: ")

        if user_chat.lower() == '/bye':
            print("Exiting the chat. Goodbye!")
            break
        
        history.append({"role": "user", "content": user_chat})


        

        history.append({"role": "assistant", "content": full_response})

        if len(history) > MAX_HISTORY:
            summarize = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSPROMPT_SUMMARIZE},
                    {"role": "user", "content": f"Summarize the following conversation history briefly:\n\n{history[1:-1]}"}
                ]
            )
            
            new_history = [history[0]]
            history = [new_history]
            history.append({"role": "system", "content": f"Summary of previous conversation: {summarize.choices[0].message.content}"})

        print(f"Bot: {full_response}")