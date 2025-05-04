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

<style scoped>
.parent {
  display: flex;
  height: 68vh;
}

.saving-indicator {
  margin-right: 1rem;
  color: rgb(165, 165, 165);
}

.spreadsheet-section {
  overflow-y: scroll;
}

.export-btn {
  margin-bottom: 0.5rem;
  font-size: 13px;
}
</style>

<script setup>
import Button from "primevue/button";
import { onMounted } from "vue";
import jspreadsheet from "jspreadsheet-ce";
import "jspreadsheet-ce/dist/jspreadsheet.css";
import * as Y from "yjs";
import { WebsocketProvider } from "y-websocket";
import { ref } from "vue";
import ProgressSpinner from "primevue/progressspinner";
import { HistoryRecord } from "jspreadsheet-ce";

const API_URL = import.meta.env.VITE_API_URL;
const YJS_URL = import.meta.env.VITE_YJS_SERVER_URL;

const savingIndicator = ref(false);
const lastSaved = ref(formatDate());

const loading = ref(false);

function donwnloadSheet() {
  loading.value = true;

  fetch(`${API_URL}/api/sheets/export/1`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${""}`,
    },
  }).then(async (res) => {
    if (!res.ok) {
      console.log("ERROR");
      console.log(res);
    } else {
      // 1) Pull out the blob
      const blob = await res.blob();

      // 2) Figure out a filename from headers (optional)
      const contentDisp = res.headers.get("Content-Disposition") || "";
      const filenameMatch = /filename="(.+)"/.exec(contentDisp);
      const filename = filenameMatch ? filenameMatch[1] : "sheet.csv";

      // 3) Create an object URL and click an <a> to download
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();

      // 4) Clean up
      window.URL.revokeObjectURL(url);
    }
    loading.value = false;
  });
}

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

onMounted(async () => {
  // Container for
  const container = document.getElementById("spreadsheet");
  if (!container) {
    console.error("#spreadsheet not found");
    return;
  }

  // 1. Yjs + WebSocket
  const ydoc = new Y.Doc();
  const provider = new WebsocketProvider(YJS_URL, "demo-room", ydoc);
  provider.on("status", (s) => console.log("Yjs status:", s.status));

  const ycells = ydoc.getMap("cells");
  let applyingRemote = false;
  let allowUpdates = true;

  // 2. Row‐update queue + debounce (200 ms)
  const updateQueue = new Map();
  let flushTimer;
  function scheduleFlush() {
    console.log("YO");
    //if (!allowUpdates) return;
    clearTimeout(flushTimer);
    flushTimer = setTimeout(flushUpdates, 200);
  }
  async function flushUpdates() {
    savingIndicator.value = true;
    const batch = Array.from(updateQueue.entries());
    console.log("SAVING");
    updateQueue.clear();
    let allRowsData = [];
    await Promise.all(
      batch.map(([rowID, row_data]) => {
        // Split row data into only filled cells
        let data = [];
        for (let i = 0; i < row_data.length; i++) {
          if (row_data[i] != "") {
            data.push({ col: i, val: row_data[i] });
          }
        }

        //console.log(data);
        allRowsData.push({ row_id: rowID, row_data: data });
      })
    );

    console.log({ row_data: allRowsData, sheet_id: "1" });

    fetch(`${API_URL}/api/sheets/rows`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${""}`,
      },
      body: JSON.stringify({ row_data: allRowsData, sheet_id: "1" }),
    }).then(() => {
      savingIndicator.value = false;
      lastSaved.value = formatDate();
    });
  }

  // 3. Initialize jspreadsheet
  const defaultCol = { type: "text", title: "", width: 100 };
  const sheets = jspreadsheet(container, {
    worksheets: [{ data: [], minDimensions: [100, 100] }],
    onundo: (instance, historyRecord) => {
      console.log(historyRecord);
      // nothing to do if it's a remote update, undo stack is empty, or we're seeding
      if (applyingRemote || !allowUpdates || !historyRecord) return;

      for (let i = 0; i < historyRecord.records.length; i++) {
        let record = historyRecord.records[i];
        console.log(record)
        // pull out the undone cell's coords (inspect historyRecord if these keys differ)
        const x = record.x;
        const y = record.y;

        console.log(x, y);

        // grab the reverted value from the sheet
        const revertedValue = instance.getValueFromCoords(x, y);

        // write it into Yjs
        ydoc.transact(() => {
          ycells.set(`${x},${y}`, revertedValue);
        });

        // enqueue the entire row for a batched save
        const rowData = instance.getRowData(y);
        updateQueue.set(y, rowData);
      }

      // schedule the save
      scheduleFlush();
    },
    onchange: (instance, cell, x, y, newValue, oldValue) => {
      if (applyingRemote) return;
      if (newValue === oldValue) return;
      if (!allowUpdates) return;

      console.log("HYO");

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
  const initial = await fetch(`${API_URL}/api/sheets/1`).then((r) => r.json());
  initial.forEach((r) => {
    const rowID = Number(r.row_id);
    const rowData = r.row_data;

    // ensure sheet has at least rowID+1 rows
    const snapshotH = (sheet.getData() || []).length;
    if (rowID >= snapshotH) {
      sheet.insertRow(rowID - snapshotH + 1);
    }

    for (let i = 0; i < rowData.length; i++) {
      sheet.setValueFromCoords(rowData[i].col, rowID, rowData[i].val);
    }
    //sheet.setRowData(rowID, rowData);
  });
  allowUpdates = true;

  // 5. Observe remote Yjs updates
  ycells.observe((event) => {
    if (event.transaction.local) return;
    applyingRemote = true;

    // collect all changed cells
    const updates = Array.from(event.keysChanged).map((key) => {
      const [col, row] = key.split(",").map(Number);
      return { col, row, val: ycells.get(key) };
    });

    // guard against empty grid
    const data = sheet.getData() || [];
    let currentW = data[0]?.length ?? 0;
    let currentH = data.length;

    // find furthest-out cell
    const maxCol = Math.max(...updates.map((u) => u.col), currentW - 1);
    const maxRow = Math.max(...updates.map((u) => u.row), currentH - 1);

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