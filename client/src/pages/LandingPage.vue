<script setup>
import { ref } from 'vue';
</script>

<template>
  <div class="landing-page">
    <div class="content">
      <p class="badge">Launching 2025</p>
      <h1>
        Your future is <span class="accent">Luvon</span>
      </h1>
      <p class="subtitle">Accelerate your research with <span class="highlight">smart tools</span> and <span class="highlight">advanced data entry</span>.</p>
      <div class="button-group">
        <button class="btn-primary">Begin my journey</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Playfair+Display:ital,wght@1,700&display=swap');

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
  font-family: 'Inter', sans-serif;
  font-size: 4rem;
  font-weight: 700;
  line-height: 1.2;
  color: #ffffff;
}

.accent {
  font-family: 'Playfair Display', serif;
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
