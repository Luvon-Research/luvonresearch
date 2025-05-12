from models.user import UserBase, UserCreated
from fastapi import HTTPException, status
from services.supabase_service import SupabaseService
from clerk_backend_api import Clerk
from config import settings

class UserService:
    def __init__(self, db: SupabaseService):
        self.db = db
        self.clerk = Clerk(settings.CLERK_API_SECRET_KEY)

    async def get_by_id(self, id:str):
        try:
            client = await self.db.get_client()
            query_builder = client.table('users').select("*").eq("id", id)
            response = query_builder.execute()
            return response.data
        except Exception as e:
            print(e)
            return e
    
    async def verify_user_token(self, request):
        """
        returns user_id if valid
        raises AuthenticationException otherwise
        """
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
        
        session_token = auth_header.split(" ")[1]
        
        try:
            session = self.clerk.sessions.get(session_id=session_token)
            print(session)
            if not session:
                raise HTTPException(status_code=401, detail="Invalid session")
            return session.user_id, session.last_active_organization_id
        
        except Exception as e:
            raise HTTPException(status_code=401, detail=str(e))
        
        
    async def create(self, data: UserBase) -> UserCreated:
        try:
            client = self.db.get_client()
            response = client.table('users').insert(data.model_dump()).execute()
            val = response.data
            print(val)
            return UserCreated(
                status = "success",
                message="User created successfully"
            )
        except Exception as e:
            print(e)
            if(e.code == '23505'): # Key already exists
                raise HTTPException(
                    status_code=status.HTTP_200_OK,
                    detail="User with that key already exists. No need to create.",
                    )
            else: 
                print(e)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Something went wrong...",
                )