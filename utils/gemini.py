import os
from io import BytesIO
import requests
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_ONLY_HIGH"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_ONLY_HIGH"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_ONLY_HIGH"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_ONLY_HIGH"
  }
]


llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash",
                            temperature=0,
                            api_key=os.getenv('GEMINI_API_KEY'))

vision = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp",
                            temperature=0,
                            api_key=os.getenv('GEMINI_API_KEY'))

async def get_gemini_completion(prompt):
    response = llm.generate_content(prompt)
    return response.text

async def format_img_parts(att):
    response = requests.get(att.url)
    if response.status_code == 200:
        return [
            {
                "mime_type": att.content_type,
                "data": BytesIO(response.content).getvalue()
            },
        ]
    else: 
        return []


async def get_image_suggestions(msg):
    img_parts = await format_img_parts(msg.attachments[0])
    if msg.content:
        response = await get_gemini_vision_completion(img_parts, msg.content)
        return response
    else: 
        print('não falou nada')    
        response = await get_gemini_vision_completion(img_parts, 'Sobre o que trata a imagem?')
        return response

async def get_gemini_vision_completion(img_parts, prompt):
    prompt_parts = [
        prompt, 
        img_parts[0]
    ]
    response = vision.generate_content(prompt_parts)
    print(response.text)
    return response.text
