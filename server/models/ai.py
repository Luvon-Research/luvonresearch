from pydantic import BaseModel,Field
from typing import Optional

class AIResponse(BaseModel):
    status: str = Field(description="'success' or 'failed'")
    answer: str
    img_path: str = Field(description="Only use this feild for chart responses or else leave blank")
    extra_metadata: str = Field(description="Leave this blank by default unless specified")
    
class GraphAgentResponse(BaseModel):
    status: str = Field(description="'success' or 'failed'")
    r_code: str = Field(description="Code in R to recreate this graph")
    filename: str = Field(description="The filename of the chart image")

class AIInput(BaseModel):
    prompt: str

class MainAgentResponse(BaseModel):
    status: str = Field(description="'success' or 'failed'")
    answer_path: str