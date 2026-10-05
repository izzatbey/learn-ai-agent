from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(    
    api_key=os.getenv("OPENAI_API_KEY")
)

# CONSTANTS
SYSPROMPT = "You are a helpful assistant."
MAX_HISTORY = 2 * 2 + 1

history = [
    {"role": "system", "content": SYSPROMPT},
]

while True:
    user_chat = input("You: ")
    
    # Exit the loop if the user types 'exit'
    if user_chat.lower() == 'bye':
        print("Exiting the chat. Goodbye!")
        break
    
    history.append({"role": "user", "content": user_chat})
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=history
    )
    
    history.append({"role": "assistant", "content": response.choices[0].message.content})
    
    if len(history) > MAX_HISTORY:
        #summarize history
        summarize = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes conversation history into a concise format."},
                {"role": "user", "content": f"Summarize the following conversation history briefly:\n\n{history[1:-1]}"}
            ]
        )
        
        new_history = [history[0]]
        history = [new_history]
        history.append({"role": "system", "content": f"Summary of previous conversation: {summarize.choices[0].message.content}"})
    
    print("Bot: ", response.choices[0].message.content)
    