<script setup>
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import MultiSelect from 'primevue/multiselect';
import ChartContainer from '@/components/ui/charts/ChartContainer.vue';
import Textarea from 'primevue/textarea';
import Avatar from 'primevue/avatar';
import ProgressSpinner from 'primevue/progressspinner';
import Dropdown from 'primevue/dropdown';
import Divider from 'primevue/divider';
import Tooltip from 'primevue/tooltip';

// State
const searchTerm = ref('');
const showDialog = ref(false);
const promptText = ref('');
const selectedDataSources = ref([]);
const dataSourceOptions = [
  'Data Source 1',
  'Data Source 2',
  'Data Source 3',
  'Data Source 4',
  'Data Source 5',
  'Data Source 6',
  'Data Source 7',
  'Data Source 8',
  'Data Source 9',
  'Data Source 10'
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

const selectedChart = ref(null);
const chatInput = ref('');
const messages = ref({});
const isAiTyping = ref(false);
const chatWindowRef = ref(null);
const sidebarWidth = ref(400);
const isSidebarPinned = ref(true);
const showSuggestedQuestions = ref(false);
const selectedChartPoint = ref(null);

// Suggested questions
const suggestedQuestions = [
  "What's the highest data point?",
  "Explain this trend",
  "What are the key insights?",
  "Compare the minimum and maximum values",
  "What patterns do you see in the data?",
  "Show me year-over-year growth"
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
      sender: 'user',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    
    messages.value[selectedChart.value.id].push(userMessage);
    chatInput.value = '';
    
    // Auto-scroll to bottom
    nextTick(() => {
      scrollToBottom();
    });
    
    // Simulate AI response
    isAiTyping.value = true;
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    const aiResponse = {
      id: Date.now() + 1,
      text: `I've analyzed your question about "${userMessage.text}". Based on the data in ${selectedChart.value.title}, here's what I found...`,
      sender: 'ai',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
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
  if (e.key === 'Enter' && chatInput.value) {
    e.preventDefault();
    sendMessage();
  }
  
  // Press "/" to focus chat input
  if (e.key === '/' && document.activeElement.tagName !== 'TEXTAREA') {
    e.preventDefault();
    const chatTextarea = document.querySelector('.chat-input-field');
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
    document.removeEventListener('mousemove', doDrag);
    document.removeEventListener('mouseup', stopDrag);
  };
  
  document.addEventListener('mousemove', doDrag);
  document.addEventListener('mouseup', stopDrag);
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
      sender: 'system',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      context: elementData
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
  document.addEventListener('keydown', handleKeyDown);
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown);
});

const showDetailDialog = ref(false);

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
    console.log('Selected file:', file.name);
    // Here you would typically handle the file (e.g., upload, display preview)
    // For now, we just log it.
    // Reset the input value so the same file can be selected again if needed
    if (fileInputRef.value) {
      fileInputRef.value.value = '';
    }
  }
};

const startNewChartSession = () => {
  // Implementation of startNewChartSession
};

const addToChatHandler = (chart) => {
  // Placeholder for future "Add to chat" functionality
  console.log('Add to chat clicked for chart:', chart.title);
  // Prevent openChat from being called if needed, though @click.stop should handle it
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
        class="p-button-lg create-btn"
        @click="openDialog"
        aria-label="Add Chart"
      />
    </div>

    <!-- Charts grid: 3 per row -->
    <div class="chart-grid">
      <template v-if="filteredCharts.length">
        <div
          v-for="chart in filteredCharts"
          :key="chart.id"
          class="chart-card"
          @click="openChat(chart)"
        >
          <Button 
            icon="pi pi-sparkles" 
            class="p-button-rounded p-button-sm p-button-text add-to-chat-btn" 
            v-tooltip.top="'Add to chat'"
            @click.stop="addToChatHandler(chart)" 
          />
          <h3>{{ chart.title }}</h3>
          <div class="chart-container-placeholder">
            <span>Chart Preview</span>
          </div>
          <!-- Original ChartContainer is commented out or removed for placeholder UI -->
          <!-- 
          <ChartContainer
            :title="chart.title" 
            :loading="!chart.dataSources" 
          />
          -->
        </div>
      </template>
      <div v-else class="no-results">
        No charts found.
      </div>
    </div>

    <!-- Generation dialog -->
    <Dialog
      v-model:visible="showDialog"
      modal
      :style="{ width: '35vw', height: '42vh' }"
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
            :selectAll="true"
            :filter="false"
            selectAllLabel="Apply all datasources"
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

    <Dialog
      v-model:visible="showDetailDialog"
      modal
      :style="{ width: '66vw', height: '90vh', borderRadius: '12px' }"
      :draggable="false"
      :resizable="false"
      class="detail-dialog"
    >
      <div class="detail-container">
        <div class="chart-display">
          <div class="chart-display-wrapper" v-if="selectedChart">
            <ChartContainer
              :title="selectedChart.title" 
              :loading="!selectedChart.dataSources"
              @elementClick="handleChartElementClick"
              :highlightedPoint="selectedChartPoint"
              class="detail-chart-instance" />
          </div>
        </div>
        <div 
          class="chat-sidebar"
          :class="{ 'collapsed': !isSidebarPinned }"
        >
          <!-- Sidebar Header removed -->
          <!-- Chat Window and Input remain below -->
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
                    <small>📊 {{ msg.context.label }}: {{ msg.context.value }}</small>
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
            <!-- AI Typing Indicator -->
            <div v-if="isAiTyping" class="message-container ai">
              <Avatar icon="pi pi-robot" class="message-avatar ai-avatar" size="small" />
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
                v-for="question in suggestedQuestions" :key="question"
                :label="question"
                class="p-button-sm p-button-outlined suggested-question-chip"
                @click="useSuggestedQuestion(question)"
              />
            </div>
            <div class="main-input-row">
              <input type="file" ref="fileInputRef" @change="handleFileSelected" style="display: none;" />
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
                v-tooltip.top="showSuggestedQuestions ? 'Hide suggestions' : 'Show suggestions'"
              />
              <InputText
                v-model="chatInput"
                :placeholder="`Ask about ${selectedChart?.title || 'the chart'}...`"
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
      </div>
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
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
}
.no-results {
  grid-column: 1 / -1;
  text-align: center;
  color: var(--text-color-secondary);
  padding: 2rem;
}
.chart-dialog .p-dialog-header {
  background: var(--green-500, #4CAF50);
  color: var(--primary-color-text, #ffffff);
  padding: 1rem 1.5rem;
  font-size: 1.15rem;
  font-weight: 600;
  border-bottom: 1px solid var(--green-600, #388E3C);
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
  font-family: 'Poppins', sans-serif;
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
  box-shadow: 0 0 0 0.2rem var(--primary-color-transparent, rgba(0,123,255,.25));
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
  font-family: 'Poppins', sans-serif;
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
  0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
  40% { transform: scale(1); opacity: 1; }
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
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;
  aspect-ratio: 1 / 1;
  position: relative;
}
.chart-card h3 {
  font-family: 'Poppins', sans-serif;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.75rem 0;
  line-height: 1.3;
}
.chart-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.1);
}
.chart-card .chart-container-placeholder {
  flex-grow: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--surface-ground);
  border-radius: 8px;
  margin-top: 1rem;
  color: var(--text-color-secondary);
  font-style: italic;
}
.detail-dialog .p-dialog-content {
  display: flex;
  gap: 1rem;
  padding: 1rem 1rem 0.5rem 1rem;
  height: 100%;
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

.detail-chart-instance .chart-title-slot-class { /* Assuming ChartContainer uses a class for its title slot */
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