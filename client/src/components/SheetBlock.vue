<template>
  <div id="spreadsheet"></div>
</template>

<script>
import { defineComponent } from "vue";
import jspreadsheet from "jspreadsheet-ce";
import "jspreadsheet-ce/dist/jspreadsheet.css";
import * as Y from "yjs";
import { WebsocketProvider } from "y-websocket";

export default defineComponent({
  name: "LiveSpreadsheet",
  mounted() {
    // 1. Yjs + WebSocket setup
    const ydoc     = new Y.Doc();
    new WebsocketProvider("ws://localhost:1234", "demo-room", ydoc);
    const ycells   = ydoc.getMap("cells");
    let applyingRemote = false;

    // 2. Create sheet with a 100×100 minimum
    const defaultCol = { type: "text", title: "", width: 100 };
    const sheets = jspreadsheet(document.getElementById("spreadsheet"), {
      worksheets: [
        {
          data: [],               // start empty
          minDimensions: [100,100]
        }
      ],
      onchange: (instance, cell, x, y, newValue, oldValue) => {
        if (applyingRemote) return;
        if (newValue !== oldValue) {
          // wrap in a single transaction so remote peers see a batch if you group sets
          ydoc.transact(() => {
            ycells.set(`${x},${y}`, newValue);
          });
        }
      },
    });
    const sheet = sheets[0];

    // 3. Observe **all** remote changes at once
    ycells.observe(event => {
      // ignore our own local writes
      if (event.transaction.local) return;
      applyingRemote = true;

      // collect {col,row,val} for every changed key
      const updates = Array.from(event.keysChanged).map(key => {
        const [col, row] = key.split(",").map(Number);
        return { col, row, val: ycells.get(key) };
      });

      // determine current grid size
      const data      = sheet.getData();                     
      let currentW    = data[0].length;
      let currentH    = data.length;

      // find the furthest-out cell in this batch
      const maxCol = Math.max(...updates.map(u => u.col), currentW - 1);
      const maxRow = Math.max(...updates.map(u => u.row), currentH - 1);

      // 4. Expand columns if needed
      if (maxCol >= currentW) {
        const addCols = maxCol - currentW + 1;
        for (let i = 0; i < addCols; i++) {
          sheet.insertColumn(
            [],                   // no initial data
            currentW + i,         // at the end
            false,                // insert *after* the reference index
            defaultCol
          );                     
        }
        currentW += addCols;
      }

      // 5. Expand rows if needed
      if (maxRow >= currentH) {
        const addRows = maxRow - currentH + 1;
        sheet.insertRow(addRows); // adds blank rows at bottom :contentReference[oaicite:2]{index=2}
        currentH += addRows;
      }

      // 6. Finally, apply every cell update
      updates.forEach(({ col, row, val }) => {
        sheet.setValueFromCoords(col, row, val);
      });

      applyingRemote = false;
    });
  }
});
</script>
