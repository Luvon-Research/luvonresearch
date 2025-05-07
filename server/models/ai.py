from pydantic import BaseModel,Field
from typing import Optional

class AIResponse(BaseModel):
    status: str = Field(description="'success' or 'failed'")
    answer: str = Field(description='list of messages')
    #img_path: str = Field(description="Only use this feild for chart responses or else leave blank")
    #extra_metadata: str = Field(description="Leave this blank by default unless specified, or else include code here")
    
class GraphAgentResponse(BaseModel):
    status: str = Field(description="'success' or 'failed'")
    r_code: str = Field(description="Code in R to recreate this graph")
    
class GraphAgentFinalResponse(BaseModel):
    status: str = Field(description="'success' or 'failed'")
    r_code: str = Field(description="Code in R to recreate this graph")
    img_url: str = Field(description="URL of generated chart")

class AIInput(BaseModel):
    prompt: str
    context_source: str

class MainAgentResponse(BaseModel):
    status: str = Field(description="'success' or 'failed'")
    answer_path: str