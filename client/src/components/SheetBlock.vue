<template>
  <div class="d-flex justify-content-end saving-indicator">
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
    <p v-if="!savingIndicator">Last Saved: {{ lastSaved }}</p>
  </div>

  <div class="parent">
    <div id="spreadsheet" class="spreadsheet-section"></div>
  </div>
</template>

<style scoped>
.parent {
  display: flex;
  height: 68vh;
}

.saving-indicator {
  margin-right: 1rem;
}

.spreadsheet-section {
  overflow-y: scroll;
}

</style>

<script setup>
import { onMounted, onUnmounted, ref, watch, defineProps, nextTick } from "vue";
import jspreadsheet from "jspreadsheet-ce";
import "jspreadsheet-ce/dist/jspreadsheet.css";
import * as Y from "yjs";
import { WebsocketProvider } from "y-websocket";
import ProgressSpinner from "primevue/progressspinner";

const props = defineProps({
  sheetId: {
    type: String,
    default: null,
  },
});

const savingIndicator = ref(false);
const lastSaved = ref(formatDate());
const loading = ref(false);
const error = ref(null);
const API_URL = import.meta.env.VITE_API_URL;

let sheet = null;
let ydoc = null;
let provider = null;
let ycells = null;
let allowUpdates = true;
const updateQueue = new Map();
let flushTimer = null;
const defaultCol = { type: "text", title: "", width: 100 };

function formatDate(date = new Date()) {
  const pad = (n) => String(n).padStart(2, "0");

  const month = pad(date.getMonth() + 1);
  const day = pad(date.getDate());
  const year = String(date.getFullYear()).slice(-2);

  let hours = date.getHours();
  const ampm = hours >= 12 ? "PM" : "AM";
  hours = hours % 12 || 12; // 0 → 12
  const hh = pad(hours);

  const mm = pad(date.getMinutes());
  const ss = pad(date.getSeconds());

  return `${month}/${day}/${year} ${hh}:${mm}:${ss} ${ampm}`;
}

async function updateSheetDisplay(sheetData = []) {
  if (!sheet) {
    console.warn("updateSheetDisplay called before sheet initialized.");
    return;
  }

  console.log("Attempting to update sheet display with data:", sheetData);
  allowUpdates = false;

  try {
    const minDims = sheet.options.minDimensions || [10, 10];
    const emptyData = Array(minDims[1]).fill(0).map(() => Array(minDims[0]).fill(''));
    sheet.setData(emptyData);

    await nextTick();

    if (sheetData && sheetData.length > 0) {
      let maxRow = -1;
      let maxCol = -1;
      sheetData.forEach(r => {
        const rowID = Number(r.row_id);
        if (rowID > maxRow) maxRow = rowID;
        if (r.row_data) {
          r.row_data.forEach(cell => {
            if (cell.col > maxCol) maxCol = cell.col;
          });
        }
      });

      const currentData = sheet.getData();
      const currentH = currentData.length;
      const currentW = currentData[0]?.length ?? 0;

      if (maxRow >= currentH) {
        console.log(`Inserting ${maxRow - currentH + 1} rows`);
        sheet.insertRow(maxRow - currentH + 1);
      }
      if (maxCol >= currentW) {
        console.log(`Inserting ${maxCol - currentW + 1} columns`);
        sheet.insertColumn(maxCol - currentW + 1, currentW);
      }

      await nextTick();

      sheetData.forEach((r) => {
        const rowID = Number(r.row_id);
        const rowData = r.row_data || [];

        for (let i = 0; i < rowData.length; i++) {
          if (typeof rowData[i] === 'object' && rowData[i] !== null && 'col' in rowData[i] && 'val' in rowData[i]) {
            sheet.setValueFromCoords(rowData[i].col, rowID, rowData[i].val, true);
          } else {
            console.warn(`Invalid row data item at index ${i} for row ${rowID}:`, rowData[i]);
          }
        }
      });
      console.log("Finished applying data to sheet.");
    } else {
      console.log("No data provided, sheet remains empty (reset to minDimensions).");
    }

  } catch (err) {
    console.error("Error updating sheet display:", err);
    error.value = "Failed to display sheet data.";
  } finally {
    setTimeout(() => {
      allowUpdates = true;
      console.log("Re-enabled sheet updates.");
    }, 150);
  }
}

function setupYjsConnection(id) {
  if (provider) {
    console.log("Disconnecting previous Yjs provider...");
    provider.disconnect();
    provider = null;
  }
  if (ydoc) {
  }

  if (!id) {
    console.warn("No sheet ID provided, cannot set up Yjs connection.");
    if (ycells) ycells.unobserve(onYjsObserve);
    ydoc = null;
    ycells = null;
    return;
  }

  console.log(`Setting up Yjs connection for sheet: ${id}`);
  if (!ydoc) ydoc = new Y.Doc();

  const roomName = `sheet-${id}`;
  provider = new WebsocketProvider(
    "ws://localhost:1234",
    roomName,
    ydoc
  );
  provider.on("status", (event) => console.log(`Yjs status (${id}): ${event.status}`));

  ycells = ydoc.getMap("cells");
  ycells.unobserve(onYjsObserve);
  ycells.observe(onYjsObserve);
}

let applyingRemote = false;
const onYjsObserve = (event) => {
  if (event.transaction.local || !sheet) return;
  applyingRemote = true;
  console.log("Applying remote Yjs changes");

  const updates = Array.from(event.keysChanged).map((key) => {
    const [col, row] = key.split(",").map(Number);
    return { col, row, val: ycells.get(key) };
  });

  const data = sheet.getData() || [];
  let currentW = data[0]?.length ?? 0;
  let currentH = data.length;
  const maxCol = Math.max(...updates.map((u) => u.col), currentW - 1);
  const maxRow = Math.max(...updates.map((u) => u.row), currentH - 1);

  if (maxCol >= currentW) {
    sheet.insertColumn(maxCol - currentW + 1, currentW);
  }
  if (maxRow >= currentH) {
    sheet.insertRow(maxRow - currentH + 1);
  }

  updates.forEach(({ col, row, val }) => {
    sheet.setValueFromCoords(col, row, val, true);
  });

  applyingRemote = false;
  console.log("Finished applying remote Yjs changes");
};

async function loadSheetData() {
  if (!props.sheetId) {
    console.log("loadSheetData: No sheet ID, clearing display.");
    await updateSheetDisplay([]);
    error.value = null;
    loading.value = false;
    setupYjsConnection(null);
    return;
  }

  loading.value = true;
  error.value = null;
  console.log(`SheetBlock: Fetching data for sheet ID: ${props.sheetId}`);

  try {
    const response = await fetch(`${API_URL}/api/sheets/${props.sheetId}`, {
      headers: {
        Authorization: `Bearer ${""}`,
      },
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    console.log("Fetched data (DATADOG):", data);

    await updateSheetDisplay(data);

    setupYjsConnection(props.sheetId);

  } catch (err) {
    console.error("Error loading sheet data:", err);
    error.value = err.message || 'Failed to load sheet data.';
    await updateSheetDisplay([]);
    setupYjsConnection(null);
  } finally {
    loading.value = false;
  }
}

watch(() => props.sheetId, (newId, oldId) => {
  console.log(`Sheet ID changed from ${oldId} to ${newId}`);
  if (newId !== oldId) {
    loadSheetData();
  }
}, { immediate: true });

function scheduleFlush() {
  if (!allowUpdates) return;
  clearTimeout(flushTimer);
  flushTimer = setTimeout(flushUpdates, 500);
}

async function flushUpdates() {
  if (!props.sheetId) {
    console.warn("flushUpdates called without sheetId.");
    return;
  }
  if (updateQueue.size === 0) return;

  savingIndicator.value = true;
  const batch = Array.from(updateQueue.entries());
  console.log("Saving batch:", batch);
  updateQueue.clear();

  let allRowsData = [];
  batch.forEach(([rowID, row_data]) => {
    let data = [];
    if (Array.isArray(row_data)) {
      for (let i = 0; i < row_data.length; i++) {
        if (row_data[i] !== null && row_data[i] !== undefined && row_data[i] !== "") {
          data.push({ col: i, val: row_data[i] });
        }
      }
    }
    if (data.length > 0) {
      allRowsData.push({ row_id: rowID, row_data: data });
    }
  });

  if (allRowsData.length === 0) {
    console.log("No changes with data to save.");
    savingIndicator.value = false;
    return;
  }

  console.log("Formatted data for saving:", { row_data: allRowsData, sheet_id: props.sheetId });

  try {
    const response = await fetch(`${API_URL}/api/sheets/rows`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${""}`,
      },
      body: JSON.stringify({ row_data: allRowsData, sheet_id: props.sheetId }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to save updates: ${response.status} ${errorText}`);
    }

    console.log("Save successful");
    lastSaved.value = formatDate();

  } catch (err) {
    console.error("Error saving updates:", err);
    error.value = "Failed to save changes.";
  } finally {
    savingIndicator.value = false;
  }
}

onMounted(async () => {
  const container = document.getElementById("spreadsheet");
  if (!container) {
    console.error("#spreadsheet container not found");
    return;
  }

  console.log("Initializing jspreadsheet...");
  const sheetInstances = jspreadsheet(container, {
    worksheets: [{
      data: [],
      minDimensions: [100, 100],
    }],
    onchange: (instance, cell, x, y, newValue, oldValue) => {
      if (applyingRemote || !allowUpdates || newValue === oldValue) return;

      if (ydoc) {
        ydoc.transact(() => {
          if (ycells) ycells.set(`${x},${y}`, newValue);
        });
      }

      const rowData = instance.getRowData(y);
      updateQueue.set(y, rowData);
      scheduleFlush();
    },
  });
  sheet = sheetInstances[0];
  console.log("jspreadsheet initialized.");
});

onUnmounted(() => {
  console.log("SheetBlock unmounting. Disconnecting Yjs and destroying sheet.");
  if (provider) {
    provider.disconnect();
  }
  if (ydoc) {
  }
  if (sheet && typeof sheet.destroy === 'function') {
    const container = document.getElementById("spreadsheet");
    if (container) {
      jspreadsheet.destroy(container);
      console.log("jspreadsheet instance destroyed.");
    }
  }
  sheet = null;
  ydoc = null;
  provider = null;
  ycells = null;
  clearTimeout(flushTimer);
});
</script>
