<template>
  <div class="relative min-h-screen bg-white px-4 pt-6" v-cloak>
    <!-- Upload Files Trigger Button at Top Right -->
    <div class="flex justify-end mb-4">
      <button
        class="flex items-center gap-2 px-5 py-2 bg-green-100 text-black font-bold rounded-full border border-green-300 hover:bg-green-200 transition"
        @click="showModal = true"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
        </svg>
        Upload File
      </button>
    </div>

    <!-- Blurred Overlay -->
    <div v-if="showModal" class="fixed inset-0 z-40 backdrop-blur-sm bg-green-50/60"></div>

    <!-- File Manager Table -->
    <div class="relative z-0" :class="{ 'pointer-events-none select-none': showModal }">
      <div class="mt-6 bg-white rounded-lg overflow-hidden shadow-none min-h-[400px]">
        <div class="flex items-center justify-between px-4 py-3 border-b border-gray-200">
          <div class="flex gap-4 text-sm font-bold text-black">
            <button @click="activeTab = 'all'" :class="{ 'border-b-2 border-green-600 pb-1': activeTab === 'all' }">View all</button>
            <button @click="activeTab = 'your'" :class="{ 'border-b-2 border-green-600 pb-1': activeTab === 'your' }">Your files</button>
            <button @click="activeTab = 'shared'" :class="{ 'border-b-2 border-green-600 pb-1': activeTab === 'shared' }">Shared files</button>
          </div>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search files..."
            class="border border-gray-300 rounded-md px-3 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-green-400 font-bold"
          />
        </div>
        <table class="w-full text-sm text-left">
          <thead class="bg-green-50 text-black font-bold">
            <tr>
              <th class="px-6 py-3">File name</th>
              <th class="px-6 py-3">File size</th>
              <th class="px-6 py-3">Uploaded</th>
              <th class="px-6 py-3">Uploaded by</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="file in filteredFiles"
              :key="file.name + file.date"
              class="border-t hover:bg-green-50"
            >
              <td class="px-6 py-3 text-black font-bold">{{ file.name }}</td>
              <td class="px-6 py-3 text-black font-bold">{{ file.size }}</td>
              <td class="px-6 py-3 text-black font-bold">{{ file.date }}</td>
              <td class="px-6 py-3 text-black font-bold">You</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Upload Modal -->
    <div
      v-if="showModal"
      class="fixed inset-0 z-50 flex items-center justify-center"
      @click.self="showModal = false"
    >
      <!-- Modal Content -->
      <div class="relative bg-green-50 w-full max-w-lg rounded-lg p-6 border z-10">
        <h2 class="text-xl font-bold mb-2 text-black">Upload file</h2>
        <p class="text-sm text-black mb-4 font-bold">Add your files or documents here</p>

        <div
          class="border-2 border-dashed border-green-400 rounded-md p-6 text-center cursor-pointer hover:bg-green-100"
          @click="$refs.fileInput.click()"
        >
          <input
            ref="fileInput" multiple
            type="file"
            class="hidden"
            @change="handleUpload"
          />
          <div class="flex flex-col items-center">
            <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mb-2">
              <svg class="w-5 h-5 text-black" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M7 10l5-5m0 0l5 5m-5-5v12" />
              </svg>
            </div>
            <p class="text-black text-sm font-bold">
              Drop your files here,
              <span class="text-black underline">or click to browse</span>
            </p>
          </div>
        </div>

        <div class="text-sm text-black mt-4 flex justify-between font-bold">
          <span>Supported files: .docx, .png, .webp, .cvs, .txt, .zip</span>
          <span>Maximum size: 10MB</span>
        </div>

        <button
          class="mt-6 w-full bg-green-500 text-white py-2 rounded-md hover:bg-green-600 transition font-bold"
          @click="submitUpload"
        >
          Continue
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const showModal = ref(false);
const uploadedFiles = ref([]);
const activeTab = ref('all');
const searchQuery = ref('');

const filteredFiles = computed(() => {
  return uploadedFiles.value.filter(file =>
    file.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  );
});

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
  if (bytes < 1073741824) return (bytes / 1048576).toFixed(1) + ' MB';
  return (bytes / 1073741824).toFixed(1) + ' GB';
}

function handleUpload(event) {
  const files = Array.from(event.target.files);
  files.forEach(file => {
    uploadedFiles.value.push({
      name: file.name,
      size: formatFileSize(file.size),
      date: new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    });
  });
  showModal.value = false;
  event.target.value = null;
}

function submitUpload() {
  showModal.value = false;
}
</script>

<style scoped>
</style>
