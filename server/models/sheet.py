# app/models/user.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class SheetRow(BaseModel):
    row_id: int
    sheet_id: str
    row_data: list[str]
    
    
class SheetRowUpdated(BaseModel):
    status: str
    message: str

class SheetData(BaseModel):
    sheet_id: int
    row_data: list
