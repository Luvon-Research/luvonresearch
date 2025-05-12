# services/box_service.py
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

# In-memory token store (replace with actual database logic)
user_token_store = {}

async def exchange_code_for_token(code: str, user_id: str):
    url = "https://api.box.com/oauth2/token"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": os.getenv("BOX_CLIENT_ID"),
        "client_secret": os.getenv("BOX_CLIENT_SECRET"),
        "redirect_uri": os.getenv("BOX_REDIRECT_URI"),
    }

    async with httpx.AsyncClient() as client:
        res = await client.post(url, data=payload)
        if res.status_code != 200:
            raise Exception(f"Box token exchange failed: {res.text}")
        token_data = res.json()

    # Store the token per user (temporary, replace with DB logic)
    user_token_store[user_id] = token_data
    return token_data

async def list_user_files(user_id: str):
    token_data = user_token_store.get(user_id)
    if not token_data:
        raise Exception("Box token not found for user")

    access_token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    url = "https://api.box.com/2.0/folders/0/items"  # root folder

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Box API error: {response.text}")

    return response.json()
