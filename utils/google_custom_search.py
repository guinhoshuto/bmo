import os
import requests
from rich import print
from dotenv import load_dotenv

load_dotenv()

params = {
    "key": os.getenv('GOOGLE_SEARCH_API'),
    "cx": os.getenv('SEARCH_ENGINE_ID'),
}

def getSearchResults(q):
    params["q"] = q
    response = requests.get("https://www.googleapis.com/customsearch/v1", params=params)
    items = response.json().get("items")
    # print(response.json())
    return items

def searchForDiscord(q, lucky=False):
    response = ''
    items = getSearchResults(q)
    # print(items)
    for i, item in enumerate(items):
        response += f"{i} - [{item.get('title')} - {item.get('displayLink')}](<{item.get('link')}>) \n"
    return response
