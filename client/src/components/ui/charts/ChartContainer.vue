<script setup lang="ts">
import Skeleton from 'primevue/skeleton';

const { title, loading } = defineProps<{
  title: string;
  loading?: boolean;
}>();
</script>

<template>
  <div class="chart-card">
    <header class="chart-card__header">{{ title }}</header>
    <div class="chart-card__body">
      <!-- static placeholder when loading -->
      <Skeleton
        v-if="loading"
        width="100%"
        height="100%"
        animation="none"
      />
      <div v-else class="chart-card__chart">
        <!-- your real chart goes here -->
      </div>
    </div>
  </div>
</template>

<style scoped>
.chart-card {
  background: #fff;
  border-radius: var(--border-radius-md);
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  overflow: hidden;
  height: 480px;
  display: flex;
  flex-direction: column;
}
.chart-card__header {
  padding: 1rem;
  font-weight: bold;
  border-bottom: 1px solid var(--surface-border);
}
.chart-card__body {
  flex: 1;
  background: var(--surface-ground);
  position: relative;
}
</style>