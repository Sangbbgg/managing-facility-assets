<template>
  <div class="preview-panel">
    <div class="preview-header">
      <div v-if="workbookName" class="preview-subtitle">
        {{ workbookName }} 기준으로 실제 데이터가 채워진 결과를 표시합니다.
      </div>
      <div v-else class="preview-subtitle">
        양식과 자산을 선택한 뒤 `미리보기`를 누르면 작성된 워크북이 여기 표시됩니다.
      </div>
    </div>

    <n-spin :show="store.loading">
      <div v-if="hasWorkbook" class="preview-body">
        <div class="sheet-meta">
          <span v-if="sheetNames.length">시트 {{ sheetNames.length }}개</span>
          <span v-if="activeSheetLabel"> / 현재 {{ activeSheetLabel }}</span>
        </div>

        <div ref="spreadsheetViewport" class="sheet-canvas">
          <div ref="spreadsheetHost" class="sheet-host" />
        </div>
      </div>

      <n-empty
        v-else
        :description="emptyDescription"
        style="padding: 80px 0"
      />
    </n-spin>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as XLSX from 'xlsx'
import jspreadsheet from 'jspreadsheet-ce'
import 'jspreadsheet-ce/dist/jspreadsheet.css'
import 'jsuites/dist/jsuites.css'
import { useFormTemplateStore } from '@/stores/formTemplateStore'

let resizeTimer = null
let viewportObserver = null
let isRendering = false
let lastViewportSize = { width: 0, height: 0 }

const store = useFormTemplateStore()

const spreadsheetViewport = ref(null)
const spreadsheetHost = ref(null)
const workbookInstance = ref(null)
const workbookSummary = ref({ sheetNames: [], activeSheet: null })

const workbookBinary = computed(() => store.previewWorkbookBinary)
const workbookName = computed(() => store.previewWorkbookName)
const hasWorkbook = computed(() => !!workbookBinary.value)
const sheetNames = computed(() => workbookSummary.value.sheetNames || [])
const activeSheetLabel = computed(() => workbookSummary.value.activeSheet || '')
const emptyDescription = computed(() => (
  store.loading
    ? '미리보기를 불러오는 중입니다.'
    : '양식과 자산을 선택하고 미리보기를 실행해 주세요.'
))

onMounted(() => {
  window.addEventListener('resize', handleWindowResize)
})

watch(
  spreadsheetViewport,
  (element) => {
    disconnectViewportObserver()
    if (!element || typeof ResizeObserver === 'undefined') {
      return
    }
    viewportObserver = new ResizeObserver(() => {
      queueWorkbookRender()
    })
    viewportObserver.observe(element)
  },
  { flush: 'post' },
)

watch(
  workbookBinary,
  async (binary) => {
    if (!binary) {
      destroySpreadsheet()
      workbookSummary.value = { sheetNames: [], activeSheet: null }
      lastViewportSize = { width: 0, height: 0 }
      return
    }
    await renderWorkbook(binary)
  },
  { immediate: true },
)

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleWindowResize)
  if (resizeTimer) {
    window.clearTimeout(resizeTimer)
  }
  disconnectViewportObserver()
  destroySpreadsheet()
})

async function renderWorkbook(binary) {
  if (isRendering) {
    return
  }
  isRendering = true
  try {
    destroySpreadsheet()
    const workbook = XLSX.read(binary, {
      type: 'array',
      cellStyles: true,
      cellFormula: true,
      cellNF: true,
      cellText: true,
    })

    const viewportSize = resolveViewportSize()
    const viewportHeight = resolveViewportHeight(viewportSize.height)
    const worksheets = workbook.SheetNames.map((sheetName) =>
      buildWorksheet(workbook.Sheets[sheetName], sheetName, viewportHeight),
    )

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
        resetPreviewScroll()
      },
    })
    resetPreviewScroll()
    lastViewportSize = viewportSize
  } finally {
    isRendering = false
  }
}

function buildWorksheet(sheet, sheetName, viewportHeight) {
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

      const cellCss = cellToCss(cell)
      if (cellCss) {
        style[cellAddress] = cellCss
      }
    }
    data.push(row)
  }

  return {
    worksheetName: sheetName,
    data,
    editable: false,
    tableOverflow: true,
    tableHeight: `${viewportHeight}px`,
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
  if (!cell) return ''
  if (cell.w != null) return String(cell.w)
  if (cell.v == null) return ''
  return String(cell.v)
}

function cellToCss(cell) {
  if (!cell?.s) return ''

  const parts = [
    'white-space: pre-wrap',
    'word-break: break-word',
  ]
  const style = cell.s

  const fillColor = normalizeColor(style.fill?.fgColor || style.fill?.bgColor)
  if (fillColor) parts.push(`background-color:${fillColor}`)

  const fontColor = normalizeColor(style.font?.color)
  if (fontColor) parts.push(`color:${fontColor}`)

  if (style.font?.name) parts.push(`font-family:${normalizeFontFamily(style.font.name)}`)
  if (style.font?.bold) parts.push('font-weight:700')
  if (style.font?.italic) parts.push('font-style:italic')

  const textDecorations = []
  if (style.font?.underline) textDecorations.push('underline')
  if (style.font?.strike) textDecorations.push('line-through')
  if (textDecorations.length) parts.push(`text-decoration:${textDecorations.join(' ')}`)
  if (style.font?.sz) parts.push(`font-size:${Math.max(Math.round(style.font.sz), 11)}px`)

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

  const border = buildBorderCss(style.border)
  if (border) parts.push(border)

  return parts.join(';')
}

function buildBorderCss(border) {
  if (!border) return ''
  const segments = []
  pushBorderSegment(segments, 'top', border.top)
  pushBorderSegment(segments, 'bottom', border.bottom)
  pushBorderSegment(segments, 'left', border.left)
  pushBorderSegment(segments, 'right', border.right)
  return segments.join(';')
}

function pushBorderSegment(segments, side, borderPart) {
  if (!borderPart?.style) return
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
    default:
      return { width: 1, style: 'solid' }
  }
}

function normalizeColor(color) {
  if (!color) return ''
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
  switch (value) {
    case 'centerContinuous':
    case 'distributed':
      return 'center'
    default:
      return value
  }
}

function normalizeVerticalAlign(value) {
  switch (value) {
    case 'center':
    case 'distributed':
      return 'middle'
    default:
      return value
  }
}

function resolveColumnWidth(source) {
  if (source?.wpx) return Math.max(Math.round(source.wpx), 72)
  if (source?.wch) return Math.max(Math.round(source.wch * 8), 72)
  return 96
}

function resolveRowHeight(source) {
  if (source?.hpx) return Math.max(Math.round(source.hpx), 24)
  if (source?.hpt) return Math.max(Math.round(source.hpt * 1.33), 24)
  return 24
}

function resolveViewportSize() {
  return {
    width: spreadsheetViewport.value?.clientWidth || 0,
    height: spreadsheetViewport.value?.clientHeight || 520,
  }
}

function resolveViewportHeight(height) {
  return Math.max(height - 64, 260)
}

function destroySpreadsheet() {
  if (workbookInstance.value?.destroy) {
    workbookInstance.value.destroy()
  }
  workbookInstance.value = null
  if (spreadsheetHost.value) {
    spreadsheetHost.value.innerHTML = ''
  }
}

function disconnectViewportObserver() {
  if (viewportObserver) {
    viewportObserver.disconnect()
    viewportObserver = null
  }
}

function resetPreviewScroll() {
  if (!spreadsheetHost.value) {
    return
  }
  for (const element of spreadsheetHost.value.querySelectorAll('.jss_content')) {
    element.scrollLeft = 0
    element.scrollTop = 0
  }
}

function handleWindowResize() {
  queueWorkbookRender()
}

function queueWorkbookRender() {
  if (!workbookBinary.value) {
    return
  }
  const nextViewportSize = resolveViewportSize()
  if (nextViewportSize.width <= 0 || nextViewportSize.height <= 0) {
    return
  }
  if (
    Math.abs(nextViewportSize.width - lastViewportSize.width) < 2 &&
    Math.abs(nextViewportSize.height - lastViewportSize.height) < 2
  ) {
    return
  }
  if (resizeTimer) {
    window.clearTimeout(resizeTimer)
  }
  resizeTimer = window.setTimeout(() => {
    resizeTimer = null
    renderWorkbook(workbookBinary.value)
  }, 120)
}
</script>

<style scoped>
.preview-panel {
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.preview-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 12px;
}

.preview-subtitle {
  font-size: 13px;
  color: #64748b;
}

.preview-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 0;
  flex: 1;
}

.sheet-meta {
  font-size: 13px;
  color: #475569;
}

.sheet-canvas {
  min-height: 0;
  flex: 1;
  overflow-x: auto;
  overflow-y: hidden;
  border: 1px solid #dbe3f0;
  border-radius: 12px;
  background: #fff;
  padding: 12px;
}

.sheet-host {
  height: 100%;
  min-height: 0;
  width: max-content;
  min-width: 100%;
}

.sheet-host :deep(.jtabs) {
  width: max-content;
  min-width: 100%;
}

.sheet-host :deep(.jss_content) {
  width: max-content !important;
  min-width: 100% !important;
  overflow-x: hidden !important;
  overflow-y: auto !important;
}

.sheet-host :deep(.jss_worksheet td),
.sheet-host :deep(.jss_worksheet th) {
  font-family: 'Malgun Gothic', sans-serif;
}
</style>
