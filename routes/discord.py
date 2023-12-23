from fastapi import APIRouter
import utils

router = APIRouter()
route = "/discord/"


@router.get(route)
async def hello():
    await utils.send_completion('uai')
    return 'oi'