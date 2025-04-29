# app/api/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from services.supabase_service import SupabaseService
from models.user import UserBase, UserCreated
from services.user_service import UserService

router = APIRouter(prefix="/api/users", tags=["users"])

def get_user_service() -> UserService:
    return UserService(SupabaseService())

@router.get("/",)
async def list_users(service: UserService = Depends(get_user_service)):
    return await service.get_all()

@router.get("/{user_id}")
async def get_user(user_id: str, service: UserService = Depends(get_user_service)):
    print("GETTING", user_id)
    user = await service.get_by_id(user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return user

@router.post("/", response_model=UserCreated, status_code=status.HTTP_201_CREATED)
async def create_user(u: UserBase, service: UserService = Depends(get_user_service)):
    print("WORKING...")
    return await service.create(u)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, service: UserService = Depends(get_user_service)):
    # will raise if not found / error
    if not await service.get_by_id(user_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    await service.delete(user_id)
