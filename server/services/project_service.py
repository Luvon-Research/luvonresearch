from fastapi import HTTPException, status
from services.supabase_service import SupabaseService
from clerk_backend_api import Clerk
from config import settings
from models.project import ProjectBase, ProjectCreated

class ProjectService:
    def __init__(self, db: SupabaseService):
        self.db = db
        self.clerk = Clerk(settings.CLERK_API_SECRET_KEY)
    
    def create(self, data: ProjectBase) -> ProjectCreated:
        """
        Store project metadata in Supabase for an existing Clerk organization
        """
        try:
            # Verify the organization exists in Clerk
            try:
                org = self.clerk.organizations.get(organization_id=data.id)
            except Exception as clerk_error:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Organization not found in Clerk: {str(clerk_error)}"
                )
            
            # Store project metadata in Supabase
            project_data = {
                "id": data.id,  # This is the Clerk organization ID
                "name": data.name,
                "created_by": data.user_id,
            }
            
            client = self.db.get_client()
            response = client.table('projects').insert(project_data).execute()
            
            return ProjectCreated(
                id=data.id,
                status="success",
                message="Project metadata stored successfully"
            )
            
        except HTTPException as he:
            raise he
        except Exception as e:
            print(e)
            if hasattr(e, 'code') and e.code == '23505':  # Key already exists
                return ProjectCreated(
                    id=data.id,
                    status="success",
                    message="Project already exists in database"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to store project metadata: {str(e)}"
                )
    
    def get_by_id(self, project_id: str):
        """
        Get project details by ID
        """
        try:
            client = self.db.get_client()
            query_builder = client.table('projects').select("*").eq("id", project_id)
            response = query_builder.execute()
            
            if not response.data:
                # If not in our database, try to get basic info from Clerk
                try:
                    org = self.clerk.organizations.get(organization_id=project_id)
                    return {
                        "id": org.id,
                        "name": org.name,
                        "created_by": None
                    }
                except:
                    return None
                    
            return response.data[0]
        except Exception as e:
            print(e)
            return None
    
    def get_user_projects(self, user_id: str):
        """
        Get all projects for a user (via Clerk API)
        """
        try:
            # Get organizations for the user from Clerk
            memberships = self.clerk.users.get_organization_memberships(user_id=user_id)
            org_ids = [m.organization.id for m in memberships]
            
            if not org_ids:
                return []
                
            # Get the details from Supabase
            client = self.db.get_client()
            response = client.table('projects').select("*").in_("id", org_ids).execute()
            
            # Create a map of existing projects
            existing_projects = {p["id"]: p for p in response.data}
            
            # Combine with Clerk data for any missing projects
            result = []
            for membership in memberships:
                org = membership.organization
                if org.id in existing_projects:
                    result.append(existing_projects[org.id])
                else:
                    # Basic info from Clerk if not in our database
                    result.append({
                        "id": org.id,
                        "name": org.name,
                        "created_by": None
                    })
            
            return result
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch user projects: {str(e)}"
            ) 