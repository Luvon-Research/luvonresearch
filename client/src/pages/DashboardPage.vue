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
      <div class="button-row">
        <button class="ai-assistant-btn">
          <i class="pi pi-sparkles"></i>
          AI assistant
        </button>

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

.button-row {
  position: absolute;
  left: 1rem;
  right: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 1;
}

.ai-assistant-btn {
  background-color: #f0f0f0;
  border: none;
  padding: 0.4rem 0.8rem;
  font-size: 0.875rem;
  color: #333;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
}

.ai-assistant-btn .pi {
  margin-right: 0.4rem;
  font-size: 1rem;
}

.sheet-container {
  position: absolute;
  top: calc(var(--navbar-height, 64px) + 1rem);
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