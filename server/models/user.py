# app/models/user.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    id: str
    firstName: str
    lastName: str
    fullName: str = Field(None, max_length=100)
    pfp: str

class UserSearchByID(BaseModel):
    id: str

class UserCreated(BaseModel):
    status: str
    message: str
