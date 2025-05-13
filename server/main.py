from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.users_router import router as users_router
from api.sheet_router import router as sheets_router
from api.project_router import router as projects_router
from api.webhook_router import router as webhooks_router
from api.ai_router import router as ai_router
import json
from sse_starlette import EventSourceResponse
import time
from api.files_router import router as files_router
from api.chat_history_router import router as chat_history_router
from api.box_router_auth import router as box_router
from services.pinecone_service import PineconeService
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from models.pinecone import QueryRequest, QueryResponse, QueryResult
from api.pinecone_router import router as pinecone_router

app = FastAPI()

# Configure CORS
origins = ["*"]  # Allow all origins

app.include_router(box_router, prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users_router)
app.include_router(sheets_router)
app.include_router(projects_router)
app.include_router(webhooks_router)
app.include_router(ai_router)
app.include_router(files_router)
app.include_router(chat_history_router)
app.include_router(pinecone_router)

@app.get("/")
async def read_root():
    return {"message": "Hello from FastAPI!"}

@app.get("/api/data")
async def get_data():
    # Example API endpoint
    return {"data": "Some data fetched from the server"}


@app.post("/api/user")
async def create_user():
    # Example API endpoint
    return {"data": "Some data fetched from the server"}

# To run the server (from the 'server' directory):
# 1. Install dependencies: pip install "fastapi[all]" uvicorn
# 2. Run: uvicorn main:app --reload

def fake_video_streamer():
    try:
        for i in range(10):
            time.sleep(0.5)
            yield {
                    "data": json.dumps(f"data point: {i}"),
                    "event": "data",
                }
        yield {"event": "end"}
    except:
        yield {
            "event": "error",
            "data": json.dumps(
                {"status_code": 500, "message": "Internal Server Error"}
            ),
        }
        raise

@app.get("/test")
async def main():
    return EventSourceResponse(fake_video_streamer())


@app.get("/create-index")
async def create_index():
    service = PineconeService()
    res = service.create_index('test')
    print(res)
    return {"status": "success"}


@app.post("/upload-pinecone-file")
async def upload_file(file: UploadFile = File(...)):
    """
    Accepts a single PDF (or any file) upload and sends it
    to PineconeService.process_and_upload_file.
    """
    # 1) Basic content‐type check (optional)
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported."
        )

    # 2) Read file bytes
    print("1")
    data = await file.read()

    # 3) Call your service
    service = PineconeService()
    print("2")
    try:
        # Change your service signature to accept (bytes, filename)
        res = await service.process_and_upload_file(data, file.filename, 'test')
        print("3")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {e}"
        )

    return {
        "status":  "success",
        "detail":  res
    }
    
pinecone_svc = PineconeService()
DEFAULT_INDEX = "test"

@app.post("/query-pinecone", response_model=QueryResponse)
async def query_pinecone(q: QueryRequest):
    return await PineconeService().query_vectors(q.prompt, namespace=q.namespace)
    