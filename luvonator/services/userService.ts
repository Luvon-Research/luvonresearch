import { useSupabaseClient } from '#imports'; // Auto-imported by Nuxt

// Define your database schema
interface Database {
  public: {
    Tables: {
      users: {
        Row: UserProfile;
        Insert: UserCreateData;
        Update: UserUpdateData;
      };
    };
  };
}

// Define a type for your user data (adjust properties based on your 'users' table columns)
interface UserProfile {
  id: string; // Assuming this is your primary key (e.g., UUID from Supabase Auth)
  clerk_id?: string; // If you link Clerk users
  full_name?: string;
  email?: string;
  created_at?: string;
  // Add other relevant user profile fields here
  [key: string]: any; // Allow for additional properties
}

// Define the type for user data used in creation (excluding auto-generated fields like id, created_at)
type UserCreateData = Omit<UserProfile, 'id' | 'created_at'>;

// Define the type for user data used in updates (all fields optional)
type UserUpdateData = Partial<UserCreateData>;

export const useUserService = () => {
  // Specify the database type
  const client = useSupabaseClient<Database>();
  const tableName = 'users'; // The name of your table in Supabase

  /**
   * Fetches a user profile by their primary ID.
   * @param userId - The primary key ID of the user.
   * @returns The user profile data or null if not found.
   */
  const getUserById = async (userId: string): Promise<UserProfile | null> => {
    if (!userId) {
      console.error('UserService: getUserById requires a userId.');
      return null;
    }
    try {
      const { data, error } = await client
        .from(tableName)
        .select('*')
        .eq('id', userId)
        .single(); // Use .single() if ID is unique and you expect only one result

      if (error) {
        console.error(`UserService: Error fetching user by ID ${userId}:`, error.message);
        // Optionally throw the error or handle it differently
        // throw error;
        return null;
      }
      return data as UserProfile | null;
    } catch (err) {
      console.error(`UserService: Unexpected error in getUserById for ID ${userId}:`, err);
      return null;
    }
  };

  /**
   * Fetches a user profile by their Clerk ID.
   * @param clerkId - The Clerk ID of the user.
   * @returns The user profile data or null if not found.
   */
  const getUserByClerkId = async (clerkId: string): Promise<UserProfile | null> => {
    if (!clerkId) {
      console.error('UserService: getUserByClerkId requires a clerkId.');
      return null;
    }
     try {
      const { data, error } = await client
        .from(tableName)
        .select('*')
        .eq('clerk_id', clerkId) // Make sure you have a 'clerk_id' column
        .maybeSingle(); // Use maybeSingle if it's possible the user doesn't exist yet

      if (error) {
        console.error(`UserService: Error fetching user by Clerk ID ${clerkId}:`, error.message);
        return null;
      }
      return data as UserProfile | null;
    } catch (err) {
      console.error(`UserService: Unexpected error in getUserByClerkId for Clerk ID ${clerkId}:`, err);
      return null;
    }
  };


  /**
   * Creates a new user profile.
   * NOTE: Often user creation is handled by Supabase Auth triggers.
   * Use this if you need manual user creation separate from auth.
   * @param userData - The data for the new user.
   * @returns The newly created user profile data or null on failure.
   */
  const createUser = async (userData: UserCreateData): Promise<UserProfile | null> => {
     if (!userData) {
      console.error('UserService: createUser requires userData.');
      return null;
    }
    try {
      // You might want validation here before inserting
      const { data, error } = await client
        .from(tableName)
        .insert([userData])
        .select()
        .single();

      if (error) {
        console.error('UserService: Error creating user:', error.message);
        return null;
      }
      console.log('UserService: User created successfully:', data);
      return data as UserProfile | null;
    } catch (err) {
      console.error('UserService: Unexpected error in createUser:', err);
      return null;
    }
  };

  /**
   * Updates an existing user profile.
   * @param userId - The primary key ID of the user to update.
   * @param updates - An object containing the fields to update.
   * @returns The updated user profile data or null on failure.
   */
  const updateUser = async (userId: string, updates: UserUpdateData): Promise<UserProfile | null> => {
    if (!userId || !updates || Object.keys(updates).length === 0) {
      console.error('UserService: updateUser requires a userId and updates object.');
      return null;
    }
    try {
      // Prevent updating the primary key or clerk_id if necessary
      // delete updates.id;
      // delete updates.clerk_id;

      const { data, error } = await client
        .from(tableName)
        .update(updates)
        .eq('id', userId)
        .select()
        .single();

      if (error) {
        console.error(`UserService: Error updating user ${userId}:`, error.message);
        return null;
      }
      console.log(`UserService: User ${userId} updated successfully:`, data);
      return data as UserProfile | null;
    } catch (err) {
      console.error(`UserService: Unexpected error in updateUser for ID ${userId}:`, err);
      return null;
    }
  };

   /**
   * Deletes a user profile. Use with caution! Consider soft deletes instead.
   * @param userId - The primary key ID of the user to delete.
   * @returns True if deletion was successful (or didn't error), false otherwise.
   */
  const deleteUser = async (userId: string): Promise<boolean> => {
     if (!userId) {
      console.error('UserService: deleteUser requires a userId.');
      return false;
    }
    try {
      const { error } = await client
        .from(tableName)
        .delete()
        .eq('id', userId);

      if (error) {
        console.error(`UserService: Error deleting user ${userId}:`, error.message);
        return false;
      }
      console.log(`UserService: User ${userId} deleted successfully.`);
      return true;
    } catch (err) {
      console.error(`UserService: Unexpected error in deleteUser for ID ${userId}:`, err);
      return false;
    }
  };


  // Return the service functions
  return {
    getUserById,
    getUserByClerkId,
    createUser,
    updateUser,
    deleteUser,
  };
};