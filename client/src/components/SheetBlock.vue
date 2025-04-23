<script>
import { Spreadsheet, Worksheet } from "@jspreadsheet-ce/vue";
import "jsuites/dist/jsuites.css";
import "jspreadsheet-ce/dist/jspreadsheet.css";

export default {
    components: {
        Spreadsheet,
        Worksheet,
    },
}
</script>

<template>
    <Spreadsheet ref="spreadsheet">
        <Worksheet :minDimensions="[100, 100]"/>
    </Spreadsheet>
</template>

<style scoped>
.sheet-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  margin: 0;
  padding: 0;
  border: none;
}

:deep(.handsontable) {
  width: 100% !important;
  height: 100% !important;
  box-shadow: none !important;
  border: none !important;
}

:deep(.ht_master .wtHolder) {
  height: 100% !important;
}
</style>
