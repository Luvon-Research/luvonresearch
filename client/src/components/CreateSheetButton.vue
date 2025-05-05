<script setup>
import { ref, computed } from "vue";
import { useFileDialog } from "@vueuse/core";
import { useOrganization, useSession } from "@clerk/vue";
import Button from "primevue/button";
import Dialog from "primevue/dialog";
import InputText from "primevue/inputtext";
import FloatLabel from "primevue/floatlabel";

// API URL from environment
const API_URL = import.meta.env.VITE_API_URL;

const visible = ref(false);
const sheetName = ref("");
const selectedFile = ref(null);
const loading = ref(false);
const error = ref(null);

// Get Clerk organization and session
const { organization } = useOrganization();
const { session } = useSession();

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
  return (sheetName.value.trim() !== "" || selectedFile.value !== null) && !loading.value;
});

const handleCreate = async () => {
  if (!organization.value?.id) {
    error.value = "No active organization found";
    return;
  }

  try {
    loading.value = true;
    error.value = null;

    // Prepare sheet data
    const sheetData = {
      name: sheetName.value.trim() || 
            (selectedFile.value ? selectedFile.value.name.replace('.csv', '') : 'Untitled Sheet'),
      organization_id: organization.value.id
    };
    
    // Create the sheet first
    const response = await fetch(`${API_URL}/api/sheets`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${session.value.id}`
      },
      body: JSON.stringify(sheetData)
    });
    
    if (!response.ok) {
      throw new Error(await response.text() || 'Failed to create sheet');
    }
    
    const result = await response.json();
    console.log('Sheet created:', result);
    
    if (selectedFile.value) {
      // TO DO: Handle CSV import logic
      console.log("Importing:", selectedFile.value);
      // This would need a separate API endpoint for file uploads
    }
    
    // Reset form and close dialog
    sheetName.value = "";
    selectedFile.value = null;
    visible.value = false;
    
    // Emit event to notify parent that a sheet was created
    // This can be used to refresh the sheet list
    emit('sheet-created', result);
    
  } catch (err) {
    console.error('Error creating sheet:', err);
    error.value = err.message;
  } finally {
    loading.value = false;
  }
};

// Define emits
const emit = defineEmits(['sheet-created']);
</script>

<template>
  <Button
    class="create-sheet-btn"
    label="Create Sheet"
    icon="pi pi-plus"
    @click="visible = true"
    severity="secondary"
  />

  <Dialog
    v-model:visible="visible"
    modal
    header="Create New Sheet"
    :style="{ width: '35vw', maxWidth: '30rem' }"
  >
    <div class="create-sheet-form">
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
      
      <div class="sheet-name-section">
        <div class="input-wrapper">
          <FloatLabel>
            <InputText
              id="sheetName"
              v-model="sheetName"
              :disabled="loading"
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
        <div 
          class="drop-zone" 
          @drop="handleDrop" 
          @dragover="handleDragOver"
          :class="{ 'disabled': loading }"
        >
          <i class="pi pi-upload"></i>
          <p>Drag and drop your CSV file here</p>
          <p>or</p>
          <Button
            label="Browse Files"
            @click="open"
            severity="secondary"
            text
            :disabled="loading"
          />
          <p v-if="selectedFile" class="selected-file">
            Selected: {{ selectedFile.name }}
          </p>
        </div>
      </div>

      <Button
        :disabled="!isCreateEnabled"
        :loading="loading"
        :label="loading ? 'Creating...' : 'Create Sheet'"
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

.drop-zone:hover:not(.disabled) {
  border-color: #6c757d;
}

.drop-zone.disabled {
  opacity: 0.7;
  cursor: not-allowed;
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

.error-message {
  padding: 0.75rem;
  background-color: #ffebee;
  border-radius: 4px;
  color: #d32f2f;
  margin-bottom: 1rem;
}

.create-sheet-btn {
  background-color: #4a56e2; /* Blue background */
  color: white; /* White text */
  border: none; /* No border */
  padding: 0.5rem 1rem; /* Adjust padding for size */
  font-size: 0.875rem;
  border-radius: 6px; /* Rounded corners */
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  transition: background-color 0.2s ease; /* Smooth transition */
}

.create-sheet-btn:hover {
  background-color: #3b47b3; /* Darker blue on hover */
}
</style>
