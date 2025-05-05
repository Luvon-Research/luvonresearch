from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.users_router import router as users_router
from api.sheet_router import router as sheets_router
from api.project_router import router as projects_router
from api.webhook_router import router as webhooks_router
from api.ai_router import router as ai_router

app = FastAPI()

# Configure CORS
origins = ["*"]  # Allow all origins

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