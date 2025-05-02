from models.user import UserBase, UserCreated
from fastapi import HTTPException, status
from services.supabase_service import SupabaseService
from clerk_backend_api import Clerk
from models.sheet import SheetRowUpdatedResponse,SheetRowUpdates
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