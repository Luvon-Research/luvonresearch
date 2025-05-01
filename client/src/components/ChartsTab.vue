<script setup>
import { ref, computed } from 'vue';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import MultiSelect from 'primevue/multiselect';
import ChartContainer from '@/components/ui/charts/ChartContainer.vue';

// State
const searchTerm = ref('');
const showDialog = ref(false);
const promptText = ref('');
const selectedDataSources = ref([]);
const dataSourceOptions = [
  'Sales Data',
  'Energy Data',
  'Water Data',
  'Emissions Data',
  'Temperature Data'
];

// Placeholder charts (10 items)
const charts = ref(
  Array.from({ length: 10 }, (_, i) => ({ id: i + 1, title: `Chart ${i + 1}` }))
);

// Filter charts by search
const filteredCharts = computed(() =>
  charts.value.filter(c =>
    c.title.toLowerCase().includes(searchTerm.value.toLowerCase())
  )
);

// Open the generation dialog
const openDialog = () => {
  showDialog.value = true;
};

// Generate a new chart from prompt
const generateChart = () => {
  const nextId = charts.value.length
    ? Math.max(...charts.value.map(c => c.id)) + 1
    : 1;

  charts.value.push({
    id: nextId,
    title: `Chart ${nextId}`,
    dataSources: [...selectedDataSources.value]
  });
  promptText.value = '';
  selectedDataSources.value = [];
  showDialog.value = false;
};
</script>

<template>
  <div class="chart-page">
    <!-- Header bar with search and create -->
    <div class="header-bar">
      <InputText
        v-model="searchTerm"
        placeholder="Search charts..."
        class="search-input p-inputtext-lg"
      />
      <Button
        icon="pi pi-plus"
        severity="success"
        class="p-button-rounded p-button-lg create-btn"
        @click="openDialog"
        aria-label="Add Chart"
      />
    </div>

    <!-- Charts grid: 2 per row -->
    <div class="chart-grid">
      <ChartContainer
        v-for="chart in filteredCharts"
        :key="chart.id"
        :title="chart.title"
        :loading="!chart.dataSources"
      />
      <div v-if="!filteredCharts.length" class="no-results">
        No charts found.
      </div>
    </div>

    <!-- Generation dialog -->
    <Dialog
      v-model:visible="showDialog"
      modal
      :style="{ width: '50vw', height: '32vh' }"
      :contentStyle="{ padding: '1.5rem', height: 'calc(32vh - 3.5rem)', overflowY: 'auto' }"
      :draggable="false"
      :resizable="false"
      class="chart-dialog"
    >
      <div class="chat-dialog-content">
        <!-- Chat prompt bubble -->
        <div class="chat-prompt">
          <p>What would you like to visualize?</p>
        </div>

        <!-- User input area -->
        <div class="chat-input-area">
          <textarea
            v-model="promptText"
            placeholder="Type your description..."
            rows="3"
            class="chat-input p-inputtextarea p-inputtext"
            autofocus
          ></textarea>
        </div>

        <!-- Data source selection -->
        <div class="p-field data-field">
          <label for="dataSources">Data Sources</label>
          <MultiSelect
            id="dataSources"
            v-model="selectedDataSources"
            :options="dataSourceOptions"
            placeholder="Select data sources"
            class="data-source-select"
          />
        </div>
      </div>

      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="showDialog = false" />
        <Button
          label="OK"
          icon="pi pi-check"
          class="p-button-success p-button-lg"
          @click="generateChart"
        />
      </template>
    </Dialog>
  </div>
</template>

<style scoped>
.chart-page {
  padding: 2rem;
}
.header-bar {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}
.search-input {
  width: 400px;
}
.chart-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 2rem;
}
.no-results {
  grid-column: 1 / -1;
  text-align: center;
  color: var(--text-color-secondary);
  padding: 2rem;
}
.chart-dialog .p-dialog-header {
  background: var(--success-color) !important;
  color: #fff !important;
  font-size: 1.25rem;
}
.chart-dialog .p-dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}
.chat-dialog-content {
  max-width: 500px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}
.chat-prompt p {
  background: var(--surface-card);
  color: var(--text-color);
  padding: 1rem 1.25rem;
  border-radius: 1rem;
  font-size: 1rem;
  text-align: center;
  margin: 0 auto;
}
.chat-input-area textarea.chat-input {
  width: 100%;
  min-height: 80px;
  border-radius: 0.75rem;
  padding: 0.75rem;
  font-size: 0.95rem;
}
.data-field {
  width: 100%;
  margin: 0 auto;
}
.data-source-select {
  width: 100%;
  font-size: 0.95rem;
}
</style>