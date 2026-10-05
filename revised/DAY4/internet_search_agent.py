from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import math
import requests
from ddgs import DDGS
import trafilatura

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL_NAME = "gpt-4o-mini"

def web_search(query_text: str, max_results: int=3) -> list:
    results = []
    with DDGS() as search_engine:
        for result in search_engine.texts(query_text, max_results=max_results):
            results.append({
                'title': result.get('title'),
                'url': result.get('href'),
                'snippet': result.get('body'),
                'source': 'duckduckgo'
            })
    return results

def fetch_webpage_content(url: str, max_length: int=1000) -> str:
    try:
        response = requests.get(
            url=url, 
            timeout=5,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
        )
        response.raise_for_status()
        
        extracted_content = trafilatura.extract(
            response.text,
            include_comments=False,
            include_tables=False,
        )
        
        if not extracted_content:
            return {
                'url': url,
                'ok': False,
                'content': 'Gagal Mengekstrak teks dari halaman web.'
            }
            
        clean_content = extracted_content.strip()
        if len(clean_content) > max_length:
            clean_content = clean_content[:max_length]
        
        return {
            'url': url,
            'ok': True,
            'content': clean_content
        }
        
    except requests.RequestException:
        return {
            'url': url,
            'ok': False,
            'content': 'Gagal Mengekstrak teks dari halaman web.'
        }
        
TOOLS = [
    {
        'type': 'function',
        'function': {
            'name': 'web_search',
            'description': 'Mencari informasi terkini di internet.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'query_text': {
                        'type': 'string',
                        'description': 'Kata kunci pencarian'
                    },
                    'max_results': {
                        'type': 'integer',
                        'minimum': 1,
                        'maximum': 5,
                        'default': 3,
                        'description': 'Jumlah hasil pencarian maksimum yang diinginkan',
                    }
                },
                'required': ['query_text']
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'fetch_webpage_content',
            'description': 'Mengambil dan Mengekstrak teks dari halaman web yang diberikan URL-nya.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'url': {
                        'type': 'string',
                        'description': 'URL halaman web yang akan diambil kontennya',
                    },
                    'max_length': {
                        'type': 'integer',
                        'minimum': 100,
                        'maximum': 5000,
                        'default': 1000,
                        'description': 'Panjang maksimum teks yang akan diekstrak dari halaman web',
                    }
                },
                'required': ['url']
            }
        }
    } 
]

PYTHON_FUNCTION = {
    'web_search': web_search,
    'fetch_webpage_content': fetch_webpage_content
}

def call_llm(messages_history):
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages_history,
        tools=TOOLS,
        tool_choice="auto"
    )
    
    return response

# response.choices[0].message.content
# response.choices[0].finish_reason -> "status"
# response.choices[0].message.tool_calls.id -> list of tool calls

def execute_tool_calls(message_history, assistant_message, tool_calls):
    message_history.append({
        'role': 'assistant',
        'content': assistant_message.content,
        'tool_calls': [
            {
                'id': call.id,
                'type': 'function',
                'function': {
                    'name': call.function.name,
                    'arguments': call.function.arguments
                }
            }
            
            for call in tool_calls    
        ]
    })
    
    for call in tool_calls:
        tool_name = call.function.name
        tool_arguments = json.loads(call.function.arguments or '{}')
        python_function = PYTHON_FUNCTION.get(tool_name)
        result = python_function(**tool_arguments) # -> PYTHON_FUNCTION = {'web_search': web_search, 'fetch_webpage_content': fetch_webpage_content}
                                                   # -> web_search, fetch_webpage_content
        
        
        message_history.append({
            'role': 'tool',
            'tool_call_id': call.id,
            'name': tool_name,
            'content': json.dumps(
                result,
                ensure_ascii=False
            )
        })
        
        return message_history