<script setup>
import Menubar from "primevue/menubar";
import Button from "primevue/button";
import InputText from "primevue/InputText";
import Badge from "primevue/badge";
import Avatar from "primevue/avatar";

import { ref } from "vue";
const items = ref([
  { label: 'Home', icon: 'pi pi-home' },
]);

import { SignedIn, SignedOut, SignInButton } from '@clerk/vue';
import { useAuth } from '@clerk/vue';
import { useRouter } from 'vue-router';
import { watchEffect } from 'vue';

const { isSignedIn } = useAuth();
const router = useRouter();

watchEffect(() => {
  if (isSignedIn.value) {
    router.push({ name: 'Dashboard' });
  }
});
</script>

<template>
  <div class="landing-container">
    <Menubar class="menubar" :model="items">
      <template #start>
        <!-- your logo SVG -->
      </template>
      <template #end>
        <div class="actions">
          <SignInButton mode="modal" asChild>
            <a class="login-signup">Login/Sign Up</a>

          </SignInButton>
        </div>
      </template>
    </Menubar>

    <div class="landing-page">
      <div class="content">
        <p class="badge">Launching 2025</p>
        <h1>Your future is <span class="gradientText">Luvon</span></h1>
        <p class="subtitle">
          Accelerate your research with
          <span class="highlight">smart tools</span> and
          <span class="highlight">advanced data entry</span>.
        </p>
        <div>
          <SignInButton mode="modal" asChild>
            <Button icon="pi pi-send" class="get-started-btn2" label="Begin my journey" />
          </SignInButton>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Playfair+Display:ital,wght@1,700&display=swap");

.login-signup{
  margin-right: 1rem;
  font-weight: bold;
  text-decoration: none;
  cursor: pointer;
}
/* -------------- Container + Orbs -------------- */
.landing-container {
  position: relative;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  overflow: hidden;
  background-color: #0d0d0d; /* fallback */
}
.landing-container::before {
  content: "";
  position: absolute;
  top: -20%;
  left: -15%;
  width: 700px;
  height: 700px;
  background: radial-gradient(circle at center, rgba(0,201,255,0.6), transparent 70%);
  filter: blur(200px);
  z-index: 0;
}
.landing-container::after {
  content: "";
  position: absolute;
  bottom: -20%;
  right: -15%;
  width: 800px;
  height: 800px;
  background: radial-gradient(circle at center, rgba(146,254,157,0.6), transparent 70%);
  filter: blur(200px);
  z-index: 0;
}

/* -------------- Navbar -------------- */
.menubar {
  position: relative;
  z-index: 1;
  background: transparent !important;
  border: none;
}

/* -------------- Page Content -------------- */
.landing-page {
  position: relative;
  z-index: 1;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}
.content {
  text-align: center;
  padding: 2rem;
  color: #f2f2f2;
}

/* -------------- Typography & Badges -------------- */
.badge {
  display: inline-block;
  background: rgba(255,255,255,0.05);
  color: #aaa;
  padding: 0.5rem 1rem;
  border-radius: 9999px;
  margin-bottom: 1rem;
  font-size: 0.85rem;
}
h1 {
  font-family: "Inter", sans-serif;
  font-size: 4rem;
  font-weight: 700;
  line-height: 1.2;
  margin: 0.5rem 0;
}
.subtitle {
  font-size: 1.25rem;
  color: #bbb;
  margin: 1.5rem 0 2rem;
  line-height: 1.6;
}
.highlight {
  color: #00e7a0;
}

/* -------------- Gradient Text -------------- */
.gradientText {
  background: linear-gradient(to bottom right, #00C9FF 0%, #92FE9D 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-family: "Playfair Display", serif;
  font-weight: 700;
}

/* -------------- Buttons -------------- */

/* -------------- “Get Started” Navbar Button -------------- */
.actions .get-started-btn {
  font-size: 0.875rem;
  font-weight: 700;
}

.get-started-btn2 {
  font-size: 0.875rem;
  font-weight: bold;
}

/* -------------- Clerk Sign‑In Override -------------- */
button:focus {
  outline: none;
}
</style>
