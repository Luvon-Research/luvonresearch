<script setup>
import { SignedIn, SignedOut, SignInButton, UserButton } from "@clerk/vue";
import Menubar from "primevue/menubar";
import Button from "primevue/button"
import InputText from 'primevue/inputtext';
import Badge from "primevue/badge"
import Avatar from "primevue/avatar"


import { ref } from "vue";
const items = ref([
    {
        label: 'Home',
        icon: 'pi pi-home'
    },
    {
        label: 'Projects',
        icon: 'pi pi-search',
        badge: 3,
        items: [
            {
                label: 'Core',
                icon: 'pi pi-bolt',
                shortcut: '⌘+S'
            },
            {
                label: 'Blocks',
                icon: 'pi pi-server',
                shortcut: '⌘+B'
            },
            {
                separator: true
            },
            {
                label: 'UI Kit',
                icon: 'pi pi-pencil',
                shortcut: '⌘+U'
            }
        ]
    }
]);
</script>

<template>
<Menubar :model="items">
    <template #start>
        <svg width="35" height="40" viewBox="0 0 35 40" fill="none" xmlns="http://www.w3.org/2000/svg" class="h-8">
            <path d="..." fill="var(--p-primary-color)" />
            <path d="..." fill="var(--p-text-color)" />
        </svg>
    </template>
    <template #item="{ item, props, hasSubmenu, root }">
        <a v-ripple class="flex items-center" v-bind="props.action">
            <span>{{ item.label }}</span>
            <Badge v-if="item.badge" :class="{ 'ml-auto': !root, 'ml-2': root }" :value="item.badge" />
            <span v-if="item.shortcut" class="ml-auto border border-surface rounded bg-emphasis text-muted-color text-xs p-1">{{ item.shortcut }}</span>
            <i v-if="hasSubmenu" :class="['pi pi-angle-down ml-auto', { 'pi-angle-down': root, 'pi-angle-right': !root }]"></i>
        </a>
    </template>
    <template #end>
        <div class="flex items-center gap-2">
            <InputText placeholder="Search" type="text" class="w-32 sm:w-auto" />
            <Avatar image="/images/avatar/amyelsner.png" shape="circle" />
        </div>
    </template>
</Menubar>

  
  <div class="landing-page">
    <div class="content">
      <p class="badge">Launching 2025</p>
      <h1>Your future is <span class="accent">Luvon</span></h1>
      <p class="subtitle">
        Accelerate your research with
        <span class="highlight">smart tools</span> and
        <span class="highlight">advanced data entry</span>.
      </p>
      <div class="button-group">
        <SignInButton asChild>
          <button class="btn-primary">Begin my journey</button>
        </SignInButton>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Playfair+Display:ital,wght@1,700&display=swap");

.landing-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1a1a, #000000);
  color: #f2f2f2;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.content {
  text-align: center;
  max-width: 900px;
  padding: 2rem;
}

.badge {
  background: rgba(255, 255, 255, 0.05);
  padding: 0.5rem 1rem;
  border-radius: 9999px;
  font-size: 0.85rem;
  display: inline-block;
  margin-bottom: 1rem;
  color: #aaa;
}

h1 {
  font-family: "Inter", sans-serif;
  font-size: 4rem;
  font-weight: 700;
  line-height: 1.2;
  color: #ffffff;
}

.accent {
  font-family: "Playfair Display", serif;
  font-style: italic;
  font-weight: 700;
  color: #d6d6d6;
}

.subtitle {
  font-size: 1.25rem;
  margin-top: 1.5rem;
  margin-bottom: 2rem;
  color: #bbb;
  line-height: 1.6;
}

.highlight {
  color: #00e7a0;
}

.button-group {
  display: flex;
  justify-content: center;
}

.btn-primary {
  padding: 1rem 2rem;
  font-size: 1.1rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 9999px;
  color: #f2f2f2;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.3s ease, border-color 0.3s ease;
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
}

.btn-primary:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
}
</style>
