from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

#CONSTANTS
MAX_HISTORY = 2 * 2 + 1
SUMMARIZE_PROMPT = "You are a helpful assistant that summarizes conversation history into a concise format."

history = [
    {"role": "system", "content": "You are a helpful assistant."},
]

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def stream_chat_response(messages):
    full_response = ""
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        stream=True
    )
    
    for chunk in response:
        content = chunk.choices[0].delta.content
        if content is not None:
            # Stream tokens to console as they arrive
            print(content, end='', flush=True)
            full_response += content
            
    return full_response
    
def main():
    global history
    while True:
        user_chat = input("You: ").strip()
        
        if user_chat.lower() == '/bye':
            print("Exiting the chat. Goodbye!")
            break
        
        history.append({"role": "user", "content": user_chat})
        print("AI: ", end='', flush=True)
        full_response = stream_chat_response(history)
        print()
        history.append({"role": "assistant", "content": full_response})
        
        # print("\n\n History: " + str(history))
        
        if len(history) > MAX_HISTORY:
            summarize = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SUMMARIZE_PROMPT},
                    {"role": "user", "content": f"Summarize the following conversation history briefly:\n\n{history[1:-1]}"}
                ]
            )
            # print("\n\n Summarize: " + summarize.choices[0].message.content)
            history = [
                {"role": "system", "content": f"Summary of previous conversation: {summarize.choices[0].message.content}"}
            ] + history[-1:]
        
if __name__ == "__main__":
    main()