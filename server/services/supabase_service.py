from supabase import create_client, Client
from ..config import settings

class SupabaseService:
    """Service for interacting with Supabase."""
    
    def __init__(self):
        """Initialize the Supabase client."""
        self.supabase: Client = create_client(
            settings.SUPABASE_URL, 
            settings.SUPABASE_KEY
        )
    
    def get_client(self) -> Client:
        """Get the Supabase client instance.
        
        Returns:
            Client: The Supabase client
        """
        return self.supabase
    
    # Example methods for common operations
    
    async def fetch_data(self, table_name: str, query=None):
        """Fetch data from a table with optional query parameters.
        
        Args:
            table_name: The name of the table to query
            query: Optional query builder functions to apply
            
        Returns:
            The query results
        """
        query_builder = self.supabase.table(table_name).select("*")
        
        if query:
            # Apply any additional query parameters
            query_builder = query(query_builder)
            
        response = query_builder.execute()
        return response.data
    
    async def insert_data(self, table_name: str, data: dict):
        """Insert data into a table.
        
        Args:
            table_name: The name of the table
            data: The data to insert
            
        Returns:
            The inserted data
        """
        response = self.supabase.table(table_name).insert(data).execute()
        return response.data
    
    async def update_data(self, table_name: str, data: dict, match_criteria: dict):
        """Update data in a table.
        
        Args:
            table_name: The name of the table
            data: The data to update
            match_criteria: The criteria to match records for updating
            
        Returns:
            The updated data
        """
        response = self.supabase.table(table_name).update(data).match(match_criteria).execute()
        return response.data
    
    async def delete_data(self, table_name: str, match_criteria: dict):
        """Delete data from a table.
        
        Args:
            table_name: The name of the table
            match_criteria: The criteria to match records for deletion
            
        Returns:
            The deleted data
        """
        response = self.supabase.table(table_name).delete().match(match_criteria).execute()
        return response.data

# Create a singleton instance
supabase_service = SupabaseService()