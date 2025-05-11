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

    async def upload_file(self, org_id: str, uploader_id: str, file: bytes, file_name: str, is_chart: bool = False):
        try:
            client = self.get_client()
            
            file_option = "application/pdf"
            
            if(is_chart): file_option = "image/png"
            
            # Upload file to Supabase storage
            storage_response = client.storage.from_('files').upload(file_name, file, file_options={"content-type": file_option})
            
            if not storage_response:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to upload file to storage")

            # Construct file path based on is_chart parameter
            #file_path = f"charts/{file_name}" if is_chart else f"files/{file_name}"
            
            file_url = await self.get_signed_url(file_name)
            file_url = file_url['signed_url']

            # Store file metadata in the files_data table
            file_data = {
                "id": generate_uuid(),
                "org_id": org_id,
                "uploader_id": uploader_id,
                "file_path": file_name,
                "file_url": file_url
            }
            
            # ONLY USED FOR CHARTS
            chart_data = {
                "org_id": org_id,
                "project_id": org_id, 
                "uploader_id": uploader_id,
                "file_path": file_name,
                "chart_name": "Test name",
                "file_url": file_url
            }
            
            table_name = "files_data"
            
            if is_chart:
                table_name = "charts"
                file_data = chart_data
            
            response = client.table(table_name).insert(file_data).execute()
            
            print(response)

            if not response.data:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to store file metadata")

            return {"status": "success", "message": "File uploaded successfully", "file_path": file_name, "file_url": file_url}

        except Exception as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def get_files_by_org_id(self, org_id: str, is_chart=False):
        try:
            client = self.get_client()
            table_name = "charts" if is_chart else "files_data"
            print("Charts....", org_id)
            response = client.table(table_name).select("*").eq("org_id", org_id).execute()
            files = response.data or []
            return files
        except Exception as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def get_signed_url(self, file_path: str):
        try:
            client = self.get_client()
            # Remove "files/" prefix if present
            if file_path.startswith("files/"):
                file_path = file_path[len("files/"):]
                
            signed_url_response = client.storage.from_('files').create_signed_url(
                file_path,
                expires_in=315576000 # 10 Years
            )
            return {"signed_url": signed_url_response['signedURL']}
        except Exception as e:
            print(e) 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        
    async def get_files_by_filename(self, filename: str):
        try:
            client = self.get_client()

            signed_url_response = client.storage.from_('files').create_signed_url(
                filename, 
                expires_in=315576000 # 10 years
            )
            print(f"Signed URL: {signed_url_response['signedURL']}")
            return signed_url_response['signedURL']

        except Exception as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
            
            
            