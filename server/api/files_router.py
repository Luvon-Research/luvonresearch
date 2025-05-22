from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request, Form
from services.files_service import FilesService
from services.service_provider import ServiceProvider
from services.user_service import UserService
from typing import Optional
from services.pinecone_service import PineconeService
from util.utils import parse_boolean_string

router = APIRouter(prefix="/api/files", tags=["files"])

def get_files_service() -> FilesService:
    return FilesService(ServiceProvider().supabase, get_pinecone_service())

def get_user_service() -> UserService:
    return UserService(ServiceProvider().supabase)

def get_pinecone_service() -> PineconeService:
    return PineconeService()

@router.post("/upload")
async def upload_file(
    request: Request,
    org_id: str = Form(...),
    file: UploadFile = File(...),
    is_chart: bool = Form(...),
    service: FilesService = Depends(get_files_service),
    user_service: UserService = Depends(get_user_service)
):
    try:
        # Get the uploader_id from the authenticated user
        user_id, org_id_token = await user_service.verify_user_token(request)
        
        if(org_id_token != org_id):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

        file_content = await file.read()
        return await service.upload_file(org_id, user_id, file_content, file.filename, is_chart)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{org_id}")
async def get_files_by_organization(
    org_id: str,
    request: Request,
    service: FilesService = Depends(get_files_service),
    user_service: UserService = Depends(get_user_service)
):
    try:
        print("Gettign files")
        user_id, org_id_token = await user_service.verify_user_token(request)
        
        if(org_id_token != org_id):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
        
        is_chart = parse_boolean_string(request.headers.get("is_chart"))
        
        print(is_chart)

        files = await service.get_files_by_org_id(org_id, is_chart)
        
        if not files:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No files found for this organization")

        return files
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 
    
@router.get("/signed-url/{file_path}")
async def get_signed_url(
    file_path: str,
    service: FilesService = Depends(get_files_service)
):
    try:
        return await service.get_signed_url(file_path)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{org_id}/{file_id}")
async def delete_file(
    org_id: str,
    file_id: str,
    request: Request,
    service: FilesService = Depends(get_files_service),
    user_service: UserService = Depends(get_user_service)
):
    try:
        # Get the user_id from the authenticated user
        user_id, org_id_token = await user_service.verify_user_token(request)
        
        if(org_id_token != org_id):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

        # Get the file details first to get the file path
        client = service.get_client()
        is_chart = parse_boolean_string(request.headers.get("is_chart"))
        table_name = "charts" if is_chart else "files_data"
        
        # Get file details
        file_response = client.table(table_name).select("*").eq("id", file_id).execute()
        if not file_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
        
        file_data = file_response.data[0]
        
        # Delete from storage
        try:
            client.storage.from_('files').remove([file_data['file_path']])
        except Exception as e:
            print(f"Error deleting from storage: {e}")
            # Continue with database deletion even if storage deletion fails
        
        # Delete from database
        response = client.table(table_name).delete().eq("id", file_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete file metadata")
            
        return {"status": "success", "message": "File deleted successfully"}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
