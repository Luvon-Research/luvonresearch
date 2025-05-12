<script setup>
import { ref, computed } from "vue";
import { useFileDialog } from "@vueuse/core";
import { useOrganization, useSession } from "@clerk/vue";
import Button from "primevue/button";
import Dialog from "primevue/dialog";
import InputText from "primevue/inputtext";
import FloatLabel from "primevue/floatlabel";
import IconField from "primevue/iconfield";
import InputIcon from "primevue/inputicon";

const CLIENT_ID = "qtc894sq3i00wq9tlt4zze1h5s000y1g";
const REDIRECT_URI = "http://localhost:5173/callback";

const redirectToBoxLogin = () => {
  const authUrl = `https://account.box.com/api/oauth2/authorize?response_type=code&client_id=${CLIENT_ID}&redirect_uri=${encodeURIComponent(
    REDIRECT_URI
  )}&state=box_login`;
  window.location.href = authUrl;
};

const visible = ref(false);
const sheetName = ref("");
const selectedFile = ref(null);
const uploadedFiles = ref([]);
const searchQuery = ref("");
const loading = ref(false);
const error = ref(null);
const fileViewerUrl = ref(null);
const showPreview = ref(false);

const { open, onChange } = useFileDialog({ accept: "*/*" });

onChange((files) => {
  if (files?.[0]) selectedFile.value = files[0];
});

const handleDrop = (e) => {
  e.preventDefault();
  const file = e.dataTransfer.files?.[0];
  if (file) selectedFile.value = file;
};

const handleDragOver = (e) => e.preventDefault();

const isCreateEnabled = computed(() => {
  return selectedFile.value !== null && !loading.value;
});

const filteredFiles = computed(() => {
  return uploadedFiles.value.filter((file) =>
    file.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  );
});

const handleCreate = () => {
  if (!selectedFile.value) {
    error.value = "No file selected.";
    return;
  }

  uploadedFiles.value.push({
    name: selectedFile.value.name,
    size: formatFileSize(selectedFile.value.size),
    uploaded_by: "You",
    date: new Date().toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    }),
    url: URL.createObjectURL(selectedFile.value),
  });

  sheetName.value = "";
  selectedFile.value = null;
  visible.value = false;
  error.value = null;
};

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + " KB";
  if (bytes < 1073741824) return (bytes / 1048576).toFixed(1) + " MB";
  return (bytes / 1073741824).toFixed(1) + " GB";
}
</script>

<template>
  <div v-if="uploadedFiles.length === 0" class="empty-state">
    <div class="upload-cta-box">
      <i class="pi pi-folder-open upload-icon"></i>
      <h2>No files uploaded yet</h2>
      <p class="upload-hint">Click below to add your first file</p>
      <Button
        class="upload-only-btn"
        label="Upload File"
        icon="pi pi-upload"
        @click="visible = true"
      />
    </div>
  </div>

  <div v-else>
    <h3 class="table-title">Uploaded Files</h3>
    <div class="top-actions">
      <IconField iconPosition="left" class="search-input">
        <InputIcon class="pi pi-search" />
        <InputText v-model="searchQuery" placeholder="Search files..." />
      </IconField>
      <Button
        class="create-sheet-btn"
        label="Upload File"
        icon="pi pi-upload"
        @click="visible = true"
      />
    </div>

    <div class="uploaded-list">
      <table class="file-table">
        <thead>
          <tr>
            <th>File Name</th>
            <th>Size</th>
            <th>Uploaded By</th>
            <th>Date</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="file in filteredFiles"
            :key="file.name + file.date"
            @click="fileViewerUrl = file.url; showPreview = true"
            style="cursor: pointer"
          >
            <td>{{ file.name }}</td>
            <td>{{ file.size }}</td>
            <td>{{ file.uploaded_by }}</td>
            <td>{{ file.date }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <Dialog
      v-model:visible="showPreview"
      modal
      header="File Preview"
      :style="{ width: '85vw', height: '90vh' }"
    >
      <iframe
        v-if="fileViewerUrl"
        :src="fileViewerUrl"
        style="width: 100%; height: 80vh; border: none"
      />
    </Dialog>
  </div>

  <Dialog
    v-model:visible="visible"
    modal
    header="Upload File"
    :style="{ width: '35vw', maxWidth: '30rem' }"
  >
    <div class="create-sheet-form">
      <div v-if="error" class="error-message">{{ error }}</div>

      <div class="drop-zone" @drop="handleDrop" @dragover="handleDragOver">
        <i class="pi pi-upload"></i>
        <p>Drag and drop your file here</p>
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

      <Button
        label="Upload with Box"
        icon="pi pi-external-link"
        class="box-button"
        @click="redirectToBoxLogin"
      />

      <Button
        :disabled="!isCreateEnabled"
        :loading="loading"
        :label="loading ? 'Uploading...' : 'Upload File'"
        class="create-button"
        @click="handleCreate"
      />
    </div>
  </Dialog>
</template>

<style scoped>
.box-button {
  background-color: #0061d5;
  color: white;
  font-weight: bold;
  border-radius: 6px;
  margin-top: 0.5rem;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  height: 80vh;
  gap: 1rem;
}

.upload-cta-box {
  padding: 2rem;
}

.upload-icon {
  font-size: 3rem;
  color: #4a56e2;
}

.upload-hint {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.upload-only-btn {
  background-color: #4a56e2;
  color: white;
  border-radius: 6px;
  font-weight: bold;
}

.top-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  gap: 1rem;
}

.search-input {
  flex-grow: 1;
  max-width: 300px;
}

.create-sheet-btn {
  background-color: #4a56e2;
  color: white;
  border-radius: 6px;
  padding: 0.5rem 1rem;
  font-weight: bold;
}

.uploaded-list {
  overflow-x: auto;
}

.table-title {
  margin-bottom: 0.75rem;
  font-weight: bold;
  font-size: 1.1rem;
  color: #000000;
}

.file-table {
  width: 100%;
  border-collapse: collapse;
}

.file-table th,
.file-table td {
  text-align: left;
  padding: 0.75rem;
  border-bottom: 1px solid #ddd;
}

.create-sheet-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.5rem 0;
}

.drop-zone {
  border: 2px dashed #cfd4ff;
  border-radius: 8px;
  background: #f3f4ff;
  padding: 2rem;
  text-align: center;
}

.drop-zone i {
  font-size: 2rem;
  color: #4a56e2;
  margin-bottom: 0.5rem;
}

.drop-zone p {
  margin: 0.3rem 0;
  color: #4a56e2;
  font-weight: 500;
}

.selected-file {
  color: #2c3e50;
  font-weight: 600;
}

.create-button {
  background-color: #4a56e2;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 0.75rem;
  font-weight: 600;
}

.error-message {
  background-color: #fdecea;
  color: #b71c1c;
  padding: 0.75rem;
  border-radius: 4px;
}
</style>
