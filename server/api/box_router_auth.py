# box_auth_router.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.box_service import exchange_code_for_token

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
