# box_auth_router.py
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from datetime import datetime, timedelta
import httpx
from services.box_service import exchange_code_for_token
from services.supabase_service import SupabaseService
from services.user_service import UserService
import os
from dotenv import load_dotenv
load_dotenv()


router = APIRouter(prefix="/api/box", tags=["box"])
supabase = SupabaseService()


def get_user_service() -> UserService:
    return UserService(supabase)


class TokenExchangeRequest(BaseModel):
    code: str
    user_id: str


@router.post("/exchange")
async def box_token_exchange(
    request: Request,
    body: TokenExchangeRequest,
    user_service: UserService = Depends(get_user_service)
):
    try:
        user_id, _ = await user_service.verify_user_token(request)
        token_data = await exchange_code_for_token(body.code, body.user_id)

        access_token = token_data["access_token"]
        refresh_token = token_data["refresh_token"]
        expires_in = token_data["expires_in"]
        expires_at = (datetime.utcnow() +
                      timedelta(seconds=expires_in)).isoformat()

        await user_service.store_box_token(
            user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at
        )

        return {"message": "Box token stored", "access_token": access_token}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/has_integration/")
async def has_box_integration(
    request: Request,
    user_service: UserService = Depends(get_user_service)
):
    try:
        user_id, _ = await user_service.verify_user_token(request)
        token_info = await user_service.get_box_token_record(user_id)

        if not token_info:
            return {"has_integration": False, "access_token": None}

        access_token = token_info["token"]
        refresh_token = token_info.get("refresh_token")
        expires_at_str = token_info.get("expires_at")

        now = datetime.utcnow()
        token_expired = not expires_at_str or datetime.fromisoformat(
            expires_at_str) < now

        if token_expired:
            response = await httpx.AsyncClient().post("https://api.box.com/oauth2/token", data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": os.getenv("BOX_CLIENT_ID"),
                "client_secret": os.getenv("BOX_CLIENT_SECRET")
            })

            if response.status_code != 200:
                raise HTTPException(
                    status_code=500, detail="Failed to refresh Box token")

            refreshed = response.json()
            access_token = refreshed["access_token"]
            new_refresh_token = refreshed["refresh_token"]
            new_expires_at = (
                now + timedelta(seconds=refreshed["expires_in"])).isoformat()

            supabase.get_client().table("integrations").update({
                "token": access_token,
                "refresh_token": new_refresh_token,
                "expires_at": new_expires_at
            }).eq("user_id", user_id).eq("integration", "box").execute()

        return {"has_integration": True, "access_token": access_token}

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500, detail=f"Box integration check failed: {str(e)}")
        



    
@router.get("/files/{user_id}")
async def get_box_files(user_id: str):
    access_token = "Rsg5EG3y3G3iwypQF9OOA0kkKzxWnulX"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        res = await client.get("https://api.box.com/2.0/folders/0/items", headers=headers)
    return res.json()





@router.get("/token_status")
async def box_token_status(
    request: Request,
    user_service: UserService = Depends(get_user_service)
):
    user_id, _ = await user_service.verify_user_token(request)
    token_data = await user_service.get_box_token_record(user_id)

    if not token_data:
        return {"message": "No Box integration found."}

    return {
        "token": token_data.get("token"),
        "refresh_token": token_data.get("refresh_token"),
        "expires_at": token_data.get("expires_at"),
    }






