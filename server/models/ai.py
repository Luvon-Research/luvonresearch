from pydantic import BaseModel,Field
from typing import Optional

class AIResponse(BaseModel):
    status: str = Field(description="'success' or 'failed'")
    answer: str 
    chart_path: str
    
class GraphAgentResponse(BaseModel):
    status: str = Field(description="'success' or 'failed'")
    r_code: str = Field(description="Code in R to recreate this graph")
    chart_path: str = Field(description="The absolute path to the chart image")

class AIInput(BaseModel):
    prompt: str

class MainAgentResponse(BaseModel):
    status: str = Field(description="'success' or 'failed'")
    answer_path: str