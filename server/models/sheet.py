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
    

class FileUploadResponse(BaseModel):
    status: str
    file_name: str
    project_id: str
    file_path: str


