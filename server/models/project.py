from pydantic import BaseModel
from typing import Optional

class ProjectBase(BaseModel):
    id: str  # The Clerk organization ID
    name: str
    user_id: str  # The user creating/updating the project metadata

class ProjectCreated(BaseModel):
    id: str
    status: str
    message: str 