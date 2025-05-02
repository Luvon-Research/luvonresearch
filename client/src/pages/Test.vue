<template>
    <div class="collab-container">
      <textarea
        ref="ta"
        rows="10"
        cols="50"
        placeholder="Type here…"
      />
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, onMounted, onUnmounted, nextTick } from "vue";
  import * as Y from "yjs";
  import { WebsocketProvider } from "y-websocket";
  
  const ta = ref<HTMLTextAreaElement|null>(null);
  
  onMounted(async () => {
    // 1) Set up Yjs + WebSocket
    const room = "my-room-name";
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const url = `${protocol}://${window.location.hostname}:1234`;
    const ydoc = new Y.Doc();
    const provider = new WebsocketProvider(url, room, ydoc);
    const ytext = ydoc.getText("shared-text");
  
    // 2) After mount, initialize the textarea from ytext
    await nextTick();
    if (ta.value) {
      ta.value.value = ytext.toString();
    }
  
    // 3) On local edits, compute a simple prefix‐diff and apply just that
    const onLocalInput = () => {
      if (!ta.value) return;
      const newVal = ta.value.value;
      const oldVal = ytext.toString();
      let i = 0;
      while (i < oldVal.length && i < newVal.length && oldVal[i] === newVal[i]) {
        i++;
      }
      // Delete the tail of oldVal
      if (oldVal.length > i) {
        ytext.delete(i, oldVal.length - i);
      }
      // Insert the tail of newVal
      if (newVal.length > i) {
        ytext.insert(i, newVal.slice(i));
      }
    };
    ta.value?.addEventListener("input", onLocalInput);
  
    // 4) Observe remote updates, patch the textarea in place, restore cursor
    const onRemoteUpdate = () => {
      if (!ta.value) return;
      const newVal = ytext.toString();
      if (ta.value.value !== newVal) {
        const start = ta.value.selectionStart;
        const end = ta.value.selectionEnd;
        ta.value.value = newVal;
        // put the cursor back roughly where it was
        ta.value.setSelectionRange(start, end);
      }
    };
    ytext.observe(onRemoteUpdate);
  
    // 5) Cleanup
    onUnmounted(() => {
      provider.disconnect();
      ydoc.destroy();
      ta.value?.removeEventListener("input", onLocalInput);
      ytext.unobserve(onRemoteUpdate);
    });
  });
  </script>
  
  <style scoped>
  .collab-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 1rem;
  }
  textarea {
    width: 100%;
    font-family: monospace;
  }
  </style>
  