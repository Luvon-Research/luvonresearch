from .supabase_service import supabase_service

class ServiceProvider:
    """Provider for accessing all services."""
    
    @property
    def supabase(self):
        """Get the Supabase service.
        
        Returns:
            The Supabase service instance
        """
        return supabase_service

# Create a singleton instance
service_provider = ServiceProvider() 