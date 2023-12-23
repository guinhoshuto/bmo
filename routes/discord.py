from fastapi import APIRouter
from discord import getCompletion

router = APIRouter()
route = "/discord/"


@router.get(route)
async def hello():
    getCompletion('uai')
    return 'oi'