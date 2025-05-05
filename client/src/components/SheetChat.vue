<template>
  <div class="sheet-chat" :style="{ width: chatWidth + 'px' }">
    <!-- Header -->
    <header class="chat-header">
      <h3>How can I assist you?</h3>
      <button class="close-btn" @click="close">×</button>
    </header>

    <!-- suggestion buttons -->
    <div class="suggestions">
      <button
        v-for="(s, i) in suggestions"
        :key="i"
        class="suggestion"
        @click="applySuggestion(s)"
      >
        {{ s }}
      </button>
    </div>

    <!-- messages (plain text, no boxes) -->
    <div class="messages" ref="msgsContainer">
      <p
        v-for="(msg, idx) in messages"
        :key="idx"
        :class="['message', msg.from]"
      >
        {{ msg.text }}
      </p>
    </div>

    <!-- input bar -->
    <div class="input-bar">
      <input
        v-model="draft"
        @keyup.enter="send"
        placeholder="Send a message…"
      />
      <button class="send-btn" @click="send">Send</button>
    </div>

    <!-- Resizable handle -->
    <div
      class="resize-handle"
      :class="{ active: isResizing }"
      @mousedown="startResize"
    >
      <div class="resize-icon">⋮⋮⋮</div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick, onMounted, onBeforeUnmount } from 'vue'
const emit = defineEmits(['close'])

// hard‑coded suggestion list
const suggestions = [
  'Create a new column',
  'Create a new row',
  'Perform research',
  'What else can you do?'
]

// chat state
const messages = reactive([])
const draft = ref('')
const msgsContainer = ref(null)
const chatWidth = ref(380) // Initial width in pixels
const isResizing = ref(false)
const minWidth = 200 // Minimum width in pixels

function scrollToBottom() {
  nextTick(() => {
    const el = msgsContainer.value
    if (el) el.scrollTop = el.scrollHeight
  })
}

function applySuggestion(text) {
  messages.push({ from: 'user', text })
  scrollToBottom()
  setTimeout(() => {
    messages.push({
      from: 'assistant',
      text: `🛠 Here's a response for: " ${text} "`
    })
    scrollToBottom()
  }, 500)
}

function send() {
  const txt = draft.value.trim()
  if (!txt) return
  applySuggestion(txt)
  draft.value = ''
}

function close() {
  emit('close')
}

let startX, startWidth

function startResize(event) {
  startX = event.clientX
  startWidth = chatWidth.value
  isResizing.value = true
  document.documentElement.addEventListener('mousemove', doResize)
  document.documentElement.addEventListener('mouseup', stopResize)
}

function doResize(event) {
  const newWidth = startWidth + (event.clientX - startX)
  chatWidth.value = Math.max(newWidth, minWidth) // Ensure minimum width
}

function stopResize() {
  isResizing.value = false
  document.documentElement.removeEventListener('mousemove', doResize)
  document.documentElement.removeEventListener('mouseup', stopResize)
}

onMounted(() => {
  // Any additional setup if needed
})

onBeforeUnmount(() => {
  // Clean up event listeners if needed
  document.documentElement.removeEventListener('mousemove', doResize)
  document.documentElement.removeEventListener('mouseup', stopResize)
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

.sheet-chat {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #ffffff;
  font-family: 'Inter', sans-serif;
  z-index: 1000;
  position: relative;
  border: 1px solid #e0e0e0; /* Light grey border */
  box-shadow: none !important; /* Ensure no shadow */
}

/* header with title + close */
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  border-bottom: 1px solid #e0e0e0;
}
.chat-header h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 500;
  color: #333;
}
.close-btn {
  background: none;
  border: none;
  font-size: 1.4rem;
  cursor: pointer;
  color: #666;
}

/* suggestions row */
.suggestions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e0e0e0;
}
.suggestion {
  width: 100%;
  padding: 0.6rem;
  background: #f9f9f9;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 0.95rem;
  color: #333;
  text-align: center;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
}
.suggestion:hover {
  background: #fff;
  border-color: #ccc;
}

/* messages (plain text) */
.messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}
.message {
  margin: 0.4rem 0;
  line-height: 1.4;
  font-size: 0.95rem;
}
.message.user {
  text-align: right;
  color: #3f51b5;
}
.message.assistant {
  text-align: left;
  color: #333;
}

/* input bar pinned at bottom */
.input-bar {
  display: flex;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-top: 1px solid #e0e0e0;
}
.input-bar input {
  flex: 1;
  padding: 0.6rem 1rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.95rem;
  outline: none;
  transition: border-color 0.2s;
}
.input-bar input:focus {
  border-color: #3f51b5;
}
.send-btn {
  padding: 0 1rem;
  background: #000000;
  border: none;
  border-radius: 6px;
  color: #fff;
  cursor: pointer;
  transition: background 0.2s;
}
.send-btn:hover {
  background: #35449c;
}

/* Resizable handle */
.resize-handle {
  width: 20px;
  height: 100%; /* Full height of the chat */
  cursor: ew-resize;
  position: absolute;
  top: 0;
  right: -10px;
  transition: background-color 0.2s;
}
.resize-handle.active {
  background-color: transparent;
  border-right: 2px solid #3f51b5; /* Darker blue border */
}
.resize-icon {
  font-size: 1.2rem;
  color: #666;
  text-align: center;
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
}
</style>
