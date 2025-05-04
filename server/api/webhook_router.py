from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from services.project_service import ProjectService
from services.supabase_service import SupabaseService
from models.project import ProjectBase
from config import settings
import hmac
import hashlib

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])

def get_project_service() -> ProjectService:
    return ProjectService(SupabaseService())

def verify_clerk_webhook(
    request: Request,
    svix_id: str = Header(None, alias="svix-id"),
    svix_timestamp: str = Header(None, alias="svix-timestamp"),
    svix_signature: str = Header(None, alias="svix-signature"),
):
    if not svix_id or not svix_timestamp or not svix_signature:
        raise HTTPException(status_code=401, detail="Missing Svix headers")
    
    # Get your webhook secret from environment variables
    webhook_secret = settings.CLERK_WEBHOOK_SECRET
    
    # Get the raw request body
    body = request.scope["body"]
    
    # Create the signature payload
    payload = f"{svix_id}.{svix_timestamp}.{body.decode('utf-8')}"
    
    # Compute the expected signature
    h = hmac.new(
        webhook_secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    )
    computed_signature = h.hexdigest()
    
    # Compare with the provided signature
    if not hmac.compare_digest(computed_signature, svix_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    return True

@router.post("/clerk")
async def clerk_webhook(
    request: Request,
    project_service: ProjectService = Depends(get_project_service)
):
    # Store the raw body for signature verification
    body = await request.body()
    request.scope["body"] = body
    
    # Verify the webhook signature (uncomment when you have the webhook secret)
    # verify_clerk_webhook(request)
    
    # Parse the webhook payload
    payload = await request.json()
    event_type = payload.get("type")
    
    # Handle organization creation/update events
    if event_type == "organization.created" or event_type == "organization.updated":
        data = payload.get("data", {})
        org_id = data.get("id")
        org_name = data.get("name")
        
        # Get the user who created/updated the organization
        # This might need adjustment based on the actual payload structure
        user_id = data.get("created_by") or ""
        
        # Store in your database
        project_data = ProjectBase(
            id=org_id,
            name=org_name,
            user_id=user_id
        )
        
        project_service.create(project_data)
        
    return {"status": "success"} 