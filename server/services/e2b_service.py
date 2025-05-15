from supabase import create_client, Client
from fastapi import HTTPException, status
from config import settings
import os
from util.utils import generate_uuid
from dotenv import load_dotenv
from e2b_code_interpreter import Sandbox

class E2BService:
    def __init__(self):
        load_dotenv()
        self._sandboxes_file = "sandboxes.txt"
        self.sbx_template_id = "potaq3k9ta9l28671h7j"

        # 1) Load any previously‐used sandbox IDs
        if os.path.exists(self._sandboxes_file):
            with open(self._sandboxes_file, "r") as f:
                sandbox_ids = [line.strip() for line in f if line.strip()]
        else:
            sandbox_ids = []

        active_sbx = None
        updated_ids = []

        # 2) Try each ID in turn
        for sbx_id in sandbox_ids:
            try:
                sbx = Sandbox(sandbox_id=sbx_id)      # attach to existing
                if sbx.is_running():       # check health
                    active_sbx = sbx
                    updated_ids.append(sbx_id)
                    break
            except Exception:
                # Either invalid ID or not accessible → skip
                pass

        # 3) If none was active, spin up a new one
        if active_sbx is None:
            # create from template
            active_sbx = Sandbox(template=self.sbx_template_id)
            # It will have a new .id property
            updated_ids = sandbox_ids + [active_sbx.sandbox_id]

        # 4) Persist the cleaned+updated list
        with open(self._sandboxes_file, "w") as f:
            f.write("\n".join(updated_ids))
        
        self.sbx = active_sbx
    
    async def add_file(self, filename, data):
        if(not self.sbx.is_running()):
            self.sbx = Sandbox(self.sbx_template_id)
        
        self.sbx.files.write(filename, data)
    
    async def run_command(self, command):
        return self.sbx.commands.run(command)

    async def get_file(self, filename, format="bytes"):
        if(format == 'bytes'):
            return bytes(self.sbx.files.read(filename, format="bytes"))
        else:
            return self.sbx.files.read(filename)
    
    async def remove_file(self, filename):
        self.sbx.files.remove(filename)
    
    async def remove_files(self, files):
        for file in files:
            self.sbx.files.remove(file)


    async def upload_file(self, org_id: str, uploader_id: str, file: bytes, file_name: str, is_chart: bool = False, r_code: str = ''):
        try:
            client = self.get_client()
            
            file_option = "application/pdf"
            
            if(is_chart): file_option = "image/png"
            
            #### Uploads and chunks file to pinecone
            if(not is_chart):
                pinecone = await self.pinecone.ingest_pdf_bytes(file, file_name, org_id)
            
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
                "file_url": file_url,
                "r_code": r_code
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
