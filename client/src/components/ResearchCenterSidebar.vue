<template>
  <div class="layout">
    <!-- Sidebar -->
    <div :class="['sidebar', { collapsed }]">
      <!-- Toggle Button -->
      <Button @click="collapsed = !collapsed" class="toggle-btn">
        <i class="pi pi-table"></i>
      </Button>

      <!-- Menu -->
      <Panel
        class="menu"
        :style="{ display: collapsed ? 'none' : 'block' }">
        <h1>History</h1>
      </Panel>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import Button from "primevue/button";
import PanelMenu from "primevue/panelmenu";

const collapsed = ref(true);

const items = [
  {
    label: "New Chat",
    icon: "pi pi-plus",
    command: () => console.log("New Chat"),
  },
  {
    label: "History",
    icon: "pi pi-history",
    items: [
      {
        label: "Today",
        icon: "pi pi-calendar",
        command: () => console.log("Today"),
      },
      {
        label: "Yesterday",
        icon: "pi pi-calendar-minus",
        command: () => console.log("Yesterday"),
      },
    ],
  },
  {
    label: "Settings",
    icon: "pi pi-cog",
    command: () => console.log("Settings"),
  },
];
</script>

<style scoped>
.layout {
  display: flex;
  height: 100vh;
  position: fixed;
}

.sidebar {
  background: #fdfdfd;
  border-right: 1px solid #ddd;
  width: 250px;
  transition: width 0.3s;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding-top: 0rem;
}

.sidebar.collapsed {
  width: 0rem;
}

.toggle-btn {
  margin: 0 0rem 1rem;
  background: white;
  border: none;
  font-size: 1.2rem;
  color: black;
}

.menu {
  flex: 1;
  width: 100%;
}

.content {
  flex: 1;
  padding: 1rem;
}
</style>
