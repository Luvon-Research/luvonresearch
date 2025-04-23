<script setup>
import { useRouter } from 'vue-router';
import NavBar from '@/components/NavBar.vue';
import CreateSheetButton from '@/components/CreateSheetButton.vue';

const router = useRouter();

</script>

<template>
  <div class="dashboard-layout">
    <NavBar />

    <main class="dashboard-content">
      <div class="create-button-container">
        <CreateSheetButton />
      </div>
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

.create-button-container {
  position: absolute;
  top: calc(var(--navbar-height, 64px) + 2rem);
  right: 2rem;
}
</style>