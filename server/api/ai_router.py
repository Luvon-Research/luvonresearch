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
from util.utils import check_user_connected
from services.pinecone_service import PineconeService
from services.e2b_service import E2BService
from fastapi.responses import StreamingResponse


router = APIRouter(prefix="/api/ai", tags=["ai"])

supabase = SupabaseService()

def get_e2b_service() -> E2BService:
    return E2BService()

def get_pinecone_service() -> PineconeService:
    return PineconeService()

# e2bService = get_e2b_service()
pineconeService = get_pinecone_service()

def get_ai_service() -> AIService:
    return AIService(supabase, pineconeService)

def get_user_service() -> UserService:
    return UserService(supabase)

def get_chat_history_service() -> ChatHistoryService:
    return ChatHistoryService(supabase)

@router.post("/", status_code=status.HTTP_200_OK)
async def ai_prompt(
    request: Request,
    body: AIInput, 
    ai_service: AIService = Depends(get_ai_service),
    user_service: UserService = Depends(get_user_service),
    chat_history_service: ChatHistoryService = Depends(get_chat_history_service)
):
    try:
        # Verify the user is authenticated
        user, org = await user_service.verify_user_token(request)
        print(user, org)
        
        # TODO Verify if the context is available to the org that the user is apart of 
        
        ### Saves the user message
        user_message_content = [
            {"type" : "message", "value" : body.prompt}
        ]
        user_chat = ChatHistoryUpload(org_id=org,
                                user_id=user,
                                message=user_message_content, # Ensure this is a list of dicts
                                generation_time=0,
                                from_type='user',
                                chat_id="TODO") # chat_id still needs proper handling
        
        await chat_history_service.save_chat(user_chat)
        
        start_time = time.time()
        
        ai_call_generator = ai_service.call(body, user, org, request)
        
        # Pass necessary args for chat history saving within the generator wrapper
        response_generator_with_history = stream_ai_response(
            request,  # Pass the current request object
            ai_call_generator, 
            chat_history_service, 
            org, 
            user, 
            start_time
        )
        
        return StreamingResponse(
            response_generator_with_history,
            media_type="application/x-ndjson"
        )
    
    except Exception as e:
        print("FAILED AI ROUTER", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

async def stream_ai_response(request_obj: Request, ai_service_call_generator, chat_history_service, org, user, start_time):
    accumulated_response_chunks = []
    try:
        async for chunk in ai_service_call_generator:
            accumulated_response_chunks.append(chunk)
            yield json.dumps(chunk) + "\n"
            await check_user_connected(request_obj)
    finally:
        end_time = time.time()
        if accumulated_response_chunks:
            assistant_chat = ChatHistoryUpload(
                org_id=org,
                user_id=user,
                message=accumulated_response_chunks,
                generation_time=end_time - start_time,
                from_type='assistant',
                chat_id="TODO"
            )
            try:
                await chat_history_service.save_chat(assistant_chat)
            except Exception as e:
                print(f"Failed to save chat history: {e}")
