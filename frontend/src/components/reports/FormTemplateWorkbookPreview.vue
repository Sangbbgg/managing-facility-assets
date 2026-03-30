<template>
  <n-card class="preview-card" :bordered="false">
    <template #header>
      <div class="preview-header">
        <div>
          <div class="preview-title">템플릿 프리뷰</div>
          <div v-if="template" class="preview-subtitle">
            {{ template.name }} · 실제 워크북 화면으로 표시합니다.
          </div>
          <div v-else class="preview-subtitle">
            왼쪽에서 템플릿을 선택하면 실제 시트 구조를 여기서 볼 수 있습니다.
          </div>
        </div>
      </div>
    </template>

    <n-spin :show="loading">
      <div v-if="template" class="preview-body">
        <div class="sheet-meta">
          <span v-if="sheetNames.length">
            시트 {{ sheetNames.length }}개
          </span>
          <span v-if="activeSheetLabel">
            · 현재 {{ activeSheetLabel }}
          </span>
        </div>

        <div ref="spreadsheetHost" class="sheet-canvas" />
      </div>

      <n-empty
        v-else
        description="왼쪽에서 템플릿을 선택하세요."
        style="padding: 80px 0"
      />
    </n-spin>
  </n-card>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import * as XLSX from 'xlsx'
import jspreadsheet from 'jspreadsheet-ce'
import 'jspreadsheet-ce/dist/jspreadsheet.css'
import 'jsuites/dist/jsuites.css'
import formTemplatesApi from '@/api/formTemplatesApi'

const props = defineProps({
  template: {
    type: Object,
    default: null,
  },
})

const spreadsheetHost = ref(null)
const loading = ref(false)
const workbookInstance = ref(null)
const workbookSummary = ref({ sheetNames: [], activeSheet: null })

const sheetNames = computed(() => workbookSummary.value.sheetNames)
const activeSheetLabel = computed(() => workbookSummary.value.activeSheet)

watch(
  () => props.template?.id,
  async (templateId) => {
    if (!templateId) {
      destroySpreadsheet()
      workbookSummary.value = { sheetNames: [], activeSheet: null }
      return
    }
    await loadWorkbook(templateId)
  },
  { immediate: true },
)

onBeforeUnmount(() => {
  destroySpreadsheet()
})

async function loadWorkbook(templateId) {
  loading.value = true
  try {
    destroySpreadsheet()
    const response = await formTemplatesApi.file(templateId)
    const workbook = XLSX.read(response.data, {
      type: 'array',
      cellStyles: true,
      cellFormula: true,
      cellNF: true,
      cellText: true,
    })
    const worksheets = workbook.SheetNames.map((sheetName) => buildWorksheet(workbook.Sheets[sheetName], sheetName))
    workbookSummary.value = {
      sheetNames: workbook.SheetNames,
      activeSheet: workbook.SheetNames[0] || null,
    }
    await nextTick()
    workbookInstance.value = jspreadsheet(spreadsheetHost.value, {
      worksheets,
      tabs: true,
      toolbar: false,
      contextMenu: false,
      fullscreen: false,
      onopenworksheet: (worksheet) => {
        workbookSummary.value = {
          ...workbookSummary.value,
          activeSheet: worksheet?.options?.worksheetName || null,
        }
      },
    })
  } finally {
    loading.value = false
  }
}

function buildWorksheet(sheet, sheetName) {
  const range = XLSX.utils.decode_range(sheet['!ref'] || 'A1:A1')
  const rowCount = Math.max(range.e.r + 1, 1)
  const colCount = Math.max(range.e.c + 1, 1)
  const data = []
  const style = {}

  for (let rowIndex = 0; rowIndex < rowCount; rowIndex += 1) {
    const row = []
    for (let colIndex = 0; colIndex < colCount; colIndex += 1) {
      const cellAddress = XLSX.utils.encode_cell({ r: rowIndex, c: colIndex })
      const cell = sheet[cellAddress]
      row.push(formatCellValue(cell))
      const css = cellToCss(cell)
      if (css) {
        style[cellAddress] = css
      }
    }
    data.push(row)
  }

  return {
    worksheetName: sheetName,
    data,
    editable: false,
    tableOverflow: true,
    tableWidth: '100%',
    tableHeight: '560px',
    wordWrap: true,
    rowDrag: false,
    rowResize: false,
    columnDrag: false,
    columnResize: true,
    columnSorting: false,
    selectionCopy: false,
    allowInsertColumn: false,
    allowInsertRow: false,
    allowDeleteColumn: false,
    allowDeleteRow: false,
    style,
    columns: buildColumns(sheet, colCount),
    rows: buildRows(sheet, rowCount),
    mergeCells: buildMerges(sheet),
    minDimensions: [colCount, rowCount],
  }
}

function buildColumns(sheet, colCount) {
  return Array.from({ length: colCount }, (_, colIndex) => {
    const source = sheet['!cols']?.[colIndex]
    return {
      title: XLSX.utils.encode_col(colIndex),
      width: resolveColumnWidth(source),
      readOnly: true,
      wordWrap: true,
      type: 'text',
    }
  })
}

function buildRows(sheet, rowCount) {
  return Array.from({ length: rowCount }, (_, rowIndex) => {
    const source = sheet['!rows']?.[rowIndex]
    return {
      title: String(rowIndex + 1),
      height: resolveRowHeight(source),
    }
  })
}

function buildMerges(sheet) {
  const merges = {}
  for (const merge of sheet['!merges'] || []) {
    const cellAddress = XLSX.utils.encode_cell({ r: merge.s.r, c: merge.s.c })
    merges[cellAddress] = [
      merge.e.c - merge.s.c + 1,
      merge.e.r - merge.s.r + 1,
    ]
  }
  return merges
}

function formatCellValue(cell) {
  if (!cell) {
    return ''
  }
  if (cell.w != null) {
    return String(cell.w)
  }
  if (cell.v == null) {
    return ''
  }
  return String(cell.v)
}

function cellToCss(cell) {
  if (!cell?.s) {
    return ''
  }

  const parts = [
    'white-space: pre-wrap',
    'word-break: break-word',
  ]

  const fillColor = normalizeColor(cell.s.fill?.fgColor || cell.s.fill?.bgColor)
  if (fillColor) {
    parts.push(`background-color:${fillColor}`)
  }

  const fontColor = normalizeColor(cell.s.font?.color)
  if (fontColor) {
    parts.push(`color:${fontColor}`)
  }

  if (cell.s.font?.bold) {
    parts.push('font-weight:700')
  }
  if (cell.s.font?.italic) {
    parts.push('font-style:italic')
  }
  if (cell.s.font?.sz) {
    parts.push(`font-size:${Math.max(Math.round(cell.s.font.sz), 11)}px`)
  }
  if (cell.s.alignment?.horizontal) {
    parts.push(`text-align:${cell.s.alignment.horizontal}`)
  }
  if (cell.s.alignment?.vertical) {
    parts.push(`vertical-align:${cell.s.alignment.vertical}`)
  }

  const border = buildBorderCss(cell.s.border)
  if (border) {
    parts.push(border)
  }

  return parts.join(';')
}

function buildBorderCss(border) {
  if (!border) {
    return ''
  }

  const color = normalizeColor(
    border.top?.color
    || border.bottom?.color
    || border.left?.color
    || border.right?.color,
  ) || '#cbd5e1'

  const segments = []
  if (border.top?.style) {
    segments.push(`border-top:1px solid ${color}`)
  }
  if (border.bottom?.style) {
    segments.push(`border-bottom:1px solid ${color}`)
  }
  if (border.left?.style) {
    segments.push(`border-left:1px solid ${color}`)
  }
  if (border.right?.style) {
    segments.push(`border-right:1px solid ${color}`)
  }
  return segments.join(';')
}

function normalizeColor(color) {
  if (!color) {
    return ''
  }
  if (typeof color === 'string') {
    return color.startsWith('#') ? color : `#${color.slice(-6)}`
  }
  if (color.rgb) {
    return `#${String(color.rgb).slice(-6)}`
  }
  return ''
}

function resolveColumnWidth(col) {
  if (!col) {
    return 96
  }
  if (col.wpx) {
    return Math.max(col.wpx, 64)
  }
  if (col.width) {
    return Math.max(Math.round(col.width * 7.5), 64)
  }
  if (col.wch) {
    return Math.max(Math.round(col.wch * 8), 64)
  }
  return 96
}

function resolveRowHeight(row) {
  if (!row) {
    return 24
  }
  if (row.hpx) {
    return Math.max(row.hpx, 24)
  }
  if (row.hpt) {
    return Math.max(Math.round(row.hpt * 1.33), 24)
  }
  return 24
}

function destroySpreadsheet() {
  if (workbookInstance.value?.destroy) {
    workbookInstance.value.destroy()
  } else if (spreadsheetHost.value) {
    spreadsheetHost.value.innerHTML = ''
  }
  workbookInstance.value = null
}
</script>

<style scoped>
.preview-card {
  min-height: 100%;
  background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
}

.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.preview-title {
  font-size: 18px;
  font-weight: 700;
  color: #0f172a;
}

.preview-subtitle {
  margin-top: 4px;
  font-size: 13px;
  color: #64748b;
}

.preview-body {
  display: grid;
  gap: 12px;
}

.sheet-meta {
  font-size: 12px;
  color: #64748b;
}

.sheet-canvas {
  overflow: hidden;
  border: 1px solid #dbe4ee;
  border-radius: 12px;
  background:
    linear-gradient(180deg, rgba(226, 232, 240, 0.35), rgba(255, 255, 255, 0)) 0 0 / 100% 52px no-repeat,
    #f8fafc;
  padding: 12px;
  min-height: 600px;
}

.sheet-canvas :deep(.jss_container) {
  border: 1px solid #dbe4ee;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 18px 48px rgba(15, 23, 42, 0.08);
}

.sheet-canvas :deep(.jss_tabs) {
  background: #f8fafc;
}

.sheet-canvas :deep(.jss_tab) {
  font-size: 13px;
}

.sheet-canvas :deep(td) {
  font-family: 'Malgun Gothic', sans-serif;
}
</style>
