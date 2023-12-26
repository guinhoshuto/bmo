import os
import openai
from dotenv import load_dotenv
from rich import print

load_dotenv()

helicone_api_key = os.getenv('HELICONE_API_KEY')
openai.api_key = os.getenv('OPENAI_API_KEY')
openai.api_base = "https://oai.hconeai.com/v1"

async def get_completion(prompt, channelId, userId, system=None, history=None):
    print(channelId, userId)
    completion = openai.ChatCompletion.create(
        headers={
            "Helicone-Auth": "Bearer " + helicone_api_key,
            "Helicone-User-Id": str(userId),
            "Helicone-Property-Channel": str(channelId),
             "Helicone-Cache-Enabled": "true",
        },
        # model="gpt-3.5-turbo",
        model="gpt-4",
        messages=get_message(prompt, system, history)
    )
    # c = completion.choices[0].message.content
    response = {
        "message": completion.choices[0].message.content,
        "tokens": completion.usage
    }
    return response

def get_message(prompt, system=None, history=None):
    messages = []
    if history:
        print('---history---')
        for h in history:
            print(h["is_bot"])
            messages.append({"role": "system" if h["is_bot"] else "user", "content": h["content"]})
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    print(messages)
    return messages


