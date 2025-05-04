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

    <!-- Charts grid: 2 per row -->
    <div class="chart-grid">
      <template v-if="filteredCharts.length">
        <div
          v-for="chart in filteredCharts"
          :key="chart.id"
          class="chart-card"
          @click="openChat(chart)"
        >
          <ChartContainer
            :title="chart.title"
            :loading="!chart.dataSources"
          />
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
      :style="{ width: '70vw', height: '70vh' }"
      :draggable="false"
      :resizable="false"
      class="detail-dialog"
    >
      <div class="detail-container">
        <div class="chart-display">
          <ChartContainer
            v-if="selectedChart"
            :title="selectedChart.title"
            :loading="!selectedChart.dataSources"
            @elementClick="handleChartElementClick"
            :highlightedPoint="selectedChartPoint"
          />
        </div>
        <div 
          class="chat-sidebar" 
          :style="{ width: isSidebarPinned ? sidebarWidth + 'px' : '50px', flex: isSidebarPinned ? 1 : 'none' }"
          :class="{ 'collapsed': !isSidebarPinned }"
        >
          <!-- Resize handle -->
          <div 
            v-if="isSidebarPinned"
            class="resize-handle" 
            @mousedown="startResize"
          ></div>
          
          <!-- Sidebar Header -->
          <div class="sidebar-header">
            <h3 v-if="isSidebarPinned">Chat with {{ selectedChart?.title }}</h3>
            <div class="sidebar-controls">
              <Button 
                v-if="isSidebarPinned"
                icon="pi pi-trash" 
                class="p-button-text p-button-sm"
                @click="clearConversation"
                v-tooltip="'Clear conversation'"
              />
              <Button 
                :icon="isSidebarPinned ? 'pi pi-angle-double-right' : 'pi pi-comments'" 
                class="p-button-text p-button-sm"
                @click="toggleSidebarPin"
                v-tooltip="isSidebarPinned ? 'Collapse sidebar' : 'Expand sidebar'"
              />
            </div>
          </div>
          
          <!-- Chat Window -->
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
          <div v-if="isSidebarPinned" class="chat-input-container">
            <!-- Suggested Questions -->
            <div v-if="showSuggestedQuestions" class="suggested-questions">
              <div 
                v-for="question in suggestedQuestions" 
                :key="question"
                class="suggested-question"
                @click="useSuggestedQuestion(question)"
              >
                {{ question }}
              </div>
            </div>
            
            <div class="input-row">
              <Button 
                icon="pi pi-question-circle" 
                class="p-button-text p-button-sm"
                @click="showSuggestedQuestions = !showSuggestedQuestions"
                v-tooltip="'Suggested questions'"
              />
              <InputText
                v-model="chatInput"
                placeholder="Type a message"
                class="p-inputtext chat-input-field"
                style="flex:1"
                @keydown.ctrl.enter="sendMessage"
                @keydown.meta.enter="sendMessage"
              />
              <Button
                icon="pi pi-send"
                class="p-button-text"
                @click="sendMessage"
                :disabled="!chatInput.trim() || isAiTyping"
              />
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
  font-size: 1.5rem;
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
  font-size: 1rem;
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
  padding: 1rem 1.25rem;
  font-size: 1.5rem;
  font-weight: 700;
  font-family: 'Poppins', sans-serif;
  text-align: center;
  margin: 0 auto;
}
.chat-input-area textarea.chat-input {
  width: 100%;
  min-height: 80px;
  border-radius: 0.75rem;
  padding: 0.75rem;
  font-size: 1rem;
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
  border-radius: 0.75rem !important;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.chart-dialog .p-dialog-header {
  background: var(--success-color);
  color: #fff;
  padding: 1rem 1.5rem;
  font-size: 1.25rem;
}

.chart-dialog .p-dialog-content {
  background: var(--surface-ground);
  padding: 1.5rem;
}

.chart-dialog .p-dialog-footer {
  background: var(--surface-ground);
  padding: 0.75rem 1.5rem;
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
  transition: width 0.3s ease;
  position: relative;
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
  font-size: 1.2rem;
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
  gap: 0.5rem;
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
  background: var(--primary-color);
  color: black;
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
}
.detail-dialog .p-dialog-content {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  height: 100%;
}
.detail-container {
  display: flex;
  width: 100%;
  height: 100%;
}
.detail-container .chart-display {
  flex: 3;
  margin-right: 1rem;
}
.detail-container .chat-sidebar {
  flex: 1;
  display: flex;
  flex-direction: column;
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