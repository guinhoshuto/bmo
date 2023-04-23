import os
from decouple import config
from fastapi import FastAPI
from pydantic import BaseModel
# import discord
import lib

if __name__ == '__main__':
    print('era pra entrar aqui')
    lib.run_bot()
# from dotenv import load_dotenv

# load_dotenv()
# intents = discord.Intents.default()
# intents.message_content = True
# intents.members = True

# client = discord.Client(intents=intents)
# client.run(os.getenv('DISCORD_TOKEN'))

app = FastAPI()
# lib.connect()
class Msg(BaseModel):
    msg: str


@app.get("/")
async def root():
    response = lib.getCompletion('quanto é 2 + 2')
    return {'msg': response}
    # return {"message": "Hello World. Welcome to FastAPI!"}


@app.get("/path")
async def demo_get():
    return {"message": "This is /path endpoint, use a post request to transform the text to uppercase"}


@app.post("/path")
async def demo_post(inp: Msg):
    return {"message": inp.msg.upper()}


@app.get("/path/{path_id}")
async def demo_get_path_id(path_id: int):
    return {"message": f"This is /path/{path_id} endpoint, use post request to retrieve result"}
