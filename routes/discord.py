from fastapi import APIRouter

router = APIRouter()
route = "/discord/"


@router.get(route)
async def hello():
    return 'oi'