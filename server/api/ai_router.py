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

router = APIRouter(prefix="/api/ai", tags=["ai"])

def get_ai_service() -> AIService:
    return AIService(SupabaseService())

def get_user_service() -> UserService:
    return UserService(SupabaseService())

@router.post("/", status_code=status.HTTP_200_OK) # response_model=AIResponse,
async def ai_prompt(
    request: Request,
    body: AIInput, 
    ai_service: AIService = Depends(get_ai_service),
    user_service: UserService = Depends(get_user_service),
):
    # Verify the user is authenticated
    user_id = await user_service.verify_user_token(request)
    print(user_id)
    
    # TODO Verify if the context is available to the org that the user is apart of 
    
    # Store the project metadata
    data = await ai_service.call(body)
    
    data = data.model_dump()
    
    print(data)
    
    good_json_string = repair_json(data['answer'])
    
    data['answer'] = json.loads(good_json_string)
    
    return data