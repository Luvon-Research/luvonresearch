from pydantic import BaseModel

class FileUploadRequest(BaseModel):
    org_id: str 