from pydantic import BaseModel,Field
from typing import Optional

class AIResponse(BaseModel):
    status: str = Field(description="'success' or 'failed'")
    answer: str 
    
class GraphAgentResponse(BaseModel):
    status: str = Field(description="'success' or 'failed'")
    data: str = Field(description="graph data in JSON")
    r_code: str = Field(description="Code in R to recreate this graph")

class AIInput(BaseModel):
    prompt: str

class MainAgentResponse(BaseModel):
    status: str = Field(description="'success' or 'failed'")
    answer_path: str