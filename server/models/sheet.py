# app/models/user.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class SheetRowCellData(BaseModel):
    col: int
    val: str

class SheetRow(BaseModel):
    row_id: int
    row_data: list
    
class SheetRowUpdatedResponse(BaseModel):
    status: str
    message: str

class SheetRowUpdates(BaseModel):
    sheet_id: str
    row_data: list

class SheetCreate(BaseModel):
    name: str
    owner_id: Optional[str] = None  # User ID of creator
    organization_id: Optional[str] = None  # Organization/project it belongs to
    
class SheetResponse(BaseModel):
    id: str
    name: str
    status: str
    message: str