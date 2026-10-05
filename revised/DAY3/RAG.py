from openai import OpenAI
import os
from dotenv import load_dotenv
import numpy as np
import chromadb
from chromadb.utils import embedding_functions

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

texts = 'Quick brown fox jumps over the lazy dog. OpenAI creates powerful AI models.'

openai_em_function = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small"
)

chroma_client = chromadb.PersistentClient(path="./chroma_db")

collection = chroma_client.get_or_create_collection(
    name="knowledge_base",
    metadata={'description': 'Production RAG knowledge base example'},
    embedding_function=openai_em_function
)

def load_documents(folder_path):
    documents = []
    
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            filepath = os.path.join(folder_path, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                documents.append({
                    'filename': filename,
                    'content': content   
                })
                
    return documents

# documentss = [
#     {'filename': 'doc1.txt', 'content': 'This is the content of document one.}
# ]

def add_documents_to_db(folder_path):
    docs = load_documents(folder_path)
    
    all_chunks = []
    all_ids = []
    all_metadatas = []
    
    chunk_counter = 0
    
    for doc in docs:
        chunks = chunk_text(doc['content'])
        
        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_ids.append(f"chunk_{chunk_counter}")
            all_metadatas.append({
                'source': doc['filename'],
                'chunk_id': i
            })
            chunk_counter += 1
            
    collection.add(
        documents=all_chunks,
        ids=all_ids,
        metadatas=all_metadatas
    )
    
def chunk_text(text, chunk_size=800, overlap=150):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk)
            
        start += chunk_size - overlap
    return chunks

def get_embeddings(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    
    return response.data[0].embedding

def search(query, n_result=3):
    results = collection.query(
        query_texts=[query],
        n_results=n_result
    )
    
    relevant_chunks = []
    for i in range(len(results['documents'][0])):
        relevant_chunks.append({
            'text': results['documents'][0][i],
            'source': results['metadatas'][0][i]['source'],
            'distance': results['distances'][0][i]
        })
    
    return relevant_chunks

def generate_answer(history):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=history
    )
    
    return response.choices[0].message.content

def cosine_similarity(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    
    dot_product = np.dot(vec1, vec2)
    magnitude = np.linalg.norm(vec1) * np.linalg.norm(vec2)
    
    return dot_product / magnitude

def main():
    if collection.count() == 0:
        print("Database is empty. Adding documents...")
        add_documents_to_db('./knowledge_base')
        
    print("RAG ChatBot")
    
    history = [{
        'role': 'system', 
        'content': '''You are a professional and friendly customer service agent for this company. Answer in the language used by the user

    HOW TO ANSWER:
    1. Always greet with kindness and empathy.
    2. Answer based on the context provided.
    3. If information is not in context, politely state that you need to check further.
    4. Provide clear, structured, and easy-to-understand answers.
    5. Avoid using too many emojis. Only use relevant ones that convey emotion.
    6. Always offer additional assistance at the end of your answer.
    7. If there are numbers/dates/procedures, be specific.
    8. IMPORTANT: Don't make up information. Only use what is in context.

    LANGUAGE STYLE:
    - Formal but friendly.
    - End with a relevant follow-up question.

    EXAMPLE:
    "Thank you for your question! 😊
    According to our company policy, [specific answer from context]...
    Is there anything else I can help you with?'''
    }]
    
    while True:
        raw_query = input("You: ").strip()
        
        openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        prompt_enhancement = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {'role':'system', 'content':'You are a user question translator. Translate user questions from any language into English and make them clearer and more detailed.'},
                {'role':'user', 'content':raw_query},
            ],
            max_tokens=150
        )
        
        query = prompt_enhancement.choices[0].message.content
        
        if not query:
            continue
        
        results = search(query, n_result=3)
        
        context = "\n".join([chunk['text'] for chunk in results])
        
        user_prompt = f"""Customer question: {query}
        
        Context from knowledge base:
        {context}"""
        
        history.append({'role':'user', 'content':user_prompt})
        
        answer = generate_answer(history)
        
        history[-1] = {'role':'user', 'content':query}
        history.append({'role':'assistant','content': answer})

        print(f'AI: {answer}')

if __name__ == "__main__":
    main()