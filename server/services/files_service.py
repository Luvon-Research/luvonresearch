from supabase import create_client, Client
from fastapi import HTTPException, status
from config import settings
from services.supabase_service import SupabaseService
from util.utils import generate_uuid

class FilesService:
    def __init__(self, db: SupabaseService):
        self.db = db

    def get_client(self) -> Client:
        return self.db.get_client()

    async def upload_file(self, org_id: str, uploader_id: str, file: bytes, file_name: str):
        try:
            client = self.get_client()
            
            # Upload file to Supabase storage
            storage_response = client.storage.from_('files').upload(file_name, file, file_options={"content-type": "application/pdf"})
            
            if not storage_response:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to upload file to storage")

            # Construct file path
            file_path = f"files/{file_name}"

            # Store file metadata in the files_data table
            file_data = {
                "id": generate_uuid(),
                "org_id": org_id,
                "uploader_id": uploader_id,
                "file_path": file_path
            }
            response = client.table("files_data").insert(file_data).execute()

            if not response.data:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to store file metadata")

            return {"status": "success", "message": "File uploaded successfully", "file_path": file_path}

        except Exception as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def get_files_by_org_id(self, org_id: str):
        try:
            client = self.get_client()
            response = client.table("files_data").select("*").eq("org_id", org_id).execute()
            files = response.data or []
            print(files)
            print(org_id)

            # Generate signed URLs for each file
            for file in files:
                print(f"Generating signed URL for file path: {file['file_path']}")
                # Remove "files/" prefix
                file_path = file["file_path"]
                if file_path.startswith("files/"):
                    file_path = file_path[len("files/"):]

                signed_url_response = client.storage.from_('files').create_signed_url(
                    file_path, 
                    expires_in=3600
                )
                print(f"Signed URL: {signed_url_response['signedURL']}")
                file["signed_url"] = signed_url_response['signedURL']

            return files
        except Exception as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        
        