# app/api/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from fastapi import FastAPI, Request

from services.supabase_service import SupabaseService
from models.sheet import SheetRow, SheetRowUpdatedResponse, SheetRowUpdates
from services.sheet_service import SheetService
from fastapi.responses import JSONResponse
from fastapi import Form

from fastapi import APIRouter, Depends, UploadFile, File, Form, Request, status, HTTPException
from fastapi.responses import JSONResponse
from services.supabase_service import SupabaseService
from services.sheet_service import SheetService  # or FileService if it's separate

router = APIRouter(prefix="/api/sheets", tags=["sheets"])

def get_sheet_service() -> SheetService:
    return SheetService(SupabaseService())

# TODO
# @router.get("/",)
# async def list_users(service: UserService = Depends(get_user_service)):
#     return {"status": "Hello there, TODO"}

@router.get("/{sheet_id}")
async def get_user(sheet_id: str, service: SheetService = Depends(get_sheet_service)):
    data = await service.get_sheet_data_by_id(sheet_id)
    return data

@router.post("/rows", response_model=SheetRowUpdatedResponse, status_code=status.HTTP_201_CREATED)
async def create_user(u: SheetRowUpdates, request: Request, service: SheetService = Depends(get_sheet_service)):
    return await service.updateRowsBulk(u)

@router.get("/export/{sheet_id}")
async def get_user(sheet_id: str, service: SheetService = Depends(get_sheet_service)):
    data = await service.get_sheet_data_csv_by_id(sheet_id)
    return data



def get_sheet_service() -> SheetService:
    return SheetService(SupabaseService())

# ✅ Upload any file (PDF, image, CSV...) to Supabase + log metadata
@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_sheet_file(
    file: UploadFile = File(...),
    project_id: str = Form(...),
    org_id: str = Form(...),
    uploader_id: str = Form(...),
    uploaded_by: str = Form(...),
    service: SheetService = Depends(get_sheet_service)
):
    """
    Uploads any file to Supabase Storage and logs metadata in the 'files' table.
    Accepts file, project_id, org_id, uploader_id, and uploaded_by as form fields.
    """
    result = await service.uplaod_file(file, project_id, org_id, uploader_id, uploaded_by)
    return JSONResponse(content=result)




# # TODO
# @router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_user(user_id: str, service: UserService = Depends(get_user_service)):
#     # will raise if not found / error
#     if not await service.get_by_id(user_id):
#         raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
#     await service.delete(user_id)
