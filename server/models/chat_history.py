from pydantic import BaseModel
from typing import Optional

class ChatHistoryUpload(BaseModel):
    org_id: str  
    user_id: str
    message: list
    generation_time: float
    from_type: str
    chat_id: str

class ChatHistory(BaseModel):
    org_id: str  
    user_id: str
    message: list
    generation_time: float
    from_type: str
    chat_id: str

