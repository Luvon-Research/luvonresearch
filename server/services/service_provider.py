from .supabase_service import supabase_service
from .files_service import FilesService

class ServiceProvider:
    """Provider for accessing all services."""
    
    @property
    def supabase(self):
        """Get the Supabase service.
        
        Returns:
            The Supabase service instance
        """
        return supabase_service

    @property
    def files(self):
        """Get the Files service.
        
        Returns:
            The Files service instance
        """
        return FilesService(supabase_service)

# Create a singleton instance
service_provider = ServiceProvider() 