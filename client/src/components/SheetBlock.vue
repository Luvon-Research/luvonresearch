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
import { onMounted } from "vue";
import jspreadsheet from "jspreadsheet-ce";
import "jspreadsheet-ce/dist/jspreadsheet.css";
import * as Y from "yjs";
import { WebsocketProvider } from "y-websocket";
import { ref } from "vue";
import ProgressSpinner from "primevue/progressspinner";

const API_URL = import.meta.env.VITE_API_URL;

const savingIndicator = ref(false);
const lastSaved = ref(formatDate());

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
  const provider = new WebsocketProvider(
    "ws://localhost:1234",
    "demo-room",
    ydoc
  );
  provider.on("status", (s) => console.log("Yjs status:", s.status));

  const ycells = ydoc.getMap("cells");
  let applyingRemote = false;
  let allowUpdates = true;

  // 2. Row‐update queue + debounce (200 ms)
  const updateQueue = new Map();
  let flushTimer;
  function scheduleFlush() {
    if (!allowUpdates) return;
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

    //console.log({ row_data: allRowsData, sheet_id: "1" })

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
    onchange: (instance, cell, x, y, newValue, oldValue) => {
      if (applyingRemote) return;
      if (newValue === oldValue) return;
      if (!allowUpdates) return;

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
</script>
