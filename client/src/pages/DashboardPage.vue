<script setup>
// You can add logic here later, e.g., fetching user-specific data
import { useUser, SignedIn, SignOutButton } from '@clerk/vue';

const { user } = useUser();
</script>

<template>
  <div class="dashboard-page">
    <h1>Dashboard</h1>
    <p v-if="user">Welcome back, {{ user.firstName || user.primaryEmailAddress.emailAddress }}!</p>
    <p>This is your protected dashboard area.</p>
    <!-- Add your dashboard content here -->
    <SignedIn>
        <SignOutButton asChild>
        <button>Sign Out</button>
        </SignOutButton>
     </SignedIn>
  </div>
</template>

<style scoped>
.dashboard-page {
  padding: 2rem;
  text-align: center;
}
</style>