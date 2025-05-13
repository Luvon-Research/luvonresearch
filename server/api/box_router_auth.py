# box_auth_router.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.box_service import exchange_code_for_token
from services.box_service import list_user_files
import httpx
from services.supabase_service import SupabaseService
from services.user_service import UserService
from fastapi import APIRouter, Depends, HTTPException, status, Request

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
        user_id, org_id_token = await user_service.verify_user_token(request)
        token_data = await exchange_code_for_token(body.code, body.user_id)
        access_token = token_data["access_token"]
        
        await user_service.store_box_token(user_id,access_token)
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

@router.get("/has_integration/{user_id}")
async def has_box_integration(request: Request,user_id: str, service: UserService = Depends(get_user_service)):
    
    user_id, org_id = await service.verify_user_token(request)
    from services.supabase_service import SupabaseService
    supabase = SupabaseService()

    result = supabase.get_client().table("integrations").select("token").eq("user_id", user_id).execute()
    has_integration = result.data is not None and len(result.data) > 0
    return {"has_integration": has_integration}
