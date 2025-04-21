<script setup>
import Menubar from 'primevue/menubar';
import InputText from 'primevue/inputtext';
import { ref } from 'vue';
import { useUser, SignedIn, UserButton, OrganizationSwitcher, OrganizationProfile, CreateOrganization } from '@clerk/vue';

const { user } = useUser();

const items = ref([
  {
    label: 'Dashboard',
    icon: 'pi pi-home'
  },
  {
    isSwitcherPlaceholder: true
  }
]);
</script>

<template>
  <Menubar :model="items" class="navbar">
    <template #start>
      <span class="logo-text">Luvon</span>
    </template>

    <template #item="{ item, props, hasSubmenu, root }">
      <a v-if="!item.isSwitcherPlaceholder" v-ripple class="flex items-center" v-bind="props.action">
        <span :class="item.icon" />
        <span class="ml-2">{{ item.label }}</span>
        <span v-if="hasSubmenu" class="pi pi-fw pi-angle-down ml-2" />
      </a>
      <div v-else class="flex items-center px-3">
        <OrganizationSwitcher :appearance="{
          elements: {
            organizationSwitcherTrigger: {
              padding: '0.5rem',
            }
          }
        }" />
      </div>
    </template>

    <template #end>
      <div class="flex items-center gap-2">
        <InputText placeholder="Search" type="text" class="w-32 sm:w-auto" />
        <div class="user-button-wrapper">
          <UserButton :appearance="{
            elements: {
              userButtonAvatarBox: {
                width: '40px',
                height: '40px',
                marginLeft: '25px'
              }
            }
          }" />
        </div>
      </div>
    </template>
  </Menubar>
</template>

<style scoped>
.navbar {
  padding: 0.5rem;
  background: rgb(255, 255, 255);
  border: 1px solid rgb(255, 255, 255);
  border-radius: 6px;
}

.logo-text {
  font-size: 1.5rem;
  font-weight: bold;
  color: black;
}

:deep(.p-menubar) {
  border: none;
  padding: 0;
}

:deep(.p-menuitem-link) {
  padding: 0.75rem 1.5rem; /* Increased horizontal padding for more spacing */
  color: rgb(101, 0, 0);
  transition: background-color 0.2s, color 0.2s;
  margin: 0 0.5rem; /* Added margin between menu items */
}

:deep(.p-menuitem-link:hover) {
  background-color: var(--color-background-soft);
  color: black;
}

:deep(.p-inputtext) {
  padding: 0.5rem;
  font-size: 0.875rem;
  color: black;
}



.user-button-wrapper {
  display: inline-block;
  /* padding-top: 4px; */ /* Remove or comment out the padding */
  transform: translateY(10px); /* Adjust this value to move the button down */
}

.navbar :deep(.p-menuitem):has(> div > .cl-organizationSwitcherTrigger):hover > .p-menuitem-content {
    background-color: transparent; /* Prevent hover background */
}

</style>
