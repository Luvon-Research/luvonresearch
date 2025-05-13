from pydantic import BaseModel
from typing import Optional, Any, Dict, List


class QueryRequest(BaseModel):
    prompt: str
    namespace: str
    top_k: Optional[int] = 5
    filter: Optional[Dict[str, Any]] = None

class QueryResult(BaseModel):
    id: str
    score: float
    metadata: Dict[str, Any]

class QueryResponse(BaseModel):
    results: List[QueryResult]