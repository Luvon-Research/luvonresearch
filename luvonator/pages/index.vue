<template>
  <div>
    <SignedIn>
      <Dashboard />
    </SignedIn>
    <SignedOut>
      <LandingPage />
    </SignedOut>
  </div>
</template>

<script setup>
import LandingPage from '~/pages/landing.vue';
import Dashboard from '~/pages/dashboard.vue';
// Add any necessary script setup logic here
</script>
