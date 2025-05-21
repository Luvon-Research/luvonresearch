# app/api/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from fastapi import FastAPI, Request

from services.supabase_service import SupabaseService
from models.sheet import SheetRow, SheetRowUpdatedResponse, SheetRowUpdates, SheetCreate, SheetResponse
from services.sheet_service import SheetService
from services.user_service import UserService

router = APIRouter(prefix="/api/sheets", tags=["sheets"])
supabase = SupabaseService()

def get_sheet_service() -> SheetService:
    return SheetService(supabase)

def get_user_service() -> UserService:
    return UserService(supabase)

# TODO
# @router.get("/",)
# async def list_users(service: UserService = Depends(get_user_service)):
#     return {"status": "Hello there, TODO"}

@router.get("/{sheet_id}")
async def get_sheet(sheet_id: str, service: SheetService = Depends(get_sheet_service)):
    data = await service.get_sheet_data_by_id(sheet_id)
    return data

@router.post("/rows", response_model=SheetRowUpdatedResponse, status_code=status.HTTP_201_CREATED)
async def create_sheet_rows(u: SheetRowUpdates, request: Request, service: SheetService = Depends(get_sheet_service)):
    return await service.updateRowsBulk(u)

@router.post("/", response_model=SheetResponse, status_code=status.HTTP_201_CREATED)
async def create_sheet(
    sheet: SheetCreate, 
    request: Request, 
    service: SheetService = Depends(get_sheet_service),
    user_service: UserService = Depends(get_user_service)
):
    try:
        user_id, org_id = await user_service.verify_user_token(request)
        sheet.owner_id = user_id
    except HTTPException:
        pass
    
    return await service.create_sheet(sheet)

@router.get("/organization/{organization_id}")
async def get_sheets_by_organization(
    organization_id: str,
    request: Request,
    service: SheetService = Depends(get_sheet_service),
    user_service: UserService = Depends(get_user_service)
):
    # # Verify the user is authenticated
    # try:
    #     user_id = await user_service.verify_user_token(request)
    #     # You could add validation here to ensure the user belongs to this organization
    #     # This would need integration with your auth system (Clerk)
    # except HTTPException:
    #     # Continue without user ID if authentication fails
    #     raise HTTPException(status_code=401, detail="Authentication required")
    
    return await service.get_sheets_by_organization_id(organization_id)
@router.get("/export/{sheet_id}")
async def get_user(sheet_id: str, service: SheetService = Depends(get_sheet_service)):
    data = await service.get_sheet_data_csv_by_id(sheet_id)
    return data

@router.delete("/{sheet_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sheet(
    sheet_id: str,
    request: Request,
    service: SheetService = Depends(get_sheet_service),
    user_service: UserService = Depends(get_user_service)
):
    try:
        user_id, org_id = await user_service.verify_user_token(request)
        await service.delete_sheet(sheet_id)
        return {}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )