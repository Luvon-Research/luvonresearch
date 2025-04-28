<template>
  <div>
    <NavBar />
    <slot />
  </div>
</template>

<script setup>
definePageMeta({
  layout: 'dashboard'
})
</script> 