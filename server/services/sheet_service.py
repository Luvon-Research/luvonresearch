from models.user import UserBase, UserCreated
from fastapi import HTTPException, status
from services.supabase_service import SupabaseService
from clerk_backend_api import Clerk
from models.sheet import SheetRowUpdatedResponse,SheetRowUpdates, SheetCreate, SheetResponse
from config import settings
from util.utils import generate_uuid, current_time
import csv
import io
import numpy as np
from fastapi.responses import StreamingResponse

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
    
    async def get_sheet_data_csv_by_id(self, id: str, res=True):
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
                
                if(res):
                    return StreamingResponse(buffer, media_type="text/csv", headers=headers)
                else:
                    return buffer
                    

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
                print(row)
                if all(value == "" for value in row['row_data']) or all(value['val'] == None for value in row['row_data']): # Deletes the row from the db then
                    response = client.table("sheet_data").delete().eq("row_id", row['row_id']).eq("sheet_id", modelJSON['sheet_id']).execute()
                else:
                    insert_data = row
                    insert_data['sheet_id'] = modelJSON['sheet_id']
                    insert_data['row_data'] = [cell for cell in row['row_data']
                                               if cell.get('val') is not None]
                    print(insert_data)
                    
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
        Create a new sheet with the given name and add an initial empty row.
        """
        try:
            client = self.db.get_client()

            # Generate a unique ID for the sheet
            sheet_id = generate_uuid()
            now = current_time()

            # Create the sheet record
            sheet_data = {
                "id": sheet_id,
                "name": data.name,
                "owner_id": data.owner_id,
                "organization_id": data.organization_id,
                "created_at": now
            }

            response = client.table("sheets").insert(sheet_data).execute()

            if response.data:
                # --- Add an initial empty row to sheet_data ---
                try:
                    empty_row_id = 0
                    empty_row_data = {
                        "sheet_id": sheet_id,
                        "row_id": empty_row_id,
                        "row_data": [],
                        "created_at": now,
                    }
                    # Insert the empty row
                    row_response = client.table("sheet_data").insert(empty_row_data).execute()

                    # Optional: Check if row insertion failed, though we still return success for the sheet
                    if not row_response.data:
                         print(f"Warning: Failed to create initial empty row for sheet {sheet_id}")

                except Exception as row_e:
                    # Log the error but don't fail the whole sheet creation
                    print(f"Error creating initial empty row for sheet {sheet_id}: {row_e}")
                # --- End of adding empty row ---

                # Return success for the sheet creation
                return SheetResponse(
                    id=sheet_id,
                    name=data.name,
                    status="success",
                    message="Sheet created successfully"
                )
            else:
                # This part handles failure in creating the main sheet record
                error_detail = "Failed to create sheet"
                if hasattr(response, 'error') and response.error:
                    error_detail += f": {response.error.message}"
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=error_detail
                )

        except Exception as e:
            print(f"Error in create_sheet: {e}") # Added more specific logging
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred: {str(e)}", # More generic message
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
        
    async def delete_sheet(self, sheet_id: str):
        """
        Delete a sheet and all its associated data
        """
        try:
            client = self.db.get_client()
            
            # First delete all sheet data
            data_response = client.table("sheet_data").delete().eq("sheet_id", sheet_id).execute()
            
            # Then delete the sheet itself
            sheet_response = client.table("sheets").delete().eq("id", sheet_id).execute()
            
            # Check if sheet was found and deleted
            if not sheet_response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Sheet not found"
                )
                
            return True
            
        except Exception as e:
            print(f"Error in delete_sheet: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        
        