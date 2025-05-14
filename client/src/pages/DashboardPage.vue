<script setup>
import { ref, computed, onMounted, watch, onBeforeMount } from "vue";
import { useRouter } from "vue-router";
import { useSession, useOrganization } from "@clerk/vue";
import ProgressSpinner from "primevue/progressspinner";
import NavBar from "@/components/NavBar.vue";
import ResearchCenter from "@/components/ResearchCenter.vue";

import CreateSheetButton from "@/components/CreateSheetButton.vue";
import SheetBlock from "@/components/SheetBlock.vue";
import SheetChat from "@/components/SheetChat.vue";

import Popover from "primevue/popover";
import InputText from "primevue/inputtext";
import InputGroup from "primevue/inputgroup";
import Button from "primevue/button";
import ChartsTab from "../components/ChartsTab.vue";
import FilesTab from "../components/FilesTab.vue";

const router = useRouter();
const showChat = ref(false);

function toggleChat() {
  showChat.value = !showChat.value;
}

// Use Clerk hooks
const { session } = useSession();
const { organization } = useOrganization();

// API URL from environment
let API_URL = import.meta.env.VITE_API_URL;

// Initialize sheets as an empty array (will be populated from API)
const sheets = ref([]);
const selectedSheetId = ref(null);
const loading = ref(true);

// Function to fetch sheets from API
async function fetchSheets() {
  loading.value = true;
  // Reset selection when fetching new sheets
  // selectedSheetId.value = null; // Optional: Reset while loading

  if (!organization.value?.id) {
    sheets.value = []; // Clear sheets if no org
    selectedSheetId.value = null; // Ensure no sheet is selected
    console.log("No organization selected, clearing sheets.");
    loading.value = false;
    return;
  }

  console.log(`Fetching sheets for org: ${organization.value.id}`);
  try {
    if (API_URL.startsWith("http://")) {
      API_URL = API_URL.replace(/^http:\/\//, "https://");
    }

    const response = await fetch(
      `${API_URL}/api/sheets/organization/${organization.value.id}`,
      {
        headers: {
          Authorization: `Bearer ${session.value.id}`, // Use actual session token
        },
      }
    );

    if (!response.ok) {
      loading.value = false;
      throw new Error(`Failed to fetch sheets: ${response.statusText}`);
    }

    const data = await response.json();
    sheets.value = data.map((sheet) => ({
      id: sheet.id,
      name: sheet.name,
      // Add created_at if available and you want to sort by it
      // created_at: sheet.created_at
    }));

    console.log("Fetched sheets:", sheets.value);

    // --- Set default selection ---
    if (sheets.value.length > 0) {
      // Optional: Sort sheets if needed, e.g., by name or created_at
      // sheets.value.sort((a, b) => new Date(b.created_at) - new Date(a.created_at)); // Sort newest first

      // Select the first sheet in the (potentially sorted) list
      let storedSheet = window.localStorage.getItem("selectedSheet");
      console.log("STORED SHEET: ", storedSheet);
      if (storedSheet !== null && storedSheet !== undefined) {
        selectedSheetId.value = storedSheet;
      } else {
        selectedSheetId.value = sheets.value[0].id;
        window.localStorage.setItem("selectedSheet", selectedSheetId.value);
      }
      console.log(`Default sheet selected: ${selectedSheetId.value}`);
    } else {
      // No sheets found for the org
      selectedSheetId.value = null; // Ensure nothing is selected
      console.log("No sheets found for this organization.");
      // Optionally add a placeholder message to sheets.value if needed for UI
      // sheets.value = [{ name: "No sheets found", id: null }];
    }

    loading.value = false;
    // --- End default selection ---
  } catch (err) {
    console.error("Error fetching sheets:", err);
    sheets.value = []; // Clear sheets on error
    selectedSheetId.value = null; // Ensure no selection on error
    loading.value = false;
    // Optionally add placeholder error message to sheets.value
    // sheets.value = [{ name: "Error loading sheets", id: null }];
  }
}

onBeforeMount(() => {
  let storedPage = window.localStorage.getItem("selectedPage");

  console.log(storedPage);

  if (storedPage !== undefined && storedPage !== null) {
    setSelectPage(storedPage, window.localStorage.getItem("selectedSheet"));
  }
});

// Fetch sheets when component mounts or organization changes
onMounted(async () => {
  await fetchSheets();
});

watch(
  () => organization.value?.id,
  (newOrgId, oldOrgId) => {
    if (newOrgId !== oldOrgId) {
      fetchSheets();
    }
  }
);

// Handle sheet created event from CreateSheetButton
function handleSheetCreated(newSheet) {
  // Assuming event passes the new sheet data
  fetchSheets(); // Refetch the list to include the new one
  // Optionally, directly select the newly created sheet
  // if (newSheet && newSheet.id) {
  //   selectedSheetId.value = newSheet.id;
  // }
}

// Popover reference and toggle
const op = ref();
const toggle = (event) => {
  if (sheets.value.length === 0) {
    selectedPage.value = "sheets";
  } else {
    op.value.toggle(event);
  }
};

// Search term reactive ref
const searchTerm = ref("");

const selectedPage = ref("sheets");

function setSelectPage(page, sheetId = null) {
  selectedPage.value = page; // Set the page regardless
  console.log("SETTING TO: ", page);
  window.localStorage.setItem("selectedPage", page);

  if (page === "sheets") {
    // Only update selectedSheetId if a specific sheetId is provided (from popover click)
    // Don't set it to null here if just switching back to the 'sheets' tab
    if (sheetId !== null) {
      selectedSheetId.value = sheetId;
      console.log(`Sheet selected via popover: ${sheetId}`);
    } else if (!selectedSheetId.value && sheets.value.length > 0) {
      // If switching back to sheets tab and nothing is selected, select the default (first)
      selectedSheetId.value = sheets.value[0].id;
      console.log(
        `Switched to sheets tab, selecting default: ${selectedSheetId.value}`
      );
    }

    window.localStorage.setItem("selectedSheet", selectedSheetId.value);

    // Hide popover if it was used to select a sheet
    if (op.value && sheetId !== null) {
      op.value.hide();
    }
  }
  // If switching away from sheets, selectedSheetId remains unchanged
}

// Computed property to get the name of the selected sheet for the button
const selectedSheetName = computed(() => {
  if (!selectedSheetId.value) {
    return "Sheets"; // Default text when nothing is selected
  }
  const selected = sheets.value.find((s) => s.id === selectedSheetId.value);
  return selected ? selected.name : "Sheets"; // Show name or default if somehow not found
});

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
              {{ selectedSheetName }}
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
                    :key="sheet.id"
                    class="d-flex align-items-center sheet-result"
                    @click="setSelectPage('sheets', sheet.id)"
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

            <button
              class="options-tab-btn ai-assistant-btn"
              @click="toggleChat"
            >
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

          <div v-if="selectedPage === 'sheets'">
            <CreateSheetButton @sheet-created="handleSheetCreated" />
          </div>
        </div>

        <div class="tab-page-container">
          <div v-if="!loading">
            <div v-if="selectedPage === 'sheets'">
              <div v-if="sheets.length !== 0">
                <SheetBlock :sheet-id="selectedSheetId" />
              </div>
              <div v-if="sheets.length === 0">
                <center style="margin-top: 10vh">
                  <img src="../assets/void.svg" class="no-sheets-img" />
                  <h1 class="no-sheets-title">No Sheets Yet</h1>
                  <p class="no-sheets-subtitle">
                    Create a sheet to get started by clicking the create sheet
                    button at the top
                  </p>
                </center>
              </div>
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

          <div v-if="loading">
            <center style="margin-top: 30vh">
              <ProgressSpinner
                style="width: 40px; height: 40px"
                strokeWidth="3"
                fill="transparent"
                animationDuration=".5s"
                aria-label="Custom ProgressSpinner"
              />
            </center>
          </div>
        </div>
      </div>

      <transition name="slide">
        <SheetChat
          v-if="showChat"
          class="sheet-chat"
          :sheet-id="selectedSheetId"
          :context-name="selectedSheetName"
          :context-type="selectedPage"
          @close="toggleChat"
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
  background-color: white; /* White background */
  border: 1px solid #f0f0f0; /* Lighter border */
  padding: 0.4rem 0.8rem; /* Adjust padding for size */
  font-size: 0.875rem;
  color: #333; /* Dark text color */
  border-radius: 6px; /* Slightly more rounded corners */
  box-shadow: none; /* Remove shadow */
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  transition: background-color 0.2s ease, border-color 0.2s ease; /* Smooth transition */
}

.options-tab-btn:hover {
  background-color: #f9f9f9; /* Softer light gray on hover */
  border-color: #e0e0e0; /* Slightly darker border on hover */
}

.options-tab-btn:active {
  background-color: #e0e0e0; /* Darker shade when active */
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
  height: 100%;
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

.no-sheets-img {
  margin-top: 20vh;
  width: 10rem;
}

.no-sheets-title {
  font-size: 30px;
}

.no-sheets-subtitle {
  color: gray;
  width: 30%;
}
</style>
