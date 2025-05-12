from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request, Form
from services.files_service import FilesService
from services.service_provider import ServiceProvider
from services.chat_history_service import ChatHistoryService
from services.user_service import UserService
from models.chat_history import ChatHistory, ChatHistoryUpload

router = APIRouter(prefix="/api/chat", tags=["chat"])
supabase = ServiceProvider().supabase

def get_chat_history_service() -> ChatHistoryService:
    return ChatHistoryService(supabase)

def get_user_service() -> UserService:
    return UserService(supabase)

@router.post("/")
async def save_chat(
    request: Request,
    body: ChatHistoryUpload,
    chat_history_service: ChatHistoryService = Depends(get_chat_history_service),
    user_service: UserService = Depends(get_user_service)
):
    try:
        # Get the user_id from the authenticated user
        user, org = await user_service.verify_user_token(request)
        
        if(user != body.user_id):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Unauthorized user")

        return await chat_history_service.save_chat(body)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{user_id}/{page}")
async def get_chats_for_user(
    user_id: str,
    page: int,
    request: Request,
    user_service: UserService = Depends(get_user_service),
    chat_history_service: ChatHistoryService = Depends(get_chat_history_service)
):
    try:
        print("working...")
        # Get the user_id from the authenticated user
        user, org = await user_service.verify_user_token(request)
        
        if(user_id != user):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Unauthorized user")
            
        print(user, org)
        
        return await chat_history_service.get_chats_by_user(user_id, page)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 
    