import os
import requests
from dotenv import load_dotenv

load_dotenv()

async def push():
    requests.post(
        'https://api.pushcut.io/' + os.getenv('PUSHCUT_SECRET') + '/notifications/test',
    )