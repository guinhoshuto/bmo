import os
from openai import OpenAI
from dotenv import load_dotenv
from rich import print

load_dotenv()

helicone_api_key = os.getenv('HELICONE_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')

async def get_completion(prompt, channelId, userId, system=None, history=None):
    print(channelId, userId)
    try:
        # Create client with Helicone proxy and custom headers
        client = OpenAI(
            api_key=openai_api_key,
            base_url="https://oai.hconeai.com/v1",
            default_headers={
                "Helicone-Auth": f"Bearer {helicone_api_key}" if helicone_api_key else "",
                "Helicone-User-Id": str(userId),
                "Helicone-Property-Channel": str(channelId),
                "Helicone-Cache-Enabled": "true",
            }
        )
        
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=get_message(prompt, system, history)
        )
    except Exception as e:
        print(e)
        raise
    response = {
        "message": completion.choices[0].message.content,
        "tokens": {
            "prompt_tokens": completion.usage.prompt_tokens,
            "completion_tokens": completion.usage.completion_tokens,
            "total_tokens": completion.usage.total_tokens
        }
    }
    print(response["message"])
    return response

def get_message(prompt, system=None, history=None):
    messages = []
    if history:
        for h in history:
            messages.append({"role": "assistant" if h["is_bot"] else "user", "content": h["content"]})
        messages.pop()
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    print(messages)
    return messages


