# services/box_service.py

import os
import httpx
from dotenv import load_dotenv
from services.supabase_service import SupabaseService
from services.files_service import FilesService
import requests

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


async def upload_files_to_supabase(file_ids: list, file_names: list, org_id: str, user_id:str, files_service: FilesService, access_token: str):
    headers = {"Authorization": f"Bearer {access_token}"}

    for i, file_id in enumerate(file_ids):
        url = f"https://api.box.com/2.0/files/{file_id}/content"
        response = requests.get(url, headers=headers, allow_redirects=False)  # Don't follow redirect automatically

        print(response.status_code)
        print(response)
        print(response.headers)

        if response.status_code == 302:
            # Box responds with a redirect; file location is in 'Location' header
            redirect_url = response.headers.get("Location")
            if redirect_url:
                file_response = requests.get(redirect_url)
                print(file_response.status_code)
                # file_response.content contains the binary file data
                
                file_data = file_response.content
                
                print(file_names[i])
                
                res = await files_service.upload_file(org_id=org_id, 
                                          uploader_id=user_id, 
                                          file=file_data,
                                          file_name=file_names[i],
                                          is_chart=False)

                # #print(file_response.content)  # Print first 100 bytes as sample
            else:
                print("No redirect URL found in response.")