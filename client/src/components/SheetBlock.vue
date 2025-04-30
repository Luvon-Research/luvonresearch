<template>
  <div id="spreadsheet"></div>
</template>

<script>
import { defineComponent } from 'vue';
import jspreadsheet from 'jspreadsheet-ce';
import 'jspreadsheet-ce/dist/jspreadsheet.css';
import * as Y from 'yjs';
import { WebsocketProvider } from 'y-websocket';

export default defineComponent({
  name: 'LiveSpreadsheet',
  mounted() {
    // 1. Yjs setup
    const ydoc     = new Y.Doc();
    const provider = new WebsocketProvider('ws://localhost:1234', 'demo-room', ydoc);
    const yarray   = ydoc.getArray('cells');

    // 2. Initial grid data
    const initial = yarray.length
      ? yarray.toArray()
      : Array.from({ length: 10 }, () => Array(10).fill(''));

    // 3. Create a spreadsheet with ONE worksheet
    const sheets = jspreadsheet(document.getElementById('spreadsheet'), {
      // common spreadsheet options (toolbar, etc) go here if you like
      worksheets: [
        {
          data: initial,
          minDimensions: [100, 100],
          columns: Array(10).fill({ type: 'text', title: '', width: 100 })
        }
      ],
      // this onchange applies to *all* worksheets
      onchange: (instance) => {
        const d = instance.getData();
        yarray.delete(0, yarray.length);
        yarray.insert(0, d);
      }
    });

    // grab the first (and only) sheet instance
    const sheet = sheets[0];

    // 4. Remote updates -> push into the sheet
    yarray.observe(() => {
      sheet.setData(yarray.toArray());
    });
  }
});
</script>
