<script setup lang="ts">
const props = defineProps<{
  title: string;
  img: string;
  description: string;
}>();
</script>

<template>
  <div class="section-2-card" >
    <!-- if you have an image, it goes here: -->
    <img v-if="props.img" :src="props.img" alt="" class="card-image" />

    <!-- this wrapper is auto-pushed to the bottom -->
    <div class="content-wrapper">
      <h3 class="title" >{{ props.title }}</h3>
      <p class="description">{{ props.description }}</p>
    </div>
  </div>
</template>

<style scoped>
.section-2-card {
  display: flex;
  flex-direction: column;
  /* push content-wrapper to bottom */
  height: 23rem;
  width: 18rem;
  background-color: #f0f0f0;
  border-radius: 10px;
  overflow: hidden;
}

/* optional: style your image if you have one */
.card-image {
  width: 100%;
  /* keep aspect ratio or crop as you like */
  object-fit: cover;
  flex-shrink: 0;
  margin-top: 1rem;
}

/* this is what sits at the bottom */
.content-wrapper {
  margin-top: auto;
  padding: 1rem;
}

.title {
  font-size: 1.5rem;
  text-align: left;
  margin: 0; /* reset default */
}

.description {
  margin-top: 0.5rem;
  text-align: left;
  color: #505050;
}

/* responsive */
@media only screen and (max-width: 600px) {
  .section-2-card {
    height: auto;
    min-height: 20rem;
    width: 80vw;
  }
}
</style>
