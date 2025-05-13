from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List
from services.supabase_service import SupabaseService
from models.project import ProjectBase, ProjectCreated
from services.project_service import ProjectService
from services.user_service import UserService

router = APIRouter(prefix="/api/projects", tags=["projects"])
supabase = SupabaseService()

def get_project_service() -> ProjectService:
    return ProjectService(supabase)

def get_user_service() -> UserService:
    return UserService(supabase)

@router.post("/", response_model=ProjectCreated)
async def create_project(
    project: ProjectBase, 
    request: Request, 
    project_service: ProjectService = Depends(get_project_service),
    user_service: UserService = Depends(get_user_service)
):
    # Verify the user is authenticated
    user_id, org_id = await user_service.verify_user_token(request)
    
    # Set the user_id in the project data
    project.user_id = user_id
    
    # Store the project metadata
    return project_service.create(project)

@router.get("/")
async def get_user_projects(
    request: Request,
    project_service: ProjectService = Depends(get_project_service),
    user_service: UserService = Depends(get_user_service)
):
    # Verify the user is authenticated
    user_id, org_id = await user_service.verify_user_token(request)
    
    # Get the user's projects
    return project_service.get_user_projects(user_id)

@router.get("/{project_id}")
async def get_project(
    project_id: str,
    request: Request,
    project_service: ProjectService = Depends(get_project_service),
    user_service: UserService = Depends(get_user_service)
):
    # Verify the user is authenticated
    user_id, org_id = await user_service.verify_user_token(request)
    
    # Get the project
    project = project_service.get_by_id(project_id)
    
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    # TODO: Check if user has access to this project
    # You could use Clerk API to verify membership
    
    return project 