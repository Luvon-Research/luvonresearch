# services/box_service.py

import os
import httpx
from dotenv import load_dotenv
from services.supabase_service import SupabaseService

load_dotenv()
supabase = SupabaseService()


async def exchange_code_for_token(code: str, user_id: str):
    url = "https://api.box.com/oauth2/token"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": os.getenv("BOX_CLIENT_ID"),
        "client_secret": os.getenv("BOX_CLIENT_SECRET"),
        "redirect_uri": 'http://localhost:8000/callback',
    }

    async with httpx.AsyncClient() as client:
        res = await client.post(url, data=payload)
        if res.status_code != 200:
            raise Exception(f"Box token exchange failed: {res.text}")
        token_data = res.json()

    return {
        "access_token": token_data["access_token"],
        "refresh_token": token_data["refresh_token"],
        "expires_in": token_data["expires_in"]
    }


async def list_user_files(user_id: str):
    result = supabase.get_client().table("integrations").select(
        "*").eq("user_id", user_id).execute()
    if not result.data or len(result.data) == 0:
        raise Exception("No Box integration found")

    token_data = result.data[0]
    access_token = token_data["token"]

    headers = {"Authorization": f"Bearer {access_token}"}
    url = "https://api.box.com/2.0/folders/0/items"  # root folder

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Box API error: {response.text}")

    return response.json()
