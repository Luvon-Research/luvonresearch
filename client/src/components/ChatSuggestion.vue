<template>
  <div class="d-inline-flex align-items-center border rounded p-2 command-card" @click="handleClick">
    <!-- Icon wrapper -->
    <div
      class="d-flex align-items-center justify-content-center me-2 command-icon"
      :style="'background-color: ' + color"
    >
      <!-- Replace with whatever icon you’re using -->
      <i :class="'pi ' + icon"></i>
    </div>

    <!-- Text, vertically centered -->
    <span class="command-title">{{ title }}</span>
  </div>
</template>

<script setup lang="ts">

const props = defineProps<{
  title: string;
  icon: string;
  color: string;
  prompt: string;
}>();

// 2) define the click emitter
const emit = defineEmits<{
  (e: "select", payload: string): void;
}>();

// 3) on div click -> emit the event
function handleClick() {
    emit("select", props.prompt);
}
</script>

<style scoped>
.command-card {
  height: 3.5rem;
  width: 16rem;
  border: 1px solid gray;
  border-radius: 8px;
  transition: background-color 0.2s ease-in;
  margin-top: 0.7rem;
  margin-right: 0.7rem;
}

.command-card:hover {
  cursor: pointer;
  background-color: #f1f1f1;
}

.command-title {
  color: black;
  font-weight: bold;
  font-size: 14px;
  margin-left: 0.5rem;
}

.command-icon {
  height: 2.5rem;
  width: 2.5rem;
  border-radius: 8px;
}
</style>
