import os
import openai
from dotenv import load_dotenv
from rich import print

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

async def get_completion(prompt, system=None, history=None):
    completion = openai.ChatCompletion.create(
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
        print(history)
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    return messages


