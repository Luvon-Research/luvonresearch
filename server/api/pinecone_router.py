from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List
from models.pinecone import QueryRequest, QueryResponse
from models.project import ProjectBase, ProjectCreated
from services.project_service import ProjectService
from services.user_service import UserService
from services.service_provider import ServiceProvider
from services.pinecone_service import PineconeService

router = APIRouter(prefix="/api/pinecone", tags=["pinecone"])
#supabase = SupabaseService()

def get_pinecone_service() -> PineconeService:
    return PineconeService()

def get_user_service() -> UserService:
    return UserService(ServiceProvider().supabase)

@router.post("/query", response_model=QueryResponse)
async def query_pinecone(
    request: Request, 
    body: QueryRequest,
    pinecone_service: PineconeService = Depends(get_pinecone_service),
    user_service: UserService = Depends(get_user_service)
):
    # Verify the user is authenticated
    user_id, org_id = await user_service.verify_user_token(request)
    
    if(org_id != body.namespace):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    # Store the project metadata
    return await pinecone_service.query_vectors(body.prompt, namespace=org_id, top_k=body.top_k)