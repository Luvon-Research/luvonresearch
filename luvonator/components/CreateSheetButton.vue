<script setup>
import { ref, computed } from "vue";
import { useFileDialog } from "@vueuse/core";
import Button from "primevue/button";
import Dialog from "primevue/dialog";
import InputText from "primevue/inputtext";
import FloatLabel from "primevue/floatlabel";

const visible = ref(false);
const sheetName = ref("");
const selectedFile = ref(null);
const { open, onChange } = useFileDialog({
  accept: ".csv",
});

onChange((files) => {
  if (files) {
    selectedFile.value = files[0];
  }
});

const handleDrop = (e) => {
  e.preventDefault();
  const file = e.dataTransfer.files[0];
  if (file && file.type === "text/csv") {
    selectedFile.value = file;
  }
};

const handleDragOver = (e) => {
  e.preventDefault();
};

const isCreateEnabled = computed(() => {
  return sheetName.value.trim() !== "" || selectedFile.value !== null;
});

const handleCreate = () => {
  // Handle creation/import logic here
  console.log("Sheet name:", sheetName.value);
  if (selectedFile.value) {
    console.log("Importing:", selectedFile.value);
  }
  visible.value = false;
};
</script>

<template>
  <Button label="Create Sheet" icon="pi pi-plus" @click="visible = true" severity="secondary"/>

  <Dialog
    v-model:visible="visible"
    modal
    header="Create New Sheet"
    :style="{ width: '35vw', maxWidth: '30rem' }"
  >
    <div class="create-sheet-form">
      <div class="sheet-name-section">
        <div class="input-wrapper">
          <FloatLabel>
            <InputText
              id="sheetName"
              v-model="sheetName"
            />
            <label for="sheetName">Sheet Name</label>
          </FloatLabel>
        </div>
      </div>

      <div class="divider">
        <span class="divider-text">or</span>
      </div>

      <div class="import-section">
        <h3>Import from CSV</h3>
        <div class="drop-zone" @drop="handleDrop" @dragover="handleDragOver">
          <i class="pi pi-upload"></i>
          <p>Drag and drop your CSV file here</p>
          <p>or</p>
          <Button
            label="Browse Files"
            @click="open"
            severity="secondary"
            text
          />
          <p v-if="selectedFile" class="selected-file">
            Selected: {{ selectedFile.name }}
          </p>
        </div>
      </div>

      <Button
        :disabled="!isCreateEnabled"
        label="Create Sheet"
        class="create-button"
        @click="handleCreate"
      />
    </div>
  </Dialog>
</template>

<style scoped>
.create-sheet-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.5rem;
}

.sheet-name-section,
.import-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.sheet-name-section h3,
.import-section h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.1rem;
  font-weight: 600;
}

.input-wrapper {
  width: 100%;
}

.input-wrapper :deep(.p-inputtext) {
  width: 100%;
  padding: 0.75rem;
  font-size: 1rem;
}

.divider {
  position: relative;
  text-align: center;
  margin: 0.5rem 0;
}

.divider::before {
  content: "";
  position: absolute;
  left: 0;
  top: 50%;
  width: 45%;
  height: 1px;
  background: #dee2e6;
}

.divider::after {
  content: "";
  position: absolute;
  right: 0;
  top: 50%;
  width: 45%;
  height: 1px;
  background: #dee2e6;
}

.divider-text {
  background: white;
  padding: 0 1rem;
  color: #6c757d;
  position: relative;
  z-index: 1;
}

.drop-zone {
  border: 2px dashed #dee2e6;
  border-radius: 6px;
  padding: 2rem;
  text-align: center;
  background: #f8f9fa;
  cursor: pointer;
  transition: border-color 0.2s;
}

.drop-zone:hover {
  border-color: #6c757d;
}

.drop-zone i {
  font-size: 2rem;
  color: #6c757d;
  margin-bottom: 1rem;
}

.drop-zone p {
  margin: 0.5rem 0;
  color: #6c757d;
}

.selected-file {
  margin-top: 1rem !important;
  color: #2c3e50 !important;
  font-weight: 500;
}

.create-button {
  width: 100%;
  padding: 0.75rem;
}
</style>
