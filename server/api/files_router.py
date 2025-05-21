from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request, Form
from services.files_service import FilesService
from services.service_provider import ServiceProvider
from services.user_service import UserService
from typing import Optional
from util.utils import parse_boolean_string
from pydantic import BaseModel
from services.user_service import UserService
from services.files_service import FilesService
from services.supabase_service import SupabaseService
from fastapi import Query

router = APIRouter(prefix="/api/files", tags=["files"])
supabase = SupabaseService()


def get_files_service() -> FilesService:
    return ServiceProvider().files

def get_user_service() -> UserService:
    return UserService(ServiceProvider().supabase)

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



class DeleteSingleFileRequest(BaseModel):
    file_id: str



@router.delete("/delete-single/{file_id}")
async def delete_single_file(
    request: Request,
    file_id: str,
    user_service: UserService = Depends(get_user_service),
    files_service: FilesService = Depends(get_files_service)
):
    try:
        
        user_id, org_id = await user_service.verify_user_token(request)

        
        client = supabase.get_client()
        file_result = client.table("files_data") \
            .select("file_path, org_id") \
            .eq("id", file_id).execute()

        if not file_result.data or file_result.data[0]["org_id"] != org_id:
            raise HTTPException(status_code=403, detail="You are not authorized to delete this file")

        file_path = file_result.data[0]["file_path"]

        
        remove_result = client.storage.from_("files").remove([file_path])
        print(remove_result)
        if not remove_result or isinstance(remove_result, list) and len(remove_result) == 0:
            raise HTTPException(status_code=500, detail="Storage deletion failed or file not found.")
        
       
        client.table("files_data").delete().eq("id", file_id).execute()
        print(file_id)

        return {"message": "File deleted successfully"}

    except HTTPException as e:
        raise e
    except Exception as e:
        print("Error deleting file:", e)
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")




