import requests
import json
import discord
import io
from rich import print
from bs4 import BeautifulSoup

unwanted_tags = ['script', 'style', 'meta']
content_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']

def get_content(url):
    response = requests.get(url)
    main_content = ''
    soup = BeautifulSoup(response.content, 'html.parser') 
    for tag in unwanted_tags:
        for el in soup.select(tag):
           el.extract() 
    for tag in soup.select(','.join(content_tags)):
        main_content += tag.get_text()        
    print(main_content)
    return main_content

async def http_request(url, method='GET'):
    response = requests.get(url)
    response_type = response.headers.get("content-type").split(";")[0]
    match response_type:
        case "application/json":
            json_data = f'```json\n{json.dumps(response.json(), sort_keys=True, indent=2, separators=(",", ": "))} ```'
            if(len(json_data) > 1950):
                filename = "tmp/response.json"
                with open(filename, 'w') as f:
                    f.write(json.dumps(response.json()))
                return {
                    "is_file": True,
                    "message": discord.File("tmp/response.json", "response.json")
                }
            else: 
                print('aqui entrou')
                return {
                    "is_file": False,
                    "message": json_data
                }

        case "text/html":
            print("oi")
            print(response.content)
            return "oi"
        case "image/png":
            print(response.content)
            return "oi"
        case "audio/mpeg":
            audio_data = io.BytesIO(response.content)
            return {
                "is_file": True,
                "message": discord.File(audio_data, 'audio.mp3')
            }
    
