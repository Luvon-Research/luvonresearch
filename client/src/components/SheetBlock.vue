<template>
  <div class="d-flex justify-content-between saving-indicator">
    <div class="d-flex gap-2">
      <Button
        type="button"
        label="Export Sheet"
        icon="pi pi-download"
        :loading="loading"
        class="export-btn"
        @click="donwnloadSheet"
      />
      <Button
        type="button"
        variant="outlined"
        label="Delete Sheet"
        icon="pi pi-trash"
        class="delete-btn"
        :loading="deleteLoading"
        @click="deleteSheet"
      />
    </div>
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

  <div>
    <div id="spreadsheet"></div>
  </div>
</template>

<style scoped>
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

.delete-btn {
  margin-bottom: 0.5rem;
  font-size: 13px;
}
</style>

<script setup>
import { onMounted, onUnmounted, ref, watch, nextTick } from "vue";
import Button from "primevue/button";
import jspreadsheet from "jspreadsheet-ce";
import "jspreadsheet-ce/dist/jspreadsheet.css";
import * as Y from "yjs";
import { WebsocketProvider } from "y-websocket";
import ProgressSpinner from "primevue/progressspinner";
import { HistoryRecord } from "jspreadsheet-ce";
import { useSession } from "@clerk/vue";

const props = defineProps({
  sheetId: {
    type: String,
    default: null,
  },
  setSelectedCells: {
    type: Function,
  },
  action: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits(['sheet-deleted']);

const API_URL = import.meta.env.VITE_API_URL;
const YJS_URL = import.meta.env.VITE_YJS_SERVER_URL;

const savingIndicator = ref(false);
const lastSaved = ref(formatDate());
const error = ref(null);
const selectedCellsLocal = ref({});
const deleteLoading = ref(false);

let sheet = null;
let ydoc = null;
let provider = null;
let ycells = null;
let allowUpdates = false;
const updateQueue = new Map();
let flushTimer = null;
const defaultCol = { type: "text", title: "", width: 100 };

const loading = ref(false);

const { session } = useSession();

function donwnloadSheet() {
  loading.value = true;

  fetch(`${API_URL}/api/sheets/export/${props.sheetId}`, {
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

async function updateSheetDisplay(sheetData = []) {
  if (!sheet) {
    console.warn("updateSheetDisplay called before sheet initialized.");
    return;
  }

  console.log("Attempting to update sheet display with data:", sheetData);
  allowUpdates = false; // Prevent local changes/saves while loading data

  try {
    // Reset the sheet to minimum dimensions before applying new data
    const minDims = sheet.options.minDimensions || [10, 10];
    const emptyData = Array(minDims[1])
      .fill(0)
      .map(() => Array(minDims[0]).fill(""));
    sheet.setData(emptyData);

    await nextTick(); // Wait for DOM update after setData

    // Apply the fetched data if available
    if (sheetData && sheetData.length > 0) {
      // Determine required dimensions from data
      let maxRow = -1;
      let maxCol = -1;
      sheetData.forEach((r) => {
        const rowID = Number(r.row_id);
        if (rowID > maxRow) maxRow = rowID;
        if (r.row_data) {
          r.row_data.forEach((cell) => {
            if (cell.col > maxCol) maxCol = cell.col;
          });
        }
      });

      // Ensure sheet dimensions are large enough
      const currentData = sheet.getData();
      const currentH = currentData.length;
      const currentW = currentData[0]?.length ?? 0; // Handle case where sheet might be empty

      // Calculate required dimensions, ensuring they are at least minDims
      const requiredRows = Math.max(maxRow + 1, minDims[1]);
      const requiredCols = Math.max(maxCol + 1, minDims[0]);

      // Adjust rows if needed
      if (requiredRows > currentH) {
        console.log(`Inserting ${requiredRows - currentH} rows`);
        // jspreadsheet insertRow adds rows *after* the specified index,
        // so to add rows at the end, we specify the last current index.
        // The count is the number of rows to add.
        sheet.insertRow(requiredRows - currentH, currentH - 1);
      }
      // Adjust columns if needed
      if (requiredCols > currentW) {
        console.log(`Inserting ${requiredCols - currentW} columns`);
        // Similar logic for columns
        sheet.insertColumn(requiredCols - currentW, currentW - 1);
      }

      await nextTick(); // Wait for DOM update after potential insertions

      // Populate the sheet with data
      sheetData.forEach((r) => {
        const rowID = Number(r.row_id);
        const rowData = r.row_data || [];

        for (let i = 0; i < rowData.length; i++) {
          // Check if rowData[i] is the expected object format
          if (
            typeof rowData[i] === "object" &&
            rowData[i] !== null &&
            "col" in rowData[i] &&
            "val" in rowData[i]
          ) {
            // Ensure coordinates are within the (potentially expanded) bounds
            if (rowID < requiredRows && rowData[i].col < requiredCols) {
              sheet.setValueFromCoords(
                rowData[i].col,
                rowID,
                rowData[i].val,
                true
              ); // Mark as programmatic change
            } else {
              console.warn(
                `Skipping out-of-bounds cell data at (${rowData[i].col}, ${rowID})`
              );
            }
          } else {
            // Log if the data format is unexpected
            console.warn(
              `Invalid row data item format at index ${i} for row ${rowID}:`,
              rowData[i]
            );
          }
        }
      });
      console.log("Finished applying data to sheet.");
    } else {
      // If no data, the sheet is already reset to minDimensions
      console.log(
        "No data provided, sheet remains empty (reset to minDimensions)."
      );
    }
  } catch (err) {
    console.error("Error updating sheet display:", err);
    error.value = "Failed to display sheet data.";
    // Consider resetting sheet again or showing an error overlay
  } finally {
    // Re-enable updates after a short delay to allow rendering
    setTimeout(() => {
      //allowUpdates = true;
      console.log("Re-enabled sheet updates.");
    }, 300); // Adjust delay if needed
  }
}

async function setupYjsConnection(id) {
  if (provider) {
    console.log("Disconnecting previous Yjs provider...");
    provider.disconnect();
    provider = null;
  }
  if (ydoc) {
    // Potentially destroy or reset ydoc if needed, or just let it be replaced
  }

  if (!id) {
    console.warn("No sheet ID provided, cannot set up Yjs connection.");
    if (ycells) ycells.unobserve(onYjsObserve);
    // ydoc = null; // Keep ydoc instance for potential reuse
    ycells = null;
    return;
  }

  if (!YJS_URL) {
    console.error(
      "YJS_URL environment variable is not defined! Cannot establish WebSocket connection."
    );
    error.value = "Configuration error: Collaboration server URL is missing.";
    // Ensure cleanup if URL is missing
    if (provider) provider.disconnect();
    provider = null;
    ycells = null;
    return; // Stop execution if URL is missing
  }

  console.log(`Setting up Yjs connection for sheet: ${id}`);
  if (!ydoc) ydoc = new Y.Doc(); // Create ydoc only if it doesn't exist

  const roomName = `sheet-${id}`;
  console.log(
    `Attempting to connect WebsocketProvider with URL: '${YJS_URL}', room: '${roomName}'`
  ); // Log values

  try {
    provider = new WebsocketProvider(
      YJS_URL, // Use the environment variable
      roomName,
      ydoc
    );
    provider.on("status", (event) =>
      console.log(`Yjs status (${id}): ${event.status}`)
    );

    ycells = ydoc.getMap("cells");
    //ycells.unobserve(onYjsObserve); // Ensure previous observer is removed
    ycells.observe(onYjsObserve);
    console.log(`Yjs connection setup complete for sheet: ${id}`);
  } catch (err) {
    console.error(`Failed to create WebsocketProvider for sheet ${id}:`, err);
    error.value = `Failed to connect to collaboration server for sheet ${id}. Please check the configuration or network.`;
    // Clean up potentially partially created state
    if (provider) provider.disconnect();
    provider = null;
    ycells = null;
  }
}

let applyingRemote = false;
const onYjsObserve = (event) => {
  if (event.transaction.local || !sheet || !allowUpdates) return;
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
    sheet.setValueFromCoords(col, row, val, true); // Mark as programmatic change
  });

  applyingRemote = false;
  console.log("Finished applying remote Yjs changes");
};

async function loadSheetData() {
  if (!props.sheetId) {
    console.log("loadSheetData: No sheet ID, clearing display.");
    error.value = null;
    loading.value = false;
    allowUpdates = false;
    return;
  }

  loading.value = true;
  error.value = null;
  allowUpdates = false;
  console.log(`SheetBlock: Fetching data for sheet ID: ${props.sheetId}`);

  try {
    const response = await fetch(`${API_URL}/api/sheets/${props.sheetId}`, {
      headers: {
        Authorization: `Bearer ${session.value.id}`,
      },
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    console.log("Fetched data (DATADOG):", data);

    // Update the sheet display first
    await updateSheetDisplay(data).then(() => {
      setupYjsConnection(props.sheetId);
    });

    // Then set up Yjs connection for this sheet
  } catch (err) {
    console.error("Error loading sheet data:", err);
    error.value = err.message || "Failed to load sheet data.";
    await updateSheetDisplay([]); // Clear sheet on error
    setupYjsConnection(null); // Disconnect Yjs on error
  } finally {
    loading.value = false;

    setTimeout(() => {
      allowUpdates = true;
    }, 1000);
  }
}

function handleActionFromAI(action){
  if(!sheet) return;

  if(action['action_type'] === 'update' && action['target'] === 'sheet'){
    action['data'].forEach(val => {
      console.log(val)
      sheet.setValueFromCoords(val['x'], val['y'], val['val'], true)
    })
  } else {
    console.log("ACTION NOT SUPPORTED")
    return
  }
}

// Watch for changes in sheetId prop
watch(
  () => props.sheetId,
  (newId, oldId) => {
    console.log(`Sheet ID changed from ${oldId} to ${newId}`);
    if (newId !== oldId) {
      loadSheetData();
    }
  },
  { immediate: true }
); // Load data immediately when component mounts

watch(
  () => props.action,
  (newAction, oldAction) => {
    console.log("ACTION REACHED", newAction);
    handleActionFromAI(newAction);
  },
  { immediate: true }
);

function scheduleFlush() {
  if (!allowUpdates) return; // Don't schedule if updates are disallowed (e.g., during initial load)
  clearTimeout(flushTimer);
  flushTimer = setTimeout(flushUpdates, 200); // Debounce saves
}

async function flushUpdates() {
  if (!props.sheetId) {
    console.warn("flushUpdates called without sheetId.");
    return;
  }
  if (updateQueue.size === 0) return; // Nothing to save

  savingIndicator.value = true;
  const batch = Array.from(updateQueue.entries());
  console.log("Saving batch:", batch);
  updateQueue.clear(); // Clear queue immediately

  // Format data for the backend
  let allRowsData = [];
  batch.forEach(([rowID, row_data]) => {
    let data = [];
    if (Array.isArray(row_data)) {
      for (let i = 0; i < row_data.length; i++) {
        // Only include cells that have actual values
        if (row_data[i] !== undefined && row_data[i] !== "") {
          data.push({ col: i, val: row_data[i] });
        }
      }
    }
    // Only include rows that have some data after filtering
    if (data.length > 0) {
      allRowsData.push({ row_id: rowID, row_data: data });
    }
  });

  if (allRowsData.length === 0) {
    console.log("No changes with data to save.");
    savingIndicator.value = false;
    return; // Don't send empty requests
  }

  console.log("Formatted data for saving:", {
    row_data: allRowsData,
    sheet_id: props.sheetId,
  });

  try {
    const response = await fetch(`${API_URL}/api/sheets/rows`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${session.value.id}`,
      },
      body: JSON.stringify({ row_data: allRowsData, sheet_id: props.sheetId }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(
        `Failed to save updates: ${response.status} ${errorText}`
      );
    }

    console.log("Save successful");
    lastSaved.value = formatDate(); // Update last saved time
  } catch (err) {
    console.error("Error saving updates:", err);
    error.value = "Failed to save changes.";
    // Consider re-adding failed updates to the queue or showing a persistent error
  } finally {
    savingIndicator.value = false;
  }
}

async function deleteSheet() {
  if (!confirm('Are you sure you want to delete this sheet?')) return;
  deleteLoading.value = true;
  
  try {
    const response = await fetch(`${API_URL}/api/sheets/${props.sheetId}/`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${session.value.id}`,
      },
    });

    deleteLoading.value = false;

    if (!response.ok) {
      throw new Error('Failed to delete sheet');
    }

    // Emit event to notify parent that sheet was deleted
    emit('sheet-deleted', props.sheetId);
  } catch (err) {
    deleteLoading.value = false;
    console.error('Error deleting sheet:', err);
    alert('Failed to delete sheet. Please try again.');
  }
}

onMounted(async () => {
  const container = document.getElementById("spreadsheet");
  if (!container) {
    console.error("#spreadsheet container not found");
    return;
  }

  // Initialize jspreadsheet with Yjs integration handlers
  const sheetInstances = jspreadsheet(container, {
    worksheets: [{ data: [], minDimensions: [100, 100] }], // Start with min dimensions
    onundo: (instance, historyRecord) => {
      console.log("Undo triggered:", historyRecord);
      // nothing to do if it's a remote update, undo stack is empty, or we're seeding
      if (applyingRemote || !allowUpdates || !historyRecord || !ydoc || !ycells)
        return;

      // Process each record in the undo history step
      for (let i = 0; i < historyRecord.records.length; i++) {
        let record = historyRecord.records[i];
        console.log("Undo record:", record);
        // pull out the undone cell's coords (inspect historyRecord if these keys differ)
        const x = record.x; // Column index
        const y = record.y; // Row index

        console.log(`Undoing change at (${x}, ${y})`);

        // grab the reverted value from the sheet *after* undo
        const revertedValue = instance.getValueFromCoords(x, y);

        // write the reverted value back into Yjs
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
      // Ignore changes triggered by remote updates, during loading, or if value hasn't changed
      if (applyingRemote || !allowUpdates || newValue === oldValue) return;

      console.log(
        `Local change at (${x}, ${y}): '${oldValue}' -> '${newValue}'`
      );

      // Update Yjs document
      if (ydoc) {
        ydoc.transact(() => {
          if (ycells) ycells.set(`${x},${y}`, newValue);
        });
      }

      // Queue the entire row for saving
      const rowData = instance.getRowData(y);

      // Handles special case when deleting a value of a cell
      if (newValue === "") {
        rowData[x] = null;
      }

      console.log(rowData);
      updateQueue.set(y, rowData);
      scheduleFlush(); // Debounce the save operation
    },
    onselection: (
      instance,
      leftIndex,
      topIndex,
      rightIndex,
      bottomIndex,
      origin
    ) => {
      //console.log(leftIndex, rightIndex, topIndex, bottomIndex)
      selectedCellsLocal.value = {
        leftIndex,
        topIndex,
        rightIndex,
        bottomIndex,
      };
      props.setSelectedCells({
        left: leftIndex,
        right: rightIndex,
        top: topIndex + 1,
        bottom: bottomIndex + 1,
      });
    },
    onblur: (instance) => {
      //props.setSelectedCells({});
      const { leftIndex, topIndex, rightIndex, bottomIndex } =
        selectedCellsLocal.value;
      instance.updateSelectionFromCoords(
        leftIndex,
        topIndex,
        rightIndex,
        bottomIndex,
        true
      );
    },
    // Add other jspreadsheet options here if needed
  });
  sheet = sheetInstances[0]; // Assuming only one worksheet
  console.log("jspreadsheet initialized.");

  // Initial data load is now handled by the watch effect on props.sheetId
});

onUnmounted(() => {
  console.log("SheetBlock unmounting. Disconnecting Yjs and destroying sheet.");
  if (provider) {
    provider.disconnect();
  }
  if (ydoc) {
    // ydoc.destroy(); // Consider if ydoc should be destroyed or just disconnected
  }
  if (sheet && typeof sheet.destroy === "function") {
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
