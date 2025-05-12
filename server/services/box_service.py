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
