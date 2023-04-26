import os
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

def getCompletion(prompt, system=None):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=getMessage(prompt, system)
    )
    return completion

def getMessage(prompt, system=None):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    return messages