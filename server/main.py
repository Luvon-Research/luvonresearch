from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.users_router import router as users_router

app = FastAPI()
app.include_router(users_router)

# Configure CORS (Cross-Origin Resource Sharing)
# This allows your Vue app (running on a different port)
# to communicate with the FastAPI server.
origins = [
    "http://localhost:5173",  # Default Vue dev server port
    "http://127.0.0.1:5173",
    # Add the URL of your deployed Vue app if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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