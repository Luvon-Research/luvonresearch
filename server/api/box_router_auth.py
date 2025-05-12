# box_auth_router.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.box_service import exchange_code_for_token
from services.box_service import list_user_files
import httpx


router = APIRouter(prefix="/api/box", tags=["box"])

class TokenExchangeRequest(BaseModel):
    code: str
    user_id: str

@router.post("/box/exchange")
async def box_token_exchange(request: TokenExchangeRequest):
    try:
        token_data = await exchange_code_for_token(request.code, request.user_id)
        return {"message": "Box token stored", "access_token": token_data["access_token"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


    
@router.get("/files/{user_id}")
async def get_box_files(user_id: str):
    access_token = "Rsg5EG3y3G3iwypQF9OOA0kkKzxWnulX"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        res = await client.get("https://api.box.com/2.0/folders/0/items", headers=headers)
    return res.json()

