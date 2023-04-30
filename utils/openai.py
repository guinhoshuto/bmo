import os
import openai
from dotenv import load_dotenv
from rich import print

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

async def getCompletion(prompt, system=None):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=getMessage(prompt, system)
    )
    # c = completion.choices[0].message.content
    return completion

def getMessage(prompt, system=None):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    return messages
