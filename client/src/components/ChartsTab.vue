<script setup>
import { ref, computed, nextTick, onMounted, onUnmounted, watch } from "vue";
import InputText from "primevue/inputtext";
import Button from "primevue/button";
import Dialog from "primevue/dialog";
import MultiSelect from "primevue/multiselect";
import ChartContainer from "@/components/ui/charts/ChartContainer.vue";
import Textarea from "primevue/textarea";
import Avatar from "primevue/avatar";
import ProgressSpinner from "primevue/progressspinner";
import Dropdown from "primevue/dropdown";
import Divider from "primevue/divider";
import Tooltip from "primevue/tooltip";
import { useSession, useOrganization } from "@clerk/vue";
import InputGroup from "primevue/inputgroup";
import { CodeBlock } from "vuejs-code-block";

// State
const { organization } = useOrganization();
const { session } = useSession();
const searchTerm = ref("");
const showDialog = ref(false);
const promptText = ref("");
const selectedDataSources = ref([]);
const dataSourceOptions = [
  "Data Source 1",
  "Data Source 2",
  "Data Source 3",
  "Data Source 4",
  "Data Source 5",
  "Data Source 6",
  "Data Source 7",
  "Data Source 8",
  "Data Source 9",
  "Data Source 10",
];
const selectedChart = ref(null);
const chatInput = ref("");
const messages = ref({});
const isAiTyping = ref(false);
const chatWindowRef = ref(null);
const sidebarWidth = ref(400);
const isSidebarPinned = ref(true);
const showSuggestedQuestions = ref(false);
const selectedChartPoint = ref(null);
const loadingCharts = ref(true);
const charts = ref([]);
const API_URL = import.meta.env.VITE_API_URL;
const showDetailDialog = ref(false);
const showDeleteConfirmDialog = ref(false);
const chartToDelete = ref(null);
const chartDeleteLoading = ref(false);

// Filter charts by search
const filteredCharts = computed(() =>
  charts.value.filter((c) =>
    c["chart_name"].toLowerCase().includes(searchTerm.value.toLowerCase())
  )
);

watch(
  () => organization.value?.id,
  async (newOrgId) => {
    if (!newOrgId) return; // guard against undefined
    let org_id = organization.value.id;
    let session_id = session.value.id;

    console.log(org_id, session_id);
    await getCharts();
  },
  { immediate: true } // also run on first mount when org.value.id is ready
);

// Open the generation dialog
const openDialog = () => {
  showDialog.value = true;
};

// Generate a new chart from prompt
const generateChart = () => {
  const nextId = charts.value.length
    ? Math.max(...charts.value.map((c) => c.id)) + 1
    : 1;

  charts.value.push({
    id: nextId,
    title: `Chart ${nextId}`,
    dataSources: [...selectedDataSources.value],
  });
  promptText.value = "";
  selectedDataSources.value = [];
  showDialog.value = false;
};

async function getCharts() {
  loadingCharts.value = true;
  try {
    const res = await fetch(`${API_URL}/api/files/${organization.value.id}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${session.value.id}`,
        is_chart: true,
      },
    });
    if (!res.ok) throw new Error("Fetch failed");
    const data = await res.json();
    console.log(data);
    charts.value = data;
  } catch (err) {
    console.error("Error loading chats:", err);
  } finally {
    loadingCharts.value = false;
  }
}

// Suggested questions
const suggestedQuestions = [
  "What's the highest data point?",
  "Explain this trend",
  "What are the key insights?",
  "Compare the minimum and maximum values",
  "What patterns do you see in the data?",
  "Show me year-over-year growth",
];

const openChat = (chart) => {
  selectedChart.value = chart;
  if (!messages.value[chart.id]) {
    messages.value[chart.id] = [];
  }
  showDetailDialog.value = true;
  // Auto-scroll to bottom
  nextTick(() => {
    scrollToBottom();
  });
};

const sendMessage = async () => {
  if (chatInput.value.trim() && selectedChart.value) {
    const userMessage = {
      id: Date.now(),
      text: chatInput.value,
      sender: "user",
      timestamp: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };

    messages.value[selectedChart.value.id].push(userMessage);
    chatInput.value = "";

    // Auto-scroll to bottom
    nextTick(() => {
      scrollToBottom();
    });

    // Simulate AI response
    isAiTyping.value = true;
    await new Promise((resolve) => setTimeout(resolve, 1500));

    const aiResponse = {
      id: Date.now() + 1,
      text: `I've analyzed your question about "${userMessage.text}". Based on the data in ${selectedChart.value.title}, here's what I found...`,
      sender: "ai",
      timestamp: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };

    messages.value[selectedChart.value.id].push(aiResponse);
    isAiTyping.value = false;

    nextTick(() => {
      scrollToBottom();
    });
  }
};

// Handle suggested question click
const useSuggestedQuestion = (question) => {
  chatInput.value = question;
  showSuggestedQuestions.value = false;
  sendMessage();
};

// Auto-scroll chat to bottom
const scrollToBottom = () => {
  if (chatWindowRef.value) {
    chatWindowRef.value.scrollTop = chatWindowRef.value.scrollHeight;
  }
};

// Handle keyboard shortcuts
const handleKeyDown = (e) => {
  // Enter to send message
  if (e.key === "Enter" && chatInput.value) {
    e.preventDefault();
    sendMessage();
  }

  // Press "/" to focus chat input
  if (e.key === "/" && document.activeElement.tagName !== "TEXTAREA") {
    e.preventDefault();
    const chatTextarea = document.querySelector(".chat-input-field");
    if (chatTextarea) {
      chatTextarea.focus();
    }
  }
};

// Handle sidebar resize
const startResize = (e) => {
  e.preventDefault();
  const startX = e.pageX;
  const startWidth = sidebarWidth.value;

  const doDrag = (dragEvent) => {
    const newWidth = startWidth + (startX - dragEvent.pageX);
    sidebarWidth.value = Math.min(Math.max(newWidth, 300), 600);
  };

  const stopDrag = () => {
    document.removeEventListener("mousemove", doDrag);
    document.removeEventListener("mouseup", stopDrag);
  };

  document.addEventListener("mousemove", doDrag);
  document.addEventListener("mouseup", stopDrag);
};

// Toggle sidebar pin
const toggleSidebarPin = () => {
  isSidebarPinned.value = !isSidebarPinned.value;
};

// Clear conversation
const clearConversation = () => {
  if (selectedChart.value) {
    messages.value[selectedChart.value.id] = [];
  }
};

// Handle chart element click
const handleChartElementClick = (elementData) => {
  if (selectedChart.value) {
    const contextMessage = {
      id: Date.now(),
      text: `User clicked on ${elementData.label}: ${elementData.value}`,
      sender: "system",
      timestamp: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
      context: elementData,
    };

    messages.value[selectedChart.value.id].push(contextMessage);
    selectedChartPoint.value = elementData;

    nextTick(() => {
      scrollToBottom();
    });
  }
};

// Lifecycle hooks
onMounted(() => {
  document.addEventListener("keydown", handleKeyDown);
});

onUnmounted(() => {
  document.removeEventListener("keydown", handleKeyDown);
});

// Ref for the hidden file input
const fileInputRef = ref(null);

// Triggers the hidden file input
const triggerFileInput = () => {
  fileInputRef.value?.click();
};

// Handles the selected file
const handleFileSelected = (event) => {
  const file = event.target.files[0];
  if (file) {
    console.log("Selected file:", file.name);
    // Here you would typically handle the file (e.g., upload, display preview)
    // For now, we just log it.
    // Reset the input value so the same file can be selected again if needed
    if (fileInputRef.value) {
      fileInputRef.value.value = "";
    }
  }
};

const startNewChartSession = () => {
  // Implementation of startNewChartSession
};

const addToChatHandler = (chart) => {
  // Placeholder for future "Add to chat" functionality
  console.log("Add to chat clicked for chart:", chart.title);
  // Prevent openChat from being called if needed, though @click.stop should handle it
};

function viewCodeClick() {
  const el = document.getElementById("codeblock");
  if (el) {
    el.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

// Add deleteChart function
const confirmDelete = (chart) => {
  chartToDelete.value = chart;
  showDeleteConfirmDialog.value = true;
};

const deleteChart = async () => {
  if (!chartToDelete.value) return;
  chartDeleteLoading.value = true;
  
  try {
    const res = await fetch(`${API_URL}/api/files/${organization.value.id}/${chartToDelete.value.id}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${session.value.id}`,
        is_chart: true,
      },
    });
    if (!res.ok) throw new Error("Failed to delete chart");
    await getCharts(); // Refresh the charts list
  } catch (err) {
    console.error("Error deleting chart:", err);
  } finally {
    showDeleteConfirmDialog.value = false;
    chartToDelete.value = null;
    chartDeleteLoading.value = false;
  }
};
</script>

<template>
      <div class="search-container">
      <div class="search-box">
        <InputGroup>
          <InputText v-model="searchTerm" placeholder="Search charts..." />
          <Button icon="pi pi-search" @click="openDialog" />
        </InputGroup>
      </div>
    </div>

  <div v-if="loadingCharts" class="loading-div">
    <ProgressSpinner
      style="width: 40px; height: 40px"
      strokeWidth="3"
      fill="transparent"
      animationDuration=".5s"
      aria-label="Custom ProgressSpinner"
    />
    <p class="loading-chats-label">Loading Charts...</p>
  </div>

  <div class="chart-page" v-if="!loadingCharts">
    <!-- Header bar with search and create -->

    <div v-if="filteredCharts.length === 0 && !loadingCharts">
      <center>
        <div class="no-charts">
          <img
            src="../assets/undraw_segmentation.svg"
            alt="No charts"
            class="no-charts-img"
          />
          <h1 class="no-charts-title">No charts found</h1>
          <p class="no-charts-subtitle">
            Navigate to a sheet and open the AI Assitant window and ask it to
            make a chart for you
          </p>
        </div>
      </center>
    </div>

    <!-- Charts grid: 4 per row -->
    <div class="chart-grid">
      <template v-if="filteredCharts.length">
        <div
          v-for="chart in filteredCharts"
          :key="chart.id"
          class="chart-card"
          @click="openChat(chart)"
        >
          <div class="add-to-chat-btn">
            <Button
              icon="pi pi-sparkles"
              label="Ask AI"
              class="p-button-sm p-button-text ask-ai-btn"
              iconPos="right"
              v-tooltip.top="'Add to chat'"
              @click.stop="addToChatHandler(chart)"
            />
          </div>

          <h3>{{ chart["chart_name"] }}</h3>
          <div class="chart-container-placeholder">
            <img :src="chart['file_url']" alt="Chart image" class="chart-img" />
          </div>
          <div class="delete-btn">
            <Button
              icon="pi pi-trash"
              class="p-button-danger p-button-sm p-button-text"
              v-tooltip.top="'Delete chart'"
              @click.stop="confirmDelete(chart)"
            />
          </div>
        </div>
      </template>
    </div>

    <Dialog
      v-model:visible="showDetailDialog"
      modal
      :style="{ width: 'fit-content', height: '90vh', borderRadius: '12px' }"
      :draggable="false"
      :resizable="false"
      class="detail-dialog"
    >
      <template #header>
        <div class="d-flex items-center justify-center gap-2">
          <span class="font-bold" style="font-weight: bold">{{
            selectedChart ? selectedChart["chart_name"] : "Loading"
          }}</span>
          <Button variant="outlined" @click="viewCodeClick">View Code</Button>
        </div>
      </template>
      <img
        :src="selectedChart['file_url']"
        alt="Chart expanded"
        class="expanded-chart"
      />
      <p>Here's the R code used to make this chart</p>
      <div id="codeblock">
        <CodeBlock
          :code="selectedChart ? selectedChart['r_code'] : 'loading...'"
          :numbered="true"
          :show-header="true"
          file-name="chart.R"
          language="c"
          theme="vsDark"
          style="font-size: 12px"
          class="code-block"
        >
        </CodeBlock>
      </div>

      <!-- <div class="detail-container">
        <div class="chart-display">
          <div class="chart-display-wrapper" v-if="selectedChart">
            <ChartContainer
              :title="selectedChart.title"
              :loading="!selectedChart.dataSources"
              @elementClick="handleChartElementClick"
              :highlightedPoint="selectedChartPoint"
              class="detail-chart-instance"
            />
          </div>
        </div>
        <div class="chat-sidebar" :class="{ collapsed: !isSidebarPinned }">
          <div v-if="isSidebarPinned" class="chat-window" ref="chatWindowRef">
            <div
              v-for="msg in messages[selectedChart?.id]"
              :key="msg.id"
              class="message-container"
              :class="msg.sender"
            >
              <Avatar
                v-if="msg.sender === 'ai'"
                icon="pi pi-robot"
                class="message-avatar ai-avatar"
                size="small"
              />
              <div class="message-content">
                <div class="chat-bubble" :class="msg.sender">
                  {{ msg.text }}
                  <div v-if="msg.context" class="message-context">
                    <small
                      >📊 {{ msg.context.label }}:
                      {{ msg.context.value }}</small
                    >
                  </div>
                </div>
                <div class="message-timestamp">{{ msg.timestamp }}</div>
              </div>
              <Avatar
                v-if="msg.sender === 'user'"
                icon="pi pi-user"
                class="message-avatar user-avatar"
                size="small"
              />
            </div>
            <div v-if="isAiTyping" class="message-container ai">
              <Avatar
                icon="pi pi-robot"
                class="message-avatar ai-avatar"
                size="small"
              />
              <div class="message-content">
                <div class="chat-bubble ai typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>
          <div class="advanced-chat-input-area">
            <div v-if="showSuggestedQuestions" class="suggested-questions-bar">
              <Button
                v-for="question in suggestedQuestions"
                :key="question"
                :label="question"
                class="p-button-sm p-button-outlined suggested-question-chip"
                @click="useSuggestedQuestion(question)"
              />
            </div>
            <div class="main-input-row">
              <input
                type="file"
                ref="fileInputRef"
                @change="handleFileSelected"
                style="display: none"
              />
              <Button
                icon="pi pi-paperclip"
                class="p-button-text p-button-sm"
                v-tooltip.top="'Attach file'"
                @click="triggerFileInput"
              />
              <Button
                icon="pi pi-question-circle"
                class="p-button-text p-button-sm"
                @click="showSuggestedQuestions = !showSuggestedQuestions"
                v-tooltip.top="
                  showSuggestedQuestions
                    ? 'Hide suggestions'
                    : 'Show suggestions'
                "
              />
              <InputText
                v-model="chatInput"
                :placeholder="`Ask about ${
                  selectedChart?.title || 'the chart'
                }...`"
                class="p-inputtext-lg chat-input-field"
                @keydown.ctrl.enter="sendMessage"
                @keydown.meta.enter="sendMessage"
              />
              <Button
                icon="pi pi-send"
                class="p-button-text p-button-lg"
                @click="sendMessage"
                :disabled="!chatInput.trim() || isAiTyping"
                v-tooltip.top="'Send message'"
              />
            </div>
            <div class="bottom-toolbar">
              <span class="spacer"></span>
            </div>
          </div>
        </div>
      </div> -->
    </Dialog>

    <!-- Add Delete Confirmation Dialog -->
    <Dialog
      v-model:visible="showDeleteConfirmDialog"
      modal
      :style="{ width: '30rem' }"
      :draggable="false"
      :resizable="false"
      class="delete-confirm-dialog"
    >
      <template #header>
        <div class="flex align-items-center gap-2">
          <i class="pi pi-exclamation-triangle text-yellow-500" style="font-size: 1.5rem"></i>
          <span class="font-bold">Confirm Deletion</span>
        </div>
      </template>
      <div class="confirmation-content">
        <div class="warning-icon">
          <i class="pi pi-exclamation-circle"></i>
        </div>
        <h3>Delete Chart</h3>
        <p>Are you sure you want to delete this chart? This action cannot be undone.</p>
      </div>
      <template #footer>
        <div class="flex justify-content-end gap-3">
          <Button
            label="Cancel"
            icon="pi pi-times"
            class="p-button-text p-button-rounded"
            @click="showDeleteConfirmDialog = false"
          />
          <Button
            label="Delete"
            icon="pi pi-trash"
            :loading="chartDeleteLoading"
            class="p-button-danger p-button-rounded"
            @click="deleteChart"
          />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<style scoped>
.chart-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
.code-block {
  width: 40vw;
}
.expanded-chart {
  width: 39vw;
}
.no-charts-img {
  margin-top: 20vh;
  width: 12rem;
}

.no-charts-title {
  font-size: 30px;
  margin-top: 1rem;
}

.no-charts-subtitle {
  color: gray;
  width: 30%;
}

.search-box {
  width: 20vw;
}
.loading-div {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  margin-left: auto;
  margin-right: auto;
  overflow-x: auto;
  overflow-y: auto;
  justify-content: center;
  align-items: center;
  margin-top: 15%;
}

.loading-chats-label {
  margin-top: 0.5rem;
  color: gray;
  font-size: 12px;
  text-align: center;
}

.chart-page {
  padding: 2rem;
  position: relative;
  min-height: 100vh;
}

.search-container {
  position: sticky;
  top: 0;
  z-index: 10;
  background-color: var(--surface-ground);
  padding: 1rem 0;
  margin-bottom: 1rem;
  border-bottom: 1px solid var(--surface-border);
}

.search-box {
  width: 20vw;
  margin-left: auto;
}

.chart-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-top: 1rem;
  width: 100%;
  padding-bottom: 3rem; /* Add padding to ensure last row has space */
}

.chart-dialog .p-dialog-header {
  background: var(--green-500, #4caf50);
  color: var(--primary-color-text, #ffffff);
  padding: 1rem 1.5rem;
  font-size: 1.15rem;
  font-weight: 600;
  border-bottom: 1px solid var(--green-600, #388e3c);
  text-align: center;
}
.chart-dialog .p-dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}
.chart-dialog .p-dialog-content {
  background: var(--surface-ground);
  padding: 1.5rem;
  font-size: 1rem;
}
.data-field label {
  font-size: 0.9rem;
  color: var(--text-color-secondary);
  display: block;
  margin-bottom: 0.65rem;
  font-weight: 500;
}
.chat-dialog-content {
  max-width: 500px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}
.chat-prompt p {
  color: var(--text-color);
  padding: 0.25rem 1.25rem 0.25rem 1.25rem;
  font-size: 1.2rem;
  font-weight: 600;
  font-family: "Poppins", sans-serif;
  text-align: center;
  margin: 0 auto 0.75rem auto;
}
.chat-input-area textarea.chat-input {
  width: 100%;
  min-height: 80px;
  border-radius: 8px;
  padding: 0.85rem 1rem;
  font-size: 1rem;
  border: 1px solid var(--surface-border, #ced4da);
  background-color: var(--surface-card, #ffffff);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  color: var(--text-color);
}
.chat-input-area textarea.chat-input:focus {
  border-color: var(--primary-color, #007bff);
  box-shadow: 0 0 0 0.2rem
    var(--primary-color-transparent, rgba(0, 123, 255, 0.25));
  outline: none;
}
.data-field {
  width: 100%;
  margin: 0 auto;
}
.data-source-select {
  width: 100%;
  font-size: 0.95rem;
}
.create-btn {
  width: 3rem;
  height: 3rem;
  border-radius: 0.5rem !important;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

/* Enhanced dialog UI */
.chart-dialog .p-dialog {
  border-radius: 12px !important;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1), 0 6px 15px rgba(0, 0, 0, 0.08);
}

.chat-prompt p {
  font-size: 1.5rem;
  font-weight: 700;
  font-family: "Poppins", sans-serif;
}

.chat-input-area textarea.chat-input {
  border: 1px solid var(--surface-d);
}

.chat-sidebar {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--surface-card);
  border-radius: 8px;
  overflow: hidden;
  transition: width 0.3s ease, flex-basis 0.3s ease;
  position: relative;
  flex-shrink: 0;
}
.chat-sidebar:not(.collapsed) {
  border-left: 1px solid var(--surface-border);
}
.chat-sidebar.collapsed {
  width: 50px !important;
}
.resize-handle {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 6px;
  cursor: ew-resize;
  background: transparent;
  transition: background 0.2s;
}
.resize-handle:hover {
  background: var(--primary-color);
  opacity: 0.3;
}
.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--surface-border);
}
.sidebar-header h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-grow: 1;
}
.sidebar-controls {
  display: flex;
  gap: 0.5rem;
}

.chat-window {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  min-height: 0;
}
.message-container {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}
.message-container.user {
  flex-direction: row-reverse;
}
.message-container.system {
  justify-content: center;
}
.message-avatar {
  flex-shrink: 0;
}
.ai-avatar {
  background: var(--primary-color);
}
.user-avatar {
  background: var(--green-500);
}
.message-content {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  max-width: 80%;
}
.chat-bubble {
  background: var(--surface-card);
  padding: 0.75rem;
  border-radius: 0.75rem;
  max-width: 80%;
}
.chat-bubble.ai {
  background: var(--surface-ground);
  border: 1px solid var(--surface-border);
  border-radius: 1rem 1rem 1rem 0.25rem;
}
.chat-bubble.user {
  background: #f0f0f0; /* Light grey background */
  color: #333333; /* Dark grey/black text */
  border-radius: 1rem 1rem 0.25rem 1rem;
}
.chat-bubble.system {
  background: var(--surface-100);
  font-style: italic;
  font-size: 0.9rem;
}
.message-timestamp {
  font-size: 0.75rem;
  color: var(--text-color-secondary);
  padding: 0 0.5rem;
}
.message-container.user .message-timestamp {
  text-align: right;
}
.message-context {
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid var(--surface-border);
}

/* Typing Indicator */
.typing-indicator {
  display: flex;
  gap: 0.3rem;
  padding: 0.75rem 1rem;
}
.typing-indicator span {
  width: 8px;
  height: 8px;
  background: var(--text-color-secondary);
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}
.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}
.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}
@keyframes typing {
  0%,
  80%,
  100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.chat-input-container {
  display: flex;
  gap: 0.5rem;
  padding: 1rem;
  border-top: 1px solid var(--surface-border);
  display: flex;
  flex-direction: column;
}
.suggested-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}
.suggested-question {
  background: var(--surface-100);
  padding: 0.5rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.2s;
}
.suggested-question:hover {
  background: var(--surface-200);
}
.input-row {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}
.chart-card {
  cursor: pointer;
  background-color: var(--surface-card);
  border-radius: 12px;
  padding: 1.5rem;
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  aspect-ratio: 1 / 1;
  position: relative;
  width: 100%;
  height: auto;
}
.chart-card h3 {
  font-family: "Poppins", sans-serif;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.75rem 0;
  line-height: 1.3;
}
.chart-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}
.chart-container-placeholder {
  border-radius: 8px;
  margin-top: 1rem;
  width: 100%;
  height: calc(100% - 3rem);
  display: flex;
  align-items: center;
  justify-content: center;
}

.detail-container {
  display: flex;
  width: 100%;
  height: 100%;
  gap: 0.75rem;
  flex-direction: row;
}
.detail-container .chart-display {
  flex: 3;
  min-width: 0;
  display: flex;
  flex-direction: column;
  background-color: var(--surface-section, var(--surface-ground));
  padding: 1.5rem;
  border-radius: 8px;
  overflow-y: auto;
}
.detail-container .chat-sidebar {
  flex: 1;
  min-width: 450px;
  max-width: 450px;
  border-left: 1px solid var(--surface-border);
  height: 100%;
}

/* Scrollbar Styling */
.chat-window::-webkit-scrollbar {
  width: 6px;
}
.chat-window::-webkit-scrollbar-track {
  background: transparent;
}
.chat-window::-webkit-scrollbar-thumb {
  background: var(--surface-border);
  border-radius: 3px;
}
.chat-window::-webkit-scrollbar-thumb:hover {
  background: var(--text-color-secondary);
}

.chat-sidebar:not(.collapsed) {
  /* border-left removed, handled by .detail-container .chat-sidebar */
}

.chat-sidebar.collapsed {
  flex-grow: 0;
  flex-shrink: 1;
  height: 60px;
  overflow: hidden;
}

.chat-sidebar.collapsed .sidebar-header h3,
.chat-sidebar.collapsed .chat-window,
.chat-sidebar.collapsed .suggested-questions {
  display: none;
}

.chat-sidebar.collapsed .chat-input-container {
  border-top: none;
}

.chart-display-wrapper {
  width: min(max(576px, 67vw), 864px);
  height: min(max(576px, 67vw), 864px);
  aspect-ratio: 1 / 1;
  margin: 0 auto 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
}

.detail-chart-instance {
  width: 100%;
  height: 100%;
}

.detail-chart-instance .chart-title-slot-class {
  /* Assuming ChartContainer uses a class for its title slot */
  display: none; /* Hide built-in title if sidebar header is sufficient */
}

/* New Advanced Chat Input Area */
.advanced-chat-input-area {
  padding: 0.5rem 1rem 0.25rem 1rem;
  border-top: 1px solid var(--surface-border);
  background-color: var(--surface-ground); /* Subtle background distinction */
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.main-input-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.main-input-row .chat-input-field {
  flex: 1;
  /* Assuming p-inputtext-lg provides good padding, or add specific padding here */
}

.suggested-questions-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding-bottom: 0.5rem; /* Space below suggestions if they are shown */
  border-bottom: 1px solid var(--surface-border); /* Separator */
}

.suggested-question-chip {
  font-size: 0.8rem !important;
}

.bottom-toolbar {
  display: flex;
  align-items: center;
  gap: 0.25rem; /* Smaller gap for toolbar items */
}

.bottom-toolbar .p-button-sm {
  font-size: 0.85rem !important;
}

.bottom-toolbar .spacer {
  flex-grow: 1;
}

.chat-sidebar.collapsed .advanced-chat-input-area {
  display: none; /* Hide the entire new input area when collapsed */
}

.add-to-chat-btn {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  z-index: 1;
}

.delete-btn {
  position: absolute;
  bottom: 1rem;
  right: 1rem;
  z-index: 1;
}

.delete-btn .p-button {
  opacity: 0.7;
  transition: opacity 0.2s ease;
}

.delete-btn .p-button:hover {
  opacity: 1;
}

.delete-confirm-dialog :deep(.p-dialog-header) {
  padding: 1.5rem;
  border-bottom: 1px solid var(--surface-border);
  background: var(--surface-ground);
}

.delete-confirm-dialog :deep(.p-dialog-content) {
  padding: 0;
}

.confirmation-content {
  padding: 2rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.confirmation-content .warning-icon {
  width: 4rem;
  height: 4rem;
  border-radius: 50%;
  background: var(--yellow-100);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.5rem;
}

.confirmation-content .warning-icon i {
  font-size: 2rem;
  color: var(--yellow-500);
}

.confirmation-content h3 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-color);
}

.confirmation-content p {
  margin: 0;
  line-height: 1.5;
  color: var(--text-color-secondary);
  font-size: 1rem;
}

.delete-confirm-dialog :deep(.p-dialog-footer) {
  padding: 1.5rem;
  border-top: 1px solid var(--surface-border);
  background: var(--surface-ground);
}

.delete-confirm-dialog :deep(.p-button) {
  min-width: 6rem;
  font-weight: 500;
}

.delete-confirm-dialog :deep(.p-button.p-button-danger) {
  background: var(--red-500);
  border-color: var(--red-500);
}

.delete-confirm-dialog :deep(.p-button.p-button-danger:hover) {
  background: var(--red-600);
  border-color: var(--red-600);
}

.delete-confirm-dialog :deep(.p-button.p-button-text) {
  color: var(--text-color-secondary);
}

.delete-confirm-dialog :deep(.p-button.p-button-text:hover) {
  background: var(--surface-hover);
  color: var(--text-color);
}
</style>

<!-- Global styles for dialog mask blur - using non-scoped style -->
<style>
/* Target PrimeVue dialog mask globally */
.p-dialog-mask {
  background-color: rgba(0, 0, 0, 0.4) !important;
  backdrop-filter: blur(8px) !important;
  -webkit-backdrop-filter: blur(8px) !important;
}

/* Alternative approach if the above doesn't work */
.p-component-overlay {
  background-color: rgba(0, 0, 0, 0.4) !important;
  backdrop-filter: blur(8px) !important;
  -webkit-backdrop-filter: blur(8px) !important;
}

/* Ensure proper stacking context */
.p-dialog-mask.p-component-overlay {
  z-index: 1100;
}

.p-dialog {
  z-index: 1101;
}
</style>
