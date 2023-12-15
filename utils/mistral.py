import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('MISTRAL_API_KEY')
headers={
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    "Authorization": "Bearer " + api_key
}

async def get_mistral_completion(prompt, model):
    print(prompt, model)
    completion = requests.post('https://api.mistral.ai/v1/chat/completions', 
        headers=headers,
        json={
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ] 
        }
    )
    tmp = completion.json()
    response = {
        "message": tmp["choices"][0]["message"]["content"],
        "tokens": tmp["usage"]["total_tokens"]
    }
    return response