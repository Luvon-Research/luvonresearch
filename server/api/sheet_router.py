# app/api/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from fastapi import FastAPI, Request

from services.supabase_service import SupabaseService
from models.sheet import SheetRow, SheetRowUpdatedResponse, SheetRowUpdates, SheetCreate, SheetResponse
from services.sheet_service import SheetService
from services.user_service import UserService

router = APIRouter(prefix="/api/sheets", tags=["sheets"])

def get_sheet_service() -> SheetService:
    return SheetService(SupabaseService())

def get_user_service() -> UserService:
    return UserService()

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
    # Get the user ID from the authentication token
    try:
        user_id = await user_service.verify_user_token(request)
        sheet.owner_id = user_id
    except HTTPException:
        # Continue without user ID if authentication fails
        pass
    
    return await service.create_sheet(sheet)


# # TODO
# @router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_user(user_id: str, service: UserService = Depends(get_user_service)):
#     # will raise if not found / error
#     if not await service.get_by_id(user_id):
#         raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
#     await service.delete(user_id)
