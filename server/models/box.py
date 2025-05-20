from pydantic import BaseModel
from typing import Optional

class BoxFiles(BaseModel):
    file_ids: list
    user_id: str
    file_names: list
      

