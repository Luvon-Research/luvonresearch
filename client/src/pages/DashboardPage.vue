<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import NavBar from '@/components/NavBar.vue'
import CreateSheetButton from '@/components/CreateSheetButton.vue'
import SheetBlock from '@/components/SheetBlock.vue'
import SheetChat from '@/components/SheetChat.vue'

const router = useRouter()
const showChat = ref(false)

function toggleChat() {
  showChat.value = !showChat.value
}
</script>

<template>
  <div class="dashboard-layout">
    <NavBar />

    <main class="dashboard-content">
      <!-- This wrapper will slide to the right when showChat is true -->
      <div class="dashboard-wrapper" :class="{ shifted: showChat }">
        <div class="button-row">
          <button class="ai-assistant-btn" @click="toggleChat">
            <i class="pi pi-sparkles"></i>
            AI assistant
          </button>
          <CreateSheetButton />
        </div>

        <div class="sheet-container">
          <SheetBlock />
        </div>
      </div>

      <!-- Slide in the chat panel from the left -->
      <transition name="slide">
        <SheetChat
          v-if="showChat"
          class="sheet-chat"
          @close="showChat = false"
        />
      </transition>
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
  --chat-width: 400px;
  position: relative;
  flex: 1;
  overflow: hidden; /* keep container clipped */
  background: var(--color-background);
  margin-top: var(--navbar-height, 64px);
}

/* This inner wrapper contains all your old content */
.dashboard-wrapper {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  right: 0;
  transition: margin-left 0.3s ease;
}

/* When chat is open, push the wrapper to the right */
.dashboard-wrapper.shifted {
  margin-left: var(--chat-width);
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

/* NEW: chat-pane styling */
.sheet-chat {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  width: var(--chat-width);
  background: #fff;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  z-index: 2;
  overflow: hidden;
}

/* Transition for chat sliding in */
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}
.slide-enter-from,
.slide-leave-to {
  transform: translateX(-100%);
}
</style>