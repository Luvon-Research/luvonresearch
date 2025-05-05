from models.user import UserBase, UserCreated
from fastapi import UploadFile, HTTPException, status
from services.supabase_service import SupabaseService
from clerk_backend_api import Clerk
from models.sheet import SheetRowUpdatedResponse,SheetRowUpdates
from config import settings
import csv
import io
import numpy as np
from fastapi.responses import StreamingResponse
from uuid import uuid4
import os
from fastapi import UploadFile, HTTPException, status, Request
from uuid import uuid4
import os
from clerk_backend_api import Clerk
from config import settings



class SheetService:
    def __init__(self, db: SupabaseService):
        self.db = db

    async def get_sheet_data_by_id(self, id:str):
        try:
            client = self.db.get_client()
            # chain your filters and then await execute()
            response = client.table("sheet_data").select("*").eq("sheet_id", id).execute()
            # response.data should now actually contain your rows
            return response.data or []
        except Exception as e:
            print(e)
            return e
    
    async def get_sheet_data_csv_by_id(self, id: str):
            try:
                client = self.db.get_client()
                # 1) Get the data from DB
                response = client.table("sheet_data") \
                                    .select("*") \
                                    .eq("sheet_id", id) \
                                    .execute()

                data = response.data or []

                # 2) Compute dimensions from the actual indices
                row_count = max((row["row_id"] for row in data), default=-1) + 1
                col_count = max(
                    (cell["col"] for row in data for cell in row["row_data"]),
                    default=-1,
                ) + 1

                # 3) Initialize a blank matrix of the right size
                matrix = [["" for _ in range(col_count)] for _ in range(row_count)]

                # 4) Populate it
                for row in data:
                    rid = row["row_id"]
                    for cell in row["row_data"]:
                        cell_id = cell["col"]
                        matrix[rid][cell_id] = cell["val"]

                # 5) Write CSV into an in-memory buffer
                buffer = io.StringIO()
                writer = csv.writer(buffer)
                for row in matrix:
                    writer.writerow(row)
                buffer.seek(0)

                # 7) Stream it back with download headers
                headers = {
                    "Content-Disposition": 'attachment; filename="sheet.csv"'
                }
                return StreamingResponse(buffer, media_type="text/csv", headers=headers)

            except Exception as e:
                print(e)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e),
                )
        
        
    async def updateRowsBulk(self, data: SheetRowUpdates):
        try:
            client = self.db.get_client()
            response = None
            modelJSON = data.model_dump()
            
            #print(modelJSON)
            
            rows = modelJSON['row_data']
            
            for row in rows:
                #print(row)
                if all(value == "" for value in row['row_data']): # Deletes the row from the db then
                    response = client.table("sheet_data").delete().eq("row_id", row['row_id']).eq("sheet_id", modelJSON['sheet_id']).execute()
                else:
                    insert_data = row
                    insert_data['sheet_id'] = modelJSON['sheet_id']
                    
                    response = client.table('sheet_data').upsert(insert_data).execute()
                val = response.data
                #print(val)
            
            return SheetRowUpdatedResponse(status="success", message="Updated rows")
            
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )
    
    async def verify_user_token(self, request: Request) -> str:
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")

        token_value = auth_header.split(" ")[1]
        clerk = Clerk(settings.CLERK_API_SECRET_KEY)
        session = clerk.sessions.verify(token_value)

        if not session or "user_id" not in session:
            raise HTTPException(status_code=401, detail="Invalid Clerk session")

        return session["user_id"]
    
    async def upload_file(
        self,
        file: UploadFile,
        project_id: str,
        uploader_id: str,
        request: Request
    ):
        try:
            contents = await file.read()
            extension = os.path.splitext(file.filename)[1]
            unique_name = f"{uuid4()}{extension}"
            file_path = f"{project_id}/{unique_name}"

            client = self.db.get_client()

            # Upload to Supabase Storage
            client.storage.from_("project-files").upload(
                file_path,
                contents,
                {"content-type": file.content_type}
            )

            # Log metadata
            file_record = {
                "file_name": file.filename,
                "file_path": file_path,
                "project_id": project_id,
                "uploader_id": uploader_id
            }

            insert_response = client.table("files").insert(file_record).execute()
            return {
                "status": "success",
                "file_name": file.filename,
                "project_id": project_id,
                "file_path": file_path
            }

        except Exception as e:
            print(f"[upload_file ERROR]: {e}")
            raise HTTPException(status_code=500, detail=str(e))



        
        
    
    



   








