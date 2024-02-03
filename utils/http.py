import requests
import json
import discord
import io
from os import path
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
    response_type = response.headers.get("content-type").split(";")[0].split("/")
    print(response_type)
    match response_type[0]:
        case "application":
            json_data = f'```json\n{json.dumps(response.json(), sort_keys=True, indent=2, separators=(",", ": "))} ```'
            if(len(json_data) > 1950):
                file = path.join("tmp", "response.json")
                with open(file, 'w') as f:
                    f.write(json.dumps(response.json()))

                with open(file, 'rb') as f:
                    file = discord.File(f)

                is_file = True
                message = file
            else: 
                is_file = False
                message = json_data

        case "text":
            filename = f'/tmp/text.{response_type[1]}'
            file = path.join("tmp", f'text,{response_type[1]}')
            with open(filename, 'w') as f:
                f.write(response.text)

            with open(filename, 'rb') as f:
                file = discord.File(f, f'text.{response_type[1]}')

            is_file = True
            message = file
        case "image":
            format = response_type[1]
            img = io.BytesIO(response.content)
            is_file = True
            message = discord.File(img, f'img.{format}')
        case "audio":
            format = response_type[1]
            if(response_type[1] == 'mpeg'):
                format = 'mp3'
            audio_data = io.BytesIO(response.content)
            is_file = True
            message = discord.File(audio_data, f'audio.{format}')
    
    return {
        "is_file": is_file,
        "message": message
    }
