from typing import List, Optional
from models.user import UserBase, UserCreated, UserSearchByID
from fastapi import APIRouter, Depends, HTTPException, status
from services.supabase_service import SupabaseService

class UserService:
    def __init__(self, db: SupabaseService):
        self.db = db

    async def get_by_id(self, id:str):
        print("GETTING 2", id)
        try:
            val = await self.db.fetch_user_by_id(table_name='users', id=id)
            print(val)
            return val
        except Exception as e:
            print(e)
            return e
        
    async def create(self, data: UserBase) -> UserCreated:
        try:
            val = await self.db.insert_data(table_name='users', data=data.model_dump())
            print(val)
            return UserCreated(
                status = "success",
                message="User created successfully"
            )
        except Exception as e:
            if(e.code == '23505'): # Key already exists
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User with that key already exists",
                    )
            else: 
                print(e)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Something went wrong...",
                )