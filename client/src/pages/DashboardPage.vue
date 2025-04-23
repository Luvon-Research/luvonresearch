<script setup>
import { useRouter } from 'vue-router';
import NavBar from '@/components/NavBar.vue';
import CreateSheetButton from '@/components/CreateSheetButton.vue';
import SheetBlock from '@/components/SheetBlock.vue';

const router = useRouter();

</script>

<template>
  <div class="dashboard-layout">
    <NavBar />

    <main class="dashboard-content">
      <div class="create-button-container">
        <CreateSheetButton />
      </div>
      <div class="sheet-container">
        <SheetBlock />
      </div>
    </main>
  </div>
</template>

<style scoped>
.dashboard-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.dashboard-content {
  flex: 1;
  /* padding: 1rem; */
  background: var(--color-background);
  margin-top: var(--navbar-height, 64px);
  position: relative;
}

.create-button-container {
  position: absolute;
  right: 1rem;
  z-index: 1;
}

.sheet-container {
  position: absolute;
  top: calc(var(--navbar-height, 64px));
  left: 1rem;
  right: 1rem;
  bottom: 1rem;
  background: white;
  border-radius: 8px;

  box-sizing: border-box;
  max-width: calc(100% - 2rem);
  overflow-x: auto;
  overflow-y: auto;
}
</style>