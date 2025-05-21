<template>
  <div class="sheet-chat" :style="{ width: chatWidth + 'px' }">
    <!-- Header -->
    <header class="chat-header">
      <div class="d-flex justify-content-between">
        <h3>How can I assist you?</h3>
        <div class="d-flex">
          <button class="expand-btn" @click="fullscreenToggle">
            <i
              :class="
                'pi ' +
                (fullscreen ? 'pi-window-minimize' : 'pi-window-maximize')
              "
            ></i>
          </button>
          <button class="close-btn" @click="close">×</button>
        </div>
      </div>

      <div class="d-flex">
        <span class="context-badge">
          Using Context:
          <i
            v-if="props.contextType === 'sheets'"
            class="pi pi-table sheet-icon"
          ></i>
          <img
            :src="orgImgUrl"
            v-if="props.contextType !== 'sheets'"
            class="org-img"
          />
          <p v-if="props.contextType !== 'sheets'">{{ orgName }}</p>
          <p v-if="props.contextType === 'sheets'">{{ props.contextName }}</p>
        </span>
      </div>
    </header>

    <!-- suggestion buttons -->
    <div class="suggestions" v-if="messages.length === 0 && !loadingChats">
      <button
        v-for="(s, i) in suggestions"
        :key="i"
        class="suggestion"
        @click="displayText(s)"
      >
        {{ s }}
      </button>
    </div>

    <!-- messages (plain text, no boxes) -->
    <div class="messages" ref="msgsContainer" v-if="!loadingChats">
      <div
        v-for="(msg, idx) in messages"
        :key="idx"
        :class="['message', msg.from]"
      >
        <p class="timestamp">{{ msg.timestamp }}</p>
        <p v-if="msg.type === 'message'">{{ msg.text }}</p>
        <div v-if="msg.type === 'skeleton-text'">
          <Skeleton width="80%" class="mb-2"></Skeleton>
          <Skeleton width="80%" class="mb-2"></Skeleton>
          <Skeleton width="80%" class="mb-2"></Skeleton>
        </div>
        <div v-if="msg.type === 'skeleton-img'">
          <Skeleton width="80%" height="5rem"></Skeleton>
        </div>

        <img :src="msg.text" v-if="msg.type === 'image'" class="img" />

        <div
          v-if="
            msg.from === 'assistant' &&
            msg.type !== 'skeleton-text' &&
            msg.type !== 'image'
          "
          class="generatedTime"
        >
          <div v-if="msg.type === 'code'">
            <p>Here's the R code used to make this chart</p>
            <CodeBlock
              :code="msg.text"
              :numbered="true"
              :show-header="true"
              file-name="chart.R"
              language="c"
              theme="vsDark"
              style="font-size: 12px"
            >
            </CodeBlock>
          </div>

          <div v-if="msg.type === 'data_table'">
            <DataTable :value="msg.text['data']">
              <Column
                v-for="col of msg.text['headers']"
                :field="col"
                :header="col"
              ></Column>
            </DataTable>
          </div>

          <div v-if="msg.type === 'action'">
            <p>Click the button to apply the action</p>
            <Button icon="pi pi-check" :label="JSON.parse(msg.text)['description']" class="action-btn" icon-pos="right" @click="() => applyAction(JSON.parse(msg.text))"/>
          </div>
          <i class="pi pi-sparkles"></i> Generated in {{ msg.generationTime }}s
        </div>
      </div>
    </div>

    <center v-if="!loadingChats">
      <div class="input-bar">
        <input
          v-model="draft"
          @keyup.enter="send"
          placeholder="Send a message…"
        />
        <Button
          class="send-btn"
          @click="send"
          icon="pi pi-arrow-up"
          :loading="loading"
        >
        </Button>
      </div>
    </center>

    <div v-if="loadingChats" class="loading-div">
      <ProgressSpinner
        style="width: 40px; height: 40px"
        strokeWidth="3"
        fill="transparent"
        animationDuration=".5s"
        aria-label="Custom ProgressSpinner"
      />
      <p class="loading-chats-label">Loading Chats</p>
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
import {
  ref,
  reactive,
  nextTick,
  onMounted,
  onBeforeUnmount,
  unref,
} from "vue";
import Skeleton from "primevue/skeleton";
import { useSession, useOrganization } from "@clerk/vue";
import Button from "primevue/button";
import { CodeBlock } from "vuejs-code-block";
import { ProgressSpinner } from "primevue";
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import ColumnGroup from 'primevue/columngroup';   // optional
import Row from 'primevue/row';                   // optional

const { organization } = useOrganization();
const emit = defineEmits(["close"]);
const { session } = useSession();
const orgImgUrl = ref("");
const orgName = ref("");
const fullscreen = ref(false);
const loading = ref(false);
const loadingChats = ref(true);

const props = defineProps({
  contextType: {
    type: String,
    default: null,
  },
  contextName: {
    type: String,
    default: null,
  },
  sheetId: {
    type: String,
    default: null,
  },
  selectedCells: {
    type: Map,
    default: {}
  },
  action: {
    type: Function
  }
});

onMounted(async () => {
  console.log(session.value.id);
  console.log(props.sheetId);

  console.log(session.value.user.id);
  orgImgUrl.value = organization.value.imageUrl;
  orgName.value = organization.value.name;
  // initial load
  await loadChats(1, false);

  scrollToBottom();
  // attach listener
  const el = msgsContainer.value;
  if (el) el.addEventListener("scroll", onScroll);
});

onBeforeUnmount(() => {
  const el = msgsContainer.value;
  if (el) el.removeEventListener("scroll", onScroll);
});

const API_URL = import.meta.env.VITE_API_URL;

// hard‑coded suggestion list
const suggestions = [
  "Create a new column",
  "Create a new row",
  "Perform research",
  "Create a chart",
  "What else can you do?",
];

// chat state
const messages = reactive([]);
const draft = ref("");
const msgsContainer = ref(null);
const chatWidth = ref(400); // Initial width in pixels
const isResizing = ref(false);
const minWidth = 400; // Minimum width in pixels
const currentPage = ref(1);
const PAGE_SIZE = 6;
const noMoreChats = ref(false);

function formatDateMMDDhhmm(dateInput = new Date()) {
  const d = new Date(dateInput);

  // Month and day
  const MM = String(d.getMonth() + 1).padStart(2, "0");
  const DD = String(d.getDate()).padStart(2, "0");

  // Hours and minutes
  let hh = d.getHours(); // 0–23
  const ampm = hh >= 12 ? "PM" : "AM";
  hh = hh % 12 || 12; // convert 0 → 12, 13 → 1, etc.
  const mm = String(d.getMinutes()).padStart(2, "0");

  return `${MM}/${DD} ${hh}:${mm} ${ampm}`;
}

function scrollToBottom() {
  nextTick(() => {
    const el = msgsContainer.value;
    if (el) el.scrollTop = el.scrollHeight;
  });
}

function displayText(
  text,
  from,
  type,
  generationTime = 0,
  timestamp = formatDateMMDDhhmm()
) {
  if (from === "user") {
    messages.push({
      from: from,
      type: "message",
      text: text,
      timestamp: timestamp,
    });
    scrollToBottom();
  } else if (from === "assistant") {
    messages.push({
      from: from,
      type: type,
      text: text,
      timestamp: timestamp,
      generationTime: generationTime,
    });
  }
  scrollToBottom();
}

// function getChatHistory() {
//   loadingChats.value = true;
//   fetch(`${API_URL}/api/chat/${session.value.user.id}/${currentPagenation.value}`, {
//     method: "GET",
//     headers: {
//       "Content-Type": "application/json",
//       Authorization: `Bearer ${session.value.id}`,
//     },
//   }).then(async (res) => {
//     console.log(res);

//     if (res.ok) {
//       let data = await res.json();
//       console.log(data);

//       data.forEach((msgGroup) => {
//         console.log(msgGroup);
//         msgGroup["message"].forEach((message) => {
//           displayText(
//             message["value"],
//             msgGroup["from_type"],
//             message["type"],
//             msgGroup["generation_time"].toFixed(2),
//             formatDateMMDDhhmm(new Date(msgGroup["timestamp"]))
//           );
//         });
//       });

//       // answers.forEach((val) => {
//       //   displayText(val["value"], "assistant", val["type"], elapsedSec);
//       // });
//     } else {
//       displayText(
//         "Error fetching chats, reload your page and try again",
//         "assistant",
//         "message",
//         0
//       );
//     }
//     loadingChats.value = false;
//   });
// }

async function applyAction(val){
  console.log(JSON.parse(JSON.stringify(val)))
  props.action(JSON.parse(JSON.stringify(val)))
}
// — pull‐out the fetch logic —
async function loadChats(page = 1, prepend = false) {
  loadingChats.value = true;
  try {
    const res = await fetch(
      `${API_URL}/api/chat/${session.value.user.id}/${page}`,
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${session.value.id}`,
        },
      }
    );
    if (!res.ok) throw new Error("Fetch failed");
    const data = await res.json();
    if (data.length < PAGE_SIZE) noMoreChats.value = true;

    // build a flat array of message‐objects in chronological order
    const newMessages = [];
    data.forEach((group) => {
      const ts = formatDateMMDDhhmm(new Date(group.timestamp));
      group.message.forEach((msg) => {
        newMessages.push({
          from: group.from_type,
          type: msg.type,
          text: msg.value,
          timestamp: ts,
          generationTime: group.generation_time.toFixed(2),
        });
      });
    });

    // remember scrollHeight before we prepend
    const el = msgsContainer.value;
    const prevScrollHeight = el?.scrollHeight || 0;

    if (prepend) {
      // add older messages at the front
      messages.unshift(...newMessages);
    } else {
      // initial load
      messages.push(...newMessages);
    }

    await nextTick();

    // restore scroll so content doesn’t jump
    if (el && prepend) {
      const newScrollHeight = el.scrollHeight;
      el.scrollTop = newScrollHeight - prevScrollHeight;
    } else if (el) {
      // initial load: scroll to bottom
      el.scrollTop = el.scrollHeight;
    }
  } catch (err) {
    console.error("Error loading chats:", err);
  } finally {
    loadingChats.value = false;
  }
}

// — scroll handler to detect “at top” and load the next page —
function onScroll() {
  const el = msgsContainer.value;
  if (!el || loadingChats.value || noMoreChats.value) return;
  if (el.scrollTop === 0) {
    currentPage.value += 1;
    loadChats(currentPage.value, true);
  }
}

function fullscreenToggle() {
  if (fullscreen.value) {
    // Reverts back to small
    chatWidth.value = 380;
  } else {
    chatWidth.value = window.outerWidth; // Makes it full screen
  }
  fullscreen.value = !fullscreen.value;
}

async function send() {
  const txt = draft.value.trim();
  if (!txt) return;

  displayText(txt, "user");

  displayText("Loading...", "assistant", "skeleton-text");

  const start = Date.now();

  loading.value = true;

  fetch(`${API_URL}/api/ai/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${session.value.id}`,
    },
    body: JSON.stringify({
      prompt: txt,
      session_id: session.value.id,
      context_source: unref(props.sheetId),
      selectedCells: props.selectedCells
    }),
  }).then(async (res) => {
    messages.pop();

    console.log(res);

    if (res.ok) {
      let data = await res.json();
      console.log(data);
      const elapsedSec = (Date.now() - start) / 1000;

      let answers = data["answer"];

      answers.forEach((val) => {
        displayText(val["value"], "assistant", val["type"], elapsedSec);
      });
    } else {
      const elapsedSec = (Date.now() - start) / 1000;
      let body = await res.json();
      let errMsg = body["detail"];
      displayText(errMsg, "assistant", "message", elapsedSec);
    }

    loading.value = false;
  });
  draft.value = "";
}

function close() {
  emit("close");
}

let startX, startWidth;

function startResize(event) {
  startX = event.clientX;
  startWidth = chatWidth.value;
  isResizing.value = true;
  document.documentElement.addEventListener("mousemove", doResize);
  document.documentElement.addEventListener("mouseup", stopResize);
}

function doResize(event) {
  const newWidth = startWidth + (event.clientX - startX);
  chatWidth.value = Math.max(newWidth, minWidth); // Ensure minimum width
}

function stopResize() {
  isResizing.value = false;
  document.documentElement.removeEventListener("mousemove", doResize);
  document.documentElement.removeEventListener("mouseup", stopResize);
}

onMounted(() => {
  // Any additional setup if needed
});

onBeforeUnmount(() => {
  // Clean up event listeners if needed
  document.documentElement.removeEventListener("mousemove", doResize);
  document.documentElement.removeEventListener("mouseup", stopResize);
});
</script>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap");

.sheet-chat {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #ffffff;
  font-family: "Inter", sans-serif;
  z-index: 1000;
  position: relative;
  border: 1px solid #e0e0e0; /* Light grey border */
  box-shadow: none !important; /* Ensure no shadow */
}

/* header with title + close */
.chat-header {
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

.loading-div {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  max-width: 75vw;
  margin-left: auto;
  margin-right: auto;
  min-width: 380px;
  position: relative;
  top: 30%;
}

/* suggestions row */
.suggestions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e0e0e0;
  max-width: 75vw;
  margin-left: auto;
  margin-right: auto;
  min-width: 380px;
}
.suggestion {
  max-width: 75vw;
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
  max-width: 60vw;
  min-width: 360px;
  width: 100%;
  margin-left: auto;
  margin-right: auto;
}
.message {
  margin: 0.4rem 0;
  line-height: 1.4;
  font-size: 0.95rem;
}
.message.user {
  text-align: right;
  color: #3f51b5;
  margin-left: 5%;
  padding-inline: 1rem;
  padding-top: 1rem;
  font-weight: 800;
}
.message.assistant {
  text-align: left;
  color: #333;
  margin-right: 5%;
  padding-inline: 1rem;
  padding-top: 1rem;
}

/* input bar pinned at bottom */
.input-bar {
  display: flex;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-top: 1px solid #e0e0e0;
  max-width: 45vw;
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

.timestamp {
  color: gray;
  font-size: 12px;
}

.generatedTime {
  color: gray;
  font-size: 12px;
}

.context-badge {
  display: flex;
  gap: 0.4rem;
  width: fit-content;
  height: 2rem;
  padding-inline: 1rem;
  padding-block: 0.4rem;
  border: 1px solid #f0f0f0; /* Lighter border */
  font-size: 0.875rem;
  color: #333; /* Dark text color */
  border-radius: 6px; /* Slightly more rounded corners */
  box-shadow: none; /* Remove shadow */
  cursor: pointer;
  background-color: white; /* White background */
  transition: background-color 0.2s ease, border-color 0.2s ease; /* Smooth transition */
}

.context-badge:hover {
  cursor: pointer;
  background-color: #f9f9f9; /* Softer light gray on hover */
  border-color: #e0e0e0; /* Slightly darker border on hover */
}

.sheet-icon {
  color: rgb(3, 161, 3);
  margin-top: 0.1rem;
}

.context-text {
  font-size: 13px;
  margin-right: 1rem;
}

.org-img {
  height: 1.3rem;
  width: 1.3rem;
  border-radius: 4px;
}

.expand-btn {
  margin-right: 0.5rem;
  margin-top: 0.4rem;
}

.img {
  width: 100%;
  max-width: 40vw;
}

.loading-chats-label {
  margin-top: 0.5rem;
  color: gray;
  font-size: 12px;
  text-align: center;
}

.action-btn{
  font-size: 12px;
}
</style>
