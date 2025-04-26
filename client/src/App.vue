<script setup>
// You might keep imports for global components like a Navbar or Footer here
// import TheWelcome from './components/TheWelcome.vue' // Example if you had other components

</script>

<template>
  <header>

  </header>

  <main>
    <!-- RouterView will render the component for the current route -->
    <RouterView /> 
  </main>

</template>

<style scoped>
/* Keep or modify your global styles */



.logo {
  display: block;
  margin: 0 auto 2rem;
}

nav {
  width: 100%;
  font-size: 12px;
  text-align: center;
  margin-top: 2rem;
}

nav a.router-link-exact-active {
  color: var(--color-text);
}

nav a.router-link-exact-active:hover {
  background-color: transparent;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
}

nav a:first-of-type {
  border: 0;
}

</style>