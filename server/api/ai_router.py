from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List
from services.supabase_service import SupabaseService
from models.project import ProjectBase, ProjectCreated
from services.project_service import ProjectService
from services.ai_tools_service import AIService
from models.ai import AIResponse, AIInput
from fastapi.responses import FileResponse

router = APIRouter(prefix="/api/ai", tags=["ai"])

def get_ai_service() -> AIService:
    return AIService(SupabaseService())

@router.post("/", status_code=status.HTTP_200_OK) # response_model=AIResponse,
async def ai_prompt(
    request: AIInput, 
    ai_service: AIService = Depends(get_ai_service),
):
    # Verify the user is authenticated
    #user_id = await user_service.verify_user_token(request)
    
    # Set the user_id in the project data
    #project.user_id = user_id
    
    # Store the project metadata
    data = await ai_service.call(request.prompt) #project_service.create(project)
    
    return data.model_dump()