<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";

import NavBar from "@/components/NavBar.vue";
import ResearchCenter from "@/components/ResearchCenter.vue";

import CreateSheetButton from "@/components/CreateSheetButton.vue";
import SheetBlock from "@/components/SheetBlock.vue";
import SheetChat from "@/components/SheetChat.vue";

import Popover from "primevue/popover";
import InputText from "primevue/inputtext";
import InputGroup from "primevue/inputgroup";
import InputGroupAddon from "primevue/inputgroupaddon";
import Button from "primevue/button";
import ChartsTab from "../components/ChartsTab.vue";
import FilesTab from "../components/FilesTab.vue";

const router = useRouter();
const showChat = ref(false);
function toggleChat() {
  showChat.value = !showChat.value;
}

// original sheets array
const sheets = ref([
  { name: "Test Sheet" },
  { name: "Env Data" },
  // add more as needed
]);

// Popover reference and toggle
const op = ref();
const toggle = (event) => {
  op.value.toggle(event);
};

// Search term reactive ref
const searchTerm = ref("");

const selectedPage = ref("sheets");

function setSelectPage(page) {
  if (page === "sheets") {
    toggle();
  }

  selectedPage.value = page;
}

// Computed filtered list based on searchTerm
const filteredSheets = computed(() => {
  const term = searchTerm.value.trim().toLowerCase();
  if (!term) {
    return sheets.value;
  }
  return sheets.value.filter((sheet) =>
    sheet.name.toLowerCase().includes(term)
  );
});
</script>

<template>
  <div class="dashboard-layout">
    <NavBar />
    <main class="dashboard-content">
      <div class="dashboard-wrapper" :class="{ shifted: showChat }">
        <div class="button-row">
          <div class="primary-buttons">
            <button class="options-tab-btn" @click="toggle">
              <i class="pi pi-table"></i>
              Sheets
            </button>

            <Popover ref="op">
              <div class="flex flex-col gap-4 w-[25rem]">
                <span class="popover-title">Sheets</span>

                <div class="search-box">
                  <InputGroup>
                    <InputText
                      v-model="searchTerm"
                      placeholder="Search sheets..."
                    />
                    <Button icon="pi pi-search" />
                  </InputGroup>
                </div>

                <div style="margin-top: 0.5rem">
                  <div
                    v-for="sheet in filteredSheets"
                    :key="sheet.name"
                    class="d-flex align-items-center sheet-result"
                    @click="setSelectPage('sheets')"
                  >
                    <i class="pi pi-file sheet-result-icon"></i>
                    <p class="sheet-result-name">{{ sheet.name }}</p>
                  </div>
                  <p v-if="filteredSheets.length === 0" class="no-results">
                    No sheets found.
                  </p>
                </div>
              </div>
            </Popover>

            <button class="options-tab-btn" @click="toggleChat">
              <i class="pi pi-sparkles"></i>
              AI assistant
            </button>

            <button
              class="options-tab-btn"
              @click="setSelectPage('research-center')"
            >
              <i class="pi pi-asterisk"></i>
              Research Center
            </button>

            <button class="options-tab-btn" @click="setSelectPage('charts')">
              <i class="pi pi-chart-scatter"></i>
              Charts
            </button>

            <button class="options-tab-btn" @click="setSelectPage('files')">
              <i class="pi pi-folder-open"></i>
              Files
            </button>
          </div>

          <CreateSheetButton />
        </div>

        <div class="tab-page-container">
          <div v-if="selectedPage === 'sheets'">
            <SheetBlock />
          </div>
          <div v-if="selectedPage === 'research-center'">
            <ResearchCenter />
          </div>
          <div v-if="selectedPage === 'charts'">
            <ChartsTab />
          </div>
          <div v-if="selectedPage === 'files'">
            <FilesTab />
          </div>
        </div>
      </div>

      <transition name="slide">
        <SheetChat
          v-if="showChat"
          class="sheet-chat"
          @close="showChat = false"
        />
      </transition>
    </main>
  </div>
</template>

<style scoped>
.sheet-result-icon {
  margin-top: 0.1rem;
}

.sheet-result-name {
  margin-left: 0.6rem;
  margin-top: auto;
  margin-bottom: auto;
}
.sheet-result {
  padding-inline: 0.5rem;
  padding-block: 0.5rem;
  font-weight: bold;
  background-color: transparent;
  border-radius: 10px;
}

.sheet-result:hover {
  background-color: #f2eff0;
  cursor: pointer;
}

.search-box {
  margin-top: 0.6rem;
}

.popover-title {
  font-weight: bold;
}

.no-results {
  color: #999;
  font-style: italic;
  margin-top: 0.5rem;
}

.dashboard-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.dashboard-content {
  --chat-width: 400px;
  position: relative;
  flex: 1;
  overflow: hidden;
  background: var(--color-background);
  margin-top: var(--navbar-height, 30px);
}

.dashboard-wrapper {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  right: 0;
  transition: margin-left 0.3s ease;
}

.dashboard-wrapper.shifted {
  margin-left: var(--chat-width);
}

.button-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0rem 1rem;
}

.primary-buttons {
  display: flex;
  gap: 0.5rem;
}

.options-tab-btn {
  background-color: #f0f0f0;
  border: none;
  padding: 0.4rem 0.8rem;
  font-size: 0.875rem;
  color: #333;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
}

.options-tab-btn:hover {
  background-color: #e0dfdf;
}

.options-tab-btn .pi {
  margin-right: 0.4rem;
  font-size: 1rem;
}

.tab-page-container {
  position: absolute;
  top: calc(var(--navbar-height, 64px) + 1rem);
  left: 1rem;
  right: 1rem;
  bottom: 1rem;
  background: white;
  border-radius: 8px;
  box-sizing: border-box;
  max-width: calc(100% - 2rem);
  overflow-x: auto;
  overflow-y: auto;
}

.sheet-chat {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  width: var(--chat-width);
  background: #fff;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  z-index: 2;
  overflow: hidden;
}

.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}
.slide-enter-from,
.slide-leave-to {
  transform: translateX(-100%);
}
</style>
