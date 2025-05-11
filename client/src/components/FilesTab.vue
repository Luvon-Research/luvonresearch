<script setup>
import { ref, computed, onMounted } from "vue";
import { useFileDialog } from "@vueuse/core";
import { useOrganization, useSession, useClerk } from "@clerk/vue";
import Button from "primevue/button";
import Dialog from "primevue/dialog";
import InputText from "primevue/inputtext";
import FloatLabel from "primevue/floatlabel";
import IconField from "primevue/iconfield";
import InputIcon from "primevue/inputicon";
import Avatar from "primevue/avatar";
import ProgressSpinner from "primevue/progressspinner";
import axios from 'axios';

const { organization } = useOrganization();
const { session } = useSession();
const { clerk } = useClerk();

const visible = ref(false);
const sheetName = ref("");
const selectedFile = ref(null);
const uploadedFiles = ref([]);
const searchQuery = ref("");
const loading = ref(false);
const error = ref(null);
const fileViewerUrl = ref(null);
const showPreview = ref(false);
const selectedPreviewFile = ref(null);
const organizationId = computed(() => organization.value?.id);

const API_URL = import.meta.env.VITE_API_URL;

const { open, onChange } = useFileDialog({ accept: "*/*" });

const userCache = ref(new Map()); // Cache to store user data

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

const handleCreate = async () => {
  if (!selectedFile.value || !organizationId.value) {
    error.value = "No file selected or organization not found.";
    return;
  }

  if (!session.value) {
    error.value = "You must be logged in to upload files.";
    return;
  }

  const formData = new FormData();
  formData.append('file', selectedFile.value);
  formData.append('org_id', organizationId.value);

  try {
    loading.value = true;
    await axios.post(`${API_URL}/api/files/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Bearer ${session.value.id}`
      },
    });
    await fetchFiles(); // Refresh the file list
    visible.value = false;
    selectedFile.value = null;
    error.value = null;
  } catch (err) {
    console.error("Upload error:", err);
    error.value = 'Failed to upload file.';
  } finally {
    loading.value = false;
  }
};

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + " KB";
  if (bytes < 1073741824) return (bytes / 1048576).toFixed(1) + " MB";
  return (bytes / 1073741824).toFixed(1) + " GB";
}

// Function to get user data
const getUserData = async (userId) => {
  // Check if we already have this user's data in cache
  if (userCache.value.has(userId)) {
    return userCache.value.get(userId);
  }
  
  try {
    // Since Clerk is not available, just format the user ID
    // Format the user ID to be more readable
    const userData = {
      fullName: userId.replace('user_', ''),
      imageUrl: '',
    };
    
    // Cache the result
    userCache.value.set(userId, userData);
    return userData;
  } catch (err) {
    console.error(`Error processing user data for ${userId}:`, err);
    // Return a fallback object
    return { 
      fullName: userId.replace('user_', ''), 
      imageUrl: '' 
    };
  }
};

const fetchFiles = async () => {
  if (!organizationId.value) return;

  try {
    loading.value = true;
    const response = await axios.get(`${API_URL}/api/files/${organizationId.value}`);
    console.log("Files response:", response.data);
    
    // Process files first
    const processedFiles = response.data.map(file => {
      const fileName = file.file_path ? file.file_path.split('/').pop() : 'Unnamed File';
      
      return {
        id: file.id || '',
        name: fileName,
        file_path: file.file_path, // Store the original file_path
        size: formatFileSize(file.size || 0),
        uploader_id: file.uploader_id || 'Unknown',
        date: file.created_at ? new Date(file.created_at).toLocaleDateString("en-US", {
          month: "short",
          day: "numeric",
          year: "numeric",
        }) : 'Unknown date'
      };
    });
    
    // Set files first so UI can render
    uploadedFiles.value = processedFiles;
    
    // Then fetch user data for each file
    for (const file of processedFiles) {
      if (file.uploader_id && file.uploader_id !== 'Unknown') {
        const userData = await getUserData(file.uploader_id);
        file.uploader_name = userData.fullName;
        file.uploader_image = userData.imageUrl;
      } else {
        file.uploader_name = 'Unknown User';
        file.uploader_image = '';
      }
    }
    
    console.log("Processed files with user data:", uploadedFiles.value);
  } catch (err) {
    console.error("Error fetching files:", err);
    error.value = 'Failed to fetch files.';
  } finally {
    loading.value = false;
  }
};

// Add this function to get a signed URL for a file
const getSignedUrl = async (filePath) => {
  try {
    // Extract just the filename from the path
    const fileName = filePath.split('/').pop();
    
    // Encode just the filename
    const encodedFileName = encodeURIComponent(fileName);
    console.log("Requesting signed URL for:", encodedFileName);
    
    const response = await axios.get(`${API_URL}/api/files/signed-url/${encodedFileName}`, {
      headers: {
        'Authorization': `Bearer ${session.value.id}`
      }
    });
    
    console.log("Signed URL response:", response.data);
    return response.data.signed_url || response.data.url; 
  } catch (err) {
    console.error("Error getting signed URL:", err);
    error.value = 'Failed to get file URL.';
    return null;
  }
};

// Update the click handler for file rows
const handleFileClick = async (file) => {
  try {
    loading.value = true;
    selectedPreviewFile.value = file;
    // Get a signed URL for the file
    const signedUrl = await getSignedUrl(file.file_path);
    if (signedUrl) {
      fileViewerUrl.value = signedUrl;
      showPreview.value = true;
    }
  } catch (err) {
    console.error("Error opening file:", err);
    error.value = 'Failed to open file.';
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchFiles();
});
</script>

<template>
  <!-- Show loading spinner when loading -->
  <div v-if="loading" class="loading-container">
    <ProgressSpinner />
    <p>Loading files...</p>
  </div>
  
  <!-- Show empty state only when not loading and no files -->
  <div v-else-if="uploadedFiles.length === 0" class="empty-state">
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

  <!-- Show file list when not loading and files exist -->
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
            @click="handleFileClick(file)"
            style="cursor: pointer"
          >
            <td>{{ file.name }}</td>
            <td>{{ file.size }}</td>
            <td class="uploader-cell">
              <Avatar 
                v-if="file.uploader_image" 
                :image="file.uploader_image" 
                shape="circle" 
                size="small" 
                class="uploader-avatar"
              />
              <span>{{ file.uploader_name || file.uploader_id }}</span>
            </td>
            <td>{{ file.date }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <Dialog 
      v-model:visible="showPreview" 
      modal 
      :header="selectedPreviewFile ? selectedPreviewFile.name : 'File Preview'" 
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

.uploader-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.uploader-avatar {
  width: 24px;
  height: 24px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 50vh;
  gap: 1rem;
}
</style>
