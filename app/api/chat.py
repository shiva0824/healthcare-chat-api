from fastapi import APIRouter

router = APIRouter()

@router.get("/placeholder")
def placeholder():
    return {"message": "Chat endpoints will be implemented later."}