import asyncio
from fastapi import FastAPI
import utils
from routes import discord

app = FastAPI()

app.include_router(discord.router)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(utils.run_bot())


