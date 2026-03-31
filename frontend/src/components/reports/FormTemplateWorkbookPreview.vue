<template>
  <n-card class="preview-card" :bordered="false">
    <template #header>
      <div class="preview-header">
        <div>
          <div class="preview-title">템플릿 프리뷰</div>
          <div v-if="template" class="preview-subtitle">
            {{ template.name }} · 셀을 클릭해 실제 DB 필드를 매핑할 수 있습니다.
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
          <span v-if="sheetNames.length">시트 {{ sheetNames.length }}개</span>
          <span v-if="activeSheetLabel"> · 현재 {{ activeSheetLabel }}</span>
          <span v-if="selectedCellLabel"> · 선택 {{ selectedCellLabel }}</span>
          <span v-if="selectionGuide"> · {{ selectionGuide }}</span>
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
  mappings: {
    type: Array,
    default: () => [],
  },
  selectedCell: {
    type: Object,
    default: null,
  },
  selectionMode: {
    type: String,
    default: 'cell',
  },
  selectedRowRange: {
    type: Object,
    default: null,
  },
  selectedColRange: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['select-cell', 'select-row-range', 'select-col-range'])

const spreadsheetHost = ref(null)
const loading = ref(false)
const workbookInstance = ref(null)
const workbookBinary = ref(null)
const workbookSummary = ref({ sheetNames: [], activeSheet: null })
const pendingUserSelection = ref(false)

const sheetNames = computed(() => workbookSummary.value.sheetNames)
const activeSheetLabel = computed(() => workbookSummary.value.activeSheet)
const selectedCellLabel = computed(() => {
  if (!props.selectedCell?.cell) {
    return ''
  }
  return props.selectedCell.sheetName
    ? `${props.selectedCell.sheetName} / ${props.selectedCell.cell}`
    : props.selectedCell.cell
})
const selectionGuide = computed(() => {
  if (props.selectionMode === 'row-range') {
    return '행 범위 선택 중: 워크북에서 시작 행부터 마지막 행까지 드래그하세요.'
  }
  if (props.selectionMode === 'col-range') {
    return '열 범위 선택 중: 워크북에서 양식 시작 열부터 마지막 열까지 드래그하세요.'
  }
  return ''
})

watch(
  () => props.template?.id,
  async (templateId) => {
    if (!templateId) {
      destroySpreadsheet()
      workbookBinary.value = null
      workbookSummary.value = { sheetNames: [], activeSheet: null }
      return
    }
    await loadWorkbook(templateId)
  },
  { immediate: true },
)

watch(
  () => [
    props.mappings.map((item) => `${item.sheet_name || ''}:${item.cell}:${item.field}:${item.data_source}`).join('|'),
  ],
  async () => {
    if (!workbookBinary.value || !props.template?.id) {
      return
    }
    await renderWorkbook()
  },
)

watch(
  () => [
    props.selectedCell?.sheetName || '',
    props.selectedCell?.cell || '',
  ],
  async () => {
    // Keep the current worksheet stable while mapping and range-selection state changes.
    // We only mirror the active worksheet label here instead of rebuilding jspreadsheet.
    const currentSheetName = resolveCurrentSheetName()
    if (currentSheetName) {
      workbookSummary.value = {
        ...workbookSummary.value,
        activeSheet: currentSheetName,
      }
    } else if (props.selectedCell?.sheetName) {
      workbookSummary.value = {
        ...workbookSummary.value,
        activeSheet: props.selectedCell.sheetName,
      }
    }
  },
)

onBeforeUnmount(() => {
  detachPointerIntent()
  destroySpreadsheet()
})

async function loadWorkbook(templateId) {
  loading.value = true
  try {
    const response = await formTemplatesApi.file(templateId)
    workbookBinary.value = response.data
    await renderWorkbook()
  } finally {
    loading.value = false
  }
}

async function renderWorkbook() {
  if (!workbookBinary.value) {
    return
  }

  destroySpreadsheet()
  const workbook = XLSX.read(workbookBinary.value, {
    type: 'array',
    cellStyles: true,
    cellFormula: true,
    cellNF: true,
    cellText: true,
  })

  const worksheets = workbook.SheetNames.map((sheetName) =>
    buildWorksheet(workbook.Sheets[sheetName], sheetName),
  )
  const preferredSheetName = resolvePreferredSheetName(workbook.SheetNames)

  workbookSummary.value = {
    sheetNames: workbook.SheetNames,
    activeSheet: preferredSheetName,
  }

  await nextTick()
  attachPointerIntent()
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
    onselection: (worksheet, x1, y1, x2, y2) => {
      if (!pendingUserSelection.value) {
        return
      }
      pendingUserSelection.value = false
      const sheetName = resolveCurrentSheetName(worksheet) || workbookSummary.value.activeSheet
      const startCol = Math.min(x1, x2 ?? x1)
      const endCol = Math.max(x1, x2 ?? x1)
      const startRow = Math.min(y1, y2 ?? y1)
      const endRow = Math.max(y1, y2 ?? y1)
      if (props.selectionMode === 'row-range') {
        emit('select-row-range', {
          sheetName,
          startRow: startRow + 1,
          endRow: endRow + 1,
        })
        return
      }
      if (props.selectionMode === 'col-range') {
        emit('select-col-range', {
          sheetName,
          startCol: XLSX.utils.encode_col(startCol),
          endCol: XLSX.utils.encode_col(endCol),
        })
        return
      }
      const cell = XLSX.utils.encode_cell({ r: y1, c: x1 })
      emit('select-cell', { sheetName, cell })
    },
  })
  await nextTick()
  const activeSheetIndex = workbook.SheetNames.findIndex((sheetName) => sheetName === preferredSheetName)
  if (activeSheetIndex > 0) {
    const spreadsheet = spreadsheetHost.value?.spreadsheet
    if (spreadsheet?.openWorksheet) {
      spreadsheet.openWorksheet(activeSheetIndex)
    }
  }
}

function resolvePreferredSheetName(sheetNames) {
  const currentSheet = resolveCurrentSheetName()
  if (currentSheet && sheetNames.includes(currentSheet)) {
    return currentSheet
  }
  if (props.selectedCell?.sheetName && sheetNames.includes(props.selectedCell.sheetName)) {
    return props.selectedCell.sheetName
  }
  if (workbookSummary.value.activeSheet && sheetNames.includes(workbookSummary.value.activeSheet)) {
    return workbookSummary.value.activeSheet
  }
  return sheetNames[0] || null
}

function resolveCurrentSheetName(worksheet = null) {
  if (worksheet?.options?.worksheetName) {
    return worksheet.options.worksheetName
  }
  const spreadsheet = spreadsheetHost.value?.spreadsheet
  const activeIndex = spreadsheet?.getWorksheetActive?.()
  if (Number.isInteger(activeIndex) && activeIndex >= 0) {
    return spreadsheet?.worksheets?.[activeIndex]?.options?.worksheetName || null
  }
  return workbookSummary.value.activeSheet || null
}

function buildWorksheet(sheet, sheetName) {
  const range = XLSX.utils.decode_range(sheet['!ref'] || 'A1:A1')
  const rowCount = Math.max(range.e.r + 1, 1)
  const colCount = Math.max(range.e.c + 1, 1)
  const data = []
  const style = {}
  const mappedCells = new Set(
    props.mappings
      .filter((item) => (item.sheet_name || '') === sheetName)
      .map((item) => item.cell),
  )

  for (let rowIndex = 0; rowIndex < rowCount; rowIndex += 1) {
    const row = []
    for (let colIndex = 0; colIndex < colCount; colIndex += 1) {
      const cellAddress = XLSX.utils.encode_cell({ r: rowIndex, c: colIndex })
      const cell = sheet[cellAddress]
      row.push(formatCellValue(cell))

      const cssParts = []
      const cellCss = cellToCss(cell)
      if (cellCss) {
        cssParts.push(cellCss)
      }
      if (mappedCells.has(cellAddress)) {
        cssParts.push('box-shadow: inset 0 0 0 2px #22c55e')
        cssParts.push('background-image: linear-gradient(180deg, rgba(34, 197, 94, 0.08), rgba(34, 197, 94, 0.02))')
      }
      if (
        props.selectedCell?.sheetName === sheetName
        && props.selectedCell?.cell === cellAddress
      ) {
        cssParts.push('box-shadow: inset 0 0 0 2px #2563eb')
        cssParts.push('background-image: linear-gradient(180deg, rgba(37, 99, 235, 0.12), rgba(37, 99, 235, 0.04))')
      }
      if (
        props.selectedRowRange?.sheetName === sheetName
        && props.selectedRowRange?.startRow
        && props.selectedRowRange?.endRow
        && rowIndex + 1 >= props.selectedRowRange.startRow
        && rowIndex + 1 <= props.selectedRowRange.endRow
      ) {
        cssParts.push('box-shadow: inset 0 0 0 1px rgba(245, 158, 11, 0.95)')
        cssParts.push('background-image: linear-gradient(180deg, rgba(245, 158, 11, 0.14), rgba(245, 158, 11, 0.05))')
      }
      if (
        props.selectedColRange?.sheetName === sheetName
        && props.selectedColRange?.startCol
        && props.selectedColRange?.endCol
      ) {
        const startIndex = XLSX.utils.decode_col(props.selectedColRange.startCol)
        const endIndex = XLSX.utils.decode_col(props.selectedColRange.endCol)
        if (colIndex >= startIndex && colIndex <= endIndex) {
          cssParts.push('box-shadow: inset 0 0 0 1px rgba(168, 85, 247, 0.95)')
          cssParts.push('background-image: linear-gradient(180deg, rgba(168, 85, 247, 0.14), rgba(168, 85, 247, 0.05))')
        }
      }
      if (cssParts.length) {
        style[cellAddress] = cssParts.join(';')
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
  const style = cell.s

  const fillColor = normalizeColor(style.fill?.fgColor || style.fill?.bgColor)
  if (fillColor) {
    parts.push(`background-color:${fillColor}`)
  }

  const fontColor = normalizeColor(style.font?.color)
  if (fontColor) {
    parts.push(`color:${fontColor}`)
  }

  if (style.font?.name) {
    parts.push(`font-family:${normalizeFontFamily(style.font.name)}`)
  }
  if (style.font?.bold) {
    parts.push('font-weight:700')
  }
  if (style.font?.italic) {
    parts.push('font-style:italic')
  }
  const textDecorations = []
  if (style.font?.underline) {
    textDecorations.push('underline')
  }
  if (style.font?.strike) {
    textDecorations.push('line-through')
  }
  if (textDecorations.length) {
    parts.push(`text-decoration:${textDecorations.join(' ')}`)
  }
  if (style.font?.sz) {
    parts.push(`font-size:${Math.max(Math.round(style.font.sz), 11)}px`)
  }

  if (style.alignment?.horizontal) {
    parts.push(`text-align:${normalizeHorizontalAlign(style.alignment.horizontal)}`)
  }
  if (style.alignment?.vertical) {
    parts.push(`vertical-align:${normalizeVerticalAlign(style.alignment.vertical)}`)
  }
  if (style.alignment?.wrapText) {
    parts.push('white-space:pre-wrap')
  } else {
    parts.push('white-space:nowrap')
  }
  if (style.alignment?.textRotation != null && Number(style.alignment.textRotation) !== 0) {
    parts.push(`transform:rotate(${normalizeRotation(style.alignment.textRotation)}deg)`)
    parts.push('transform-origin:center center')
  }
  if (style.alignment?.indent) {
    parts.push(`padding-left:${8 + Number(style.alignment.indent) * 10}px`)
  }

  const border = buildBorderCss(style.border)
  if (border) {
    parts.push(border)
  }

  return parts.join(';')
}

function buildBorderCss(border) {
  if (!border) {
    return ''
  }
  const segments = []
  pushBorderSegment(segments, 'top', border.top)
  pushBorderSegment(segments, 'bottom', border.bottom)
  pushBorderSegment(segments, 'left', border.left)
  pushBorderSegment(segments, 'right', border.right)
  return segments.join(';')
}

function pushBorderSegment(segments, side, borderPart) {
  if (!borderPart?.style) {
    return
  }
  const color = normalizeColor(borderPart.color) || '#94a3b8'
  const { width, style } = mapBorderStyle(borderPart.style)
  segments.push(`border-${side}:${width}px ${style} ${color}`)
}

function mapBorderStyle(style) {
  switch (style) {
    case 'medium':
      return { width: 2, style: 'solid' }
    case 'thick':
      return { width: 3, style: 'solid' }
    case 'dashed':
    case 'mediumDashed':
      return { width: 1, style: 'dashed' }
    case 'dotted':
      return { width: 1, style: 'dotted' }
    case 'double':
      return { width: 3, style: 'double' }
    case 'hair':
      return { width: 1, style: 'dotted' }
    case 'slantDashDot':
    case 'dashDot':
    case 'mediumDashDot':
    case 'dashDotDot':
    case 'mediumDashDotDot':
      return { width: 1, style: 'dashed' }
    default:
      return { width: 1, style: 'solid' }
  }
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

function normalizeFontFamily(name) {
  return `'${String(name).replace(/'/g, "\\'")}', 'Malgun Gothic', sans-serif`
}

function normalizeHorizontalAlign(value) {
  if (value === 'centerContinuous' || value === 'distributed') {
    return 'center'
  }
  if (value === 'fill' || value === 'justify') {
    return 'justify'
  }
  return value
}

function normalizeVerticalAlign(value) {
  if (value === 'center' || value === 'distributed' || value === 'justify') {
    return 'middle'
  }
  return value
}

function normalizeRotation(value) {
  const number = Number(value)
  if (Number.isNaN(number)) {
    return 0
  }
  if (number > 90) {
    return number - 180
  }
  return number
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
  pendingUserSelection.value = false
  detachPointerIntent()
  if (workbookInstance.value?.destroy) {
    workbookInstance.value.destroy()
  } else if (spreadsheetHost.value) {
    spreadsheetHost.value.innerHTML = ''
  }
  workbookInstance.value = null
}

function handlePointerIntent() {
  pendingUserSelection.value = true
}

function attachPointerIntent() {
  if (!spreadsheetHost.value) {
    return
  }
  spreadsheetHost.value.addEventListener('pointerdown', handlePointerIntent)
}

function detachPointerIntent() {
  if (!spreadsheetHost.value) {
    return
  }
  spreadsheetHost.value.removeEventListener('pointerdown', handlePointerIntent)
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
