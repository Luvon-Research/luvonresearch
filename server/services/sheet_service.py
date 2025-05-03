from models.user import UserBase, UserCreated
from fastapi import HTTPException, status
from services.supabase_service import SupabaseService
from clerk_backend_api import Clerk
from models.sheet import SheetRowUpdatedResponse,SheetRowUpdates, SheetCreate, SheetResponse
from config import settings
from util.utils import generate_uuid, current_time
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

    async def create_sheet(self, data: SheetCreate):
        """
        Create a new sheet with the given name
        """
        try:
            client = self.db.get_client()
            
            # Generate a unique ID for the sheet
            sheet_id = generate_uuid()
            
            # Create the sheet record
            sheet_data = {
                "id": sheet_id,
                "name": data.name,
                "owner_id": data.owner_id,
                "organization_id": data.organization_id,
                "created_at": current_time()
            }
            
            response = client.table("sheets").insert(sheet_data).execute()
            
            if response.data:
                return SheetResponse(
                    id=sheet_id,
                    name=data.name,
                    status="success",
                    message="Sheet created successfully"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create sheet"
                )
            
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )
        
    async def get_sheets_by_organization_id(self, organization_id: str):
        """
        Get all sheets for a specific organization
        """
        try:
            client = self.db.get_client()
            response = client.table("sheets").select("*").eq("organization_id", organization_id).execute()
            return response.data or []
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )
        
        