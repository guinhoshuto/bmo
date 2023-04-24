import os
import asyncio
from fastapi import FastAPI
import utils

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(utils.run_bot())


@app.get("/")
async def read_root():
  return {"Hello": 'oi'}
