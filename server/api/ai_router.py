from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List
from services.supabase_service import SupabaseService
from models.project import ProjectBase, ProjectCreated
from services.project_service import ProjectService
from services.ai_tools_service import AIService
from services.user_service import UserService
from models.ai import AIResponse, AIInput
from fastapi.responses import FileResponse
import json
from json_repair import repair_json
from models.chat_history import ChatHistoryUpload
from services.chat_history_service import ChatHistoryService
import time 
from services.pinecone_service import PineconeService
from services.e2b_service import E2BService

router = APIRouter(prefix="/api/ai", tags=["ai"])

supabase = SupabaseService()

def get_e2b_service() -> E2BService:
    return E2BService()

def get_pinecone_service() -> PineconeService:
    return PineconeService()

e2bService = get_e2b_service()
pineconeService = get_pinecone_service()

def get_ai_service() -> AIService:
    return AIService(supabase, pineconeService, e2bService)

def get_user_service() -> UserService:
    return UserService(supabase)

def get_chat_history_service() -> ChatHistoryService:
    return ChatHistoryService(supabase)

@router.post("/", status_code=status.HTTP_200_OK) # response_model=AIResponse,
async def ai_prompt(
    request: Request,
    body: AIInput, 
    ai_service: AIService = Depends(get_ai_service),
    user_service: UserService = Depends(get_user_service),
    chat_history_service: ChatHistoryService = Depends(get_chat_history_service)
):
    # Verify the user is authenticated
    user, org = await user_service.verify_user_token(request)
    print(user, org)
    
    # TODO Verify if the context is available to the org that the user is apart of 
    
    ### Saves the user message
    msg = [
        {"type" : "message", "value" : body.prompt}
    ]
    user_chat = ChatHistoryUpload(org_id=org,
                            user_id=user,
                            message=msg,
                            generation_time=0,
                            from_type='user',
                            chat_id="TODO")
    
    await chat_history_service.save_chat(user_chat)
    
    start = time.time()
    # Store the project metadata
    data = await ai_service.call(body, user, org)
    
    data = data.model_dump()
    
    print(data)
    
    good_json_string = repair_json(data['answer'])
    
    data['answer'] = json.loads(good_json_string)
    
    end = time.time()
    
    assistant_chat = ChatHistoryUpload(org_id=org,
                        user_id=user,
                        message=data['answer'],
                        generation_time=end-start,
                        from_type='assistant',
                        chat_id="TODO")

    await chat_history_service.save_chat(assistant_chat)

    return data