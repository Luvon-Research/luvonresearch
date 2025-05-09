from fastapi import HTTPException, status
from services.supabase_service import SupabaseService
from models.chat_history import ChatHistoryUpload, ChatHistory
from typing import Optional, Dict, Any

class ChatHistoryService:
    def __init__(self, db: SupabaseService):
        self.db = db

    async def save_chat(self, data: ChatHistoryUpload):
        try:
            client = self.db.get_client()
            
            payload = {
                       'org_id' : data.org_id, 
                       'user_id': data.user_id,
                       'message' : data.message,
                       'generation_time' : data.generation_time,
                       'from_type' : data.from_type,
                       'chat_id': 'TODO'
                       }
                        
            try:
                query_builder = client.table('chat_history').insert(payload)
                response = query_builder.execute()
                
            except Exception as e:
                print(e)
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save chat")
                
            return {"status": "success", "message": "Saved the chat successfully"}

        except Exception as e:
            print("Chat history service", e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def get_chats_by_user(self, user_id: str, page: int = 1, page_size: int = 6):
        client = self.db.get_client()
        res = None
        
        start = (page - 1) * page_size
        end   = start + page_size - 1
        
        try:
            res = client.table('chat_history').select('*').eq('user_id', user_id).order('timestamp', desc=True).range(start, end).execute()  
                    
        except Exception as e:
            print("Supabase query error:", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch chat history"
            )

        chats = list(reversed(res.data or []))        
        return chats
    
    
    # async def get_files_by_org_id(self, org_id: str):
    #     try:
    #         client = self.get_client()
    #         response = client.table("files_data").select("*").eq("org_id", org_id).execute()
    #         files = response.data or []
    #         print(files)
    #         print(org_id)

    #         # Generate signed URLs for each file
    #         for file in files:
    #             print(f"Generating signed URL for file path: {file['file_path']}")
    #             # Remove "files/" prefix
    #             file_path = file["file_path"]
    #             if file_path.startswith("files/"):
    #                 file_path = file_path[len("files/"):]

    #             signed_url_response = client.storage.from_('files').create_signed_url(
    #                 file_path, 
    #                 expires_in=3600
    #             )
    #             print(f"Signed URL: {signed_url_response['signedURL']}")
    #             file["signed_url"] = signed_url_response['signedURL']

    #         return files
    #     except Exception as e:
    #         print(e)
    #         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        
    # async def get_files_by_filename(self, filename: str):
    #     try:
    #         client = self.get_client()

    #         signed_url_response = client.storage.from_('files').create_signed_url(
    #             filename, 
    #             expires_in=31536000 # 1 year
    #         )
    #         print(f"Signed URL: {signed_url_response['signedURL']}")
    #         return signed_url_response['signedURL']

    #     except Exception as e:
    #         print(e)
    #         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
            
            
            