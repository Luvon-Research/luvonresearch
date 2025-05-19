from models.user import UserBase, UserCreated, IntegrationCreated
from fastapi import HTTPException, status
from services.supabase_service import SupabaseService
from clerk_backend_api import Clerk
from config import settings
from datetime import datetime
from typing import Optional


class UserService:
    def __init__(self, db: SupabaseService):
        self.db = db
        self.clerk = Clerk(settings.CLERK_API_SECRET_KEY)

    async def get_by_id(self, id: str):
        try:
            client = self.db.get_client()
            response = client.table('users').select("*").eq("id", id).execute()
            return response.data
        except Exception as e:
            print("get_by_id error:", e)
            return e

    async def verify_user_token(self, request):
        """
        returns user_id and org_id if valid
        """
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=401, detail="Missing or invalid Authorization header")

        session_token = auth_header.split(" ")[1]

        try:
            session = self.clerk.sessions.get(session_id=session_token)
            if not session:
                raise HTTPException(status_code=401, detail="Invalid session")
            return session.user_id, session.last_active_organization_id
        except Exception as e:
            raise HTTPException(status_code=401, detail=str(e))

    async def create(self, data: UserBase) -> UserCreated:
        try:
            client = self.db.get_client()
            response = client.table('users').insert(
                data.model_dump()).execute()
            return UserCreated(status="success", message="User created successfully")
        except Exception as e:
            if hasattr(e, 'code') and e.code == '23505':
                raise HTTPException(
                    status_code=status.HTTP_200_OK,
                    detail="User with that key already exists."
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something went wrong during user creation."
            )

    async def store_box_token(self, user_id: str, access_token: str, refresh_token: str, expires_at: str) -> IntegrationCreated:
        try:
            client = self.db.get_client()
            payload = {
                "user_id": user_id,
                "token": access_token,
                "refresh_token": refresh_token,
                "expires_at": expires_at,
                "integration": "box"
            }
            client.table('integrations').upsert(payload).execute()
            return IntegrationCreated(status="success", message="Box integration stored.")
        except Exception as e:
            print("store_box_token error:", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to store Box token."
            )

    async def get_box_token_record(self, user_id: str) -> Optional[dict]:
        try:
            client = self.db.get_client()
            response = client.table('integrations').select(
                "*").eq("user_id", user_id).eq("integration", "box").execute()
            if not response.data or len(response.data) == 0:
                return None
            return response.data[0]
        except Exception as e:
            print("get_box_token_record error:", e)
            return None
