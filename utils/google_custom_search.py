import os
import requests
from rich import print
from dotenv import load_dotenv

load_dotenv()

params = {
    "key": os.getenv('GOOGLE_SEARCH_API'),
    "cx": os.getenv('SEARCH_ENGINE_ID'),
}

def get_search_results(q):
    params["q"] = q
    response = requests.get("https://www.googleapis.com/customsearch/v1", params=params)
    items = response.json().get("items")
    # print(response.json())
    return items

def search_for_discord(q):
    message = ''
    items = get_search_results(q)
    for i, item in enumerate(items):
        message += f"{i} - [{item.get('title')} - **{item.get('displayLink')}**](<{item.get('link')}>) \n"
    return {"message": message, "items": items}
