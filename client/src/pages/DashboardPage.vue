<script setup>
import { useRouter } from 'vue-router';
import NavBar from '@/components/NavBar.vue';
import { useUser, SignedIn, SignOutButton } from '@clerk/vue';

const router = useRouter();
const { user } = useUser();

</script>

<template>
  <div class="dashboard-layout">
    <NavBar />

    <main class="dashboard-content">
      <h1>Dashboard</h1>
      <p v-if="user">
        Welcome back, {{ user.firstName || user.primaryEmailAddress.emailAddress }}!
      </p>
      <p>This is your protected dashboard area.</p>
      <SignedIn>
        <SignOutButton asChild>
          <button class="p-button p-button-secondary">Sign Out</button>
        </SignOutButton>
      </SignedIn>
    </main>
  </div>
</template>

<style scoped>
.dashboard-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.dashboard-content {
  flex: 1;
  padding: 2rem;
  background: var(--color-background);
  margin-top: var(--navbar-height, 64px);
}
</style>