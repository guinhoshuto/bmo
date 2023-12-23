from fastapi import APIRouter
from pydantic import BaseModel
import utils

router = APIRouter()
route = "/discord/"

class Prompt(BaseModel):
    prompt: str
    api: str | None = None


@router.get(route)
async def hello():
    return 'oi'

@router.post(route + 'completion')
async def ask_bmo_completion(prompt: Prompt):
    if prompt.api is None:
        prompt.api = 'openai'
    await utils.send_completion(prompt.prompt, prompt.api)
    return 'enviou' 