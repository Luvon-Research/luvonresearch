<template>
  <div class="d-flex justify-content-between saving-indicator">
    <Button
      type="button"
      label="Export Sheet"
      icon="pi pi-download"
      :loading="loading"
      class="export-btn"
      @click="donwnloadSheet"
    />
    <p v-if="savingIndicator">
      Saving Document to Cloud
      <ProgressSpinner
        style="width: 15px; height: 15px"
        strokeWidth="5"
        fill="transparent"
        animationDuration=".5s"
        aria-label="Saving Document"
      />
    </p>
    <p v-if="!savingIndicator" class="savingIndicator">
      Last Saved: {{ lastSaved }} <i class="pi pi-cloud-upload"></i>
    </p>
  </div>

  <div class="parent">
    <div id="spreadsheet"></div>
  </div>
</template>

<script setup>
import { onMounted } from "vue";
import jspreadsheet from "jspreadsheet-ce";
import "jspreadsheet-ce/dist/jspreadsheet.css";
import * as Y from "yjs";
import { WebsocketProvider } from "y-websocket";
import ProgressSpinner from "primevue/progressspinner";
import { HistoryRecord } from "jspreadsheet-ce";

const API_URL = import.meta.env.VITE_API_URL;

onMounted(async () => {
  // 0. Grab container
  const container = document.getElementById("spreadsheet");
  if (!container) {
    console.error("#spreadsheet not found");
    return;
  }

  // 1. Yjs + WebSocket
  const ydoc     = new Y.Doc();
  const provider = new WebsocketProvider("ws://localhost:1234", "demo-room", ydoc);
  provider.on("status", s => console.log("Yjs status:", s.status));

  const ycells        = ydoc.getMap("cells");
  let applyingRemote  = false;
  let allowUpdates    = true;

  // 2. Row‐update queue + debounce (200 ms)
  const updateQueue = new Map();  // rowID → rowData[]
  let   flushTimer;
  function scheduleFlush() {
    if (!allowUpdates) return;
    clearTimeout(flushTimer);
    flushTimer = setTimeout(flushUpdates, 200);
  }
  async function flushUpdates() {
    const batch = Array.from(updateQueue.entries());
    updateQueue.clear();
    await Promise.all(batch.map(([rowID, row_data]) =>
      fetch(`${API_URL}/api/sheets/row`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${""}`,
        },
        body: JSON.stringify({ row_id: rowID, row_data, sheet_id: "1" }),
      })
    ));
  }

  // 3. Initialize jspreadsheet
  const defaultCol = { type: "text", title: "", width: 100 };
  const sheets = jspreadsheet(container, {
    worksheets: [{ data: [], minDimensions: [100, 100] }],
    onchange: (instance, cell, x, y, newValue, oldValue) => {
      if (applyingRemote) return;
      if (newValue === oldValue) return;

      // 3a) write one cell into Yjs
      ydoc.transact(() => {
        ycells.set(`${x},${y}`, newValue);
      });

      // 3b) enqueue this row
      const rowData = instance.getRowData(y);
      updateQueue.set(y, rowData);
      scheduleFlush();
    },
  });
  const sheet = sheets[0];

  // 4. Load initial data (disable queue while seeding)
  allowUpdates = false;
  const initial = await fetch(`${API_URL}/api/sheets/1`)
    .then(r => r.json());
  initial.forEach(r => {
    const rowID   = Number(r.row_id);
    const rowData = r.row_data;

    // ensure sheet has at least rowID+1 rows
    const snapshotH = (sheet.getData() || []).length;
    if (rowID >= snapshotH) {
      sheet.insertRow(rowID - snapshotH + 1);
    }

    sheet.setRowData(rowID, rowData);
  });
  allowUpdates = true;

  // 5. Observe remote Yjs updates
  ycells.observe(event => {
    if (event.transaction.local) return;
    applyingRemote = true;

    // collect all changed cells
    const updates = Array.from(event.keysChanged).map(key => {
      const [col, row] = key.split(",").map(Number);
      return { col, row, val: ycells.get(key) };
    });

    // guard against empty grid
    const data     = sheet.getData() || [];
    let   currentW = data[0]?.length ?? 0;
    let   currentH = data.length;

    // find furthest-out cell
    const maxCol = Math.max(...updates.map(u => u.col), currentW - 1);
    const maxRow = Math.max(...updates.map(u => u.row), currentH - 1);

    // expand columns
    if (maxCol >= currentW) {
      for (let i = 0; i < maxCol - currentW + 1; i++) {
        sheet.insertColumn([], currentW + i, false, defaultCol);
      }
      currentW += maxCol - currentW + 1;
    }
    // expand rows
    if (maxRow >= currentH) {
      sheet.insertRow(maxRow - currentH + 1);
      currentH += maxRow - currentH + 1;
    }

    // apply each changed cell
    updates.forEach(({ col, row, val }) => {
      sheet.setValueFromCoords(col, row, val);
    });

    applyingRemote = false;
  });
});

onUnmounted(() => {
  console.log("SheetBlock unmounting. Disconnecting Yjs and destroying sheet.");
  if (provider) {
    provider.disconnect();
  }
  if (ydoc) {
    // ydoc.destroy(); // Consider if ydoc should be destroyed or just disconnected
  }
  if (sheet && typeof sheet.destroy === 'function') {
    const container = document.getElementById("spreadsheet");
    if (container) {
      // Use the official destroy method if available and the container exists
      jspreadsheet.destroy(container);
      console.log("jspreadsheet instance destroyed.");
    }
  }
  // Nullify references
  sheet = null;
  ydoc = null;
  provider = null;
  ycells = null;
  clearTimeout(flushTimer); // Clear any pending save timeouts
});
</script>