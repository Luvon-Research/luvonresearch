from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request, Form
from services.files_service import FilesService
from services.service_provider import ServiceProvider
from services.user_service import UserService

router = APIRouter(prefix="/api/files", tags=["files"])

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
        uploader_id = await user_service.verify_user_token(request)

        file_content = await file.read()
        return await service.upload_file(org_id, uploader_id, file_content, file.filename, is_chart)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{org_id}")
async def get_files_by_organization(
    org_id: str,
    service: FilesService = Depends(get_files_service)
):
    try:
        files = await service.get_files_by_org_id(org_id)
        
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
