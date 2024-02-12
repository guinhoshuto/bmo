import requests
import logging
import http.client as http_client
import json
import discord
import io
from os import path
from rich import print
from bs4 import BeautifulSoup

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

unwanted_tags = ['script', 'style', 'meta']
content_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']

def get_content(url, method, body=None, params=None):
    # response = requests.get(url)
    response = requests(method, url=url)
    main_content = ''
    soup = BeautifulSoup(response.content, 'html.parser') 
    for tag in unwanted_tags:
        for el in soup.select(tag):
           el.extract() 
    for tag in soup.select(','.join(content_tags)):
        main_content += tag.get_text()        
    print(main_content)
    return main_content

async def http_request(url, method='GET', body=None, params=None, header=None):
    print(url, method, body, params)
    settings = {}
    if(body):
        settings['data'] = json.dumps(parse_params(body))
    if(params):
        settings['params'] = parse_params(params)
    if(header):
        settings['headers'] = parse_params(header)
    print(settings)
    response = requests.request(method, url=url, data=settings)
    response_type = response.headers.get("content-type").split(";")[0].split("/")
    print(response_type)
    match response_type[0]:
        case "application":
            json_data = f'```json\n{json.dumps(response.json(), sort_keys=True, indent=2, separators=(",", ": "))} ```'
            if(len(json_data) > 1950):
                # filename = path.join("tmp", "response.json")
                filename = '/tmp/response.json'
                with open(filename, 'w') as f:
                    f.write(json.dumps(response.json()))

                with open(filename, 'rb') as f:
                    file = discord.File(f, f'response.json')

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

def parse_params(params):
    attributes = {}
    attrs = str(params).split(",")
    for attr in attrs:
        print(attr)
        tmp = attr.split("=")
        attributes[tmp[0]] = tmp[1]
    return attributes