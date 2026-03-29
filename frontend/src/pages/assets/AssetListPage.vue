<template>
  <PageShell title="자산 현황">
    <n-space justify="space-between" style="margin-bottom: 12px;" wrap>
      <n-space wrap align="center">
        <LayoutSelector :columns="activeColumns" page-key="asset_list" @apply="onLayoutApply" />
        <ColumnConfigPopover
          :columns="activeColumns"
          :default-columns="DEFAULT_COLUMNS"
          @update:columns="onColumnsUpdate"
        />
        <n-text depth="3" style="font-size: 12px;">
          {{ visibleCount }}개 컬럼 표시 / 전체 {{ assets.length }}건
        </n-text>
      </n-space>

      <n-space wrap align="center">
        <n-select v-model:value="searchField" :options="searchFieldOptions" style="width: 150px;" size="small" />
        <n-input
          v-model:value="search"
          placeholder="검색어 입력"
          clearable
          style="width: 200px;"
          size="small"
        />
        <n-select
          v-model:value="filterStatus"
          :options="statusOptions"
          clearable
          placeholder="상태 필터"
          style="width: 110px;"
          size="small"
        />
        <n-text depth="3" style="font-size: 12px;">
          {{ filteredAssets.length }}건
        </n-text>
      </n-space>
    </n-space>

    <n-text depth="3" style="font-size: 11px; display: block; margin-bottom: 6px;">
      각 컬럼 헤더를 드래그하면 순서를 변경할 수 있습니다
    </n-text>
    <ListHeader title="자산 목록" :count="filteredAssets.length" />

    <div :style="{ overflowY: 'auto', maxHeight: `${tableMaxHeight}px` }">
      <div
        ref="topScrollRef"
        style="overflow-x: auto; overflow-y: hidden; height: 14px; position: sticky; top: 0; z-index: 3; background: var(--n-color, #fff); border-top: 1px solid #e0e0e6; border-bottom: 1px solid #e0e0e6;"
        @scroll.passive="onTopScroll"
      >
        <div :style="{ width: `${scrollContentWidth}px`, height: '1px' }"></div>
      </div>

      <div ref="tableHostRef">
        <n-data-table
          :columns="tableColumns"
          :data="filteredAssets"
          :loading="loading"
          :row-key="(row) => row.id"
          :row-props="rowProps"
          :scroll-x="scrollContentWidth"
          striped
          size="small"
        />
      </div>
    </div>
  </PageShell>
</template>

<script setup>
import { computed, h, nextTick, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { NTag } from 'naive-ui'

import client from '@/api/client'
import ColumnConfigPopover from '@/components/assets/ColumnConfigPopover.vue'
import LayoutSelector from '@/components/assets/LayoutSelector.vue'
import ListHeader from '@/components/common/ListHeader.vue'
import PageShell from '@/components/common/PageShell.vue'

const router = useRouter()
const loading = ref(false)
const assets = ref([])

async function fetchAssets() {
  loading.value = true
  try {
    const response = await client.get('/api/assets/enriched')
    assets.value = response.data
  } finally {
    loading.value = false
  }
}

const DEFAULT_COLUMNS = [
  { key: 'asset_code', label: '자산코드', width: 145, visible: true },
  { key: 'asset_name', label: '설비명', width: 160, visible: true },
  { key: 'importance', label: '중요도', width: 65, visible: true },
  { key: 'status', label: '상태', width: 85, visible: true },
  { key: 'group_name', label: '그룹', width: 110, visible: true },
  { key: 'location_full_path', label: '위치', width: 180, visible: true },
  { key: 'equipment_type_name', label: '장비종류', width: 120, visible: true },
  { key: 'os_name', label: 'OS', width: 155, visible: true },
  { key: 'av_name', label: '백신', width: 130, visible: true },
  { key: 'ip_address', label: 'IP 주소', width: 120, visible: true },
  { key: 'install_date', label: '설치일', width: 95, visible: true },
  { key: 'model_name', label: '모델명', width: 150, visible: false },
  { key: 'serial_number', label: '시리얼번호', width: 140, visible: false },
  { key: 'purpose', label: '용도', width: 150, visible: false },
  { key: 'group_full_path', label: '그룹 경로', width: 210, visible: false },
  { key: 'group_code', label: '그룹코드', width: 95, visible: false },
  { key: 'location_name', label: '위치명', width: 120, visible: false },
  { key: 'equipment_type_code', label: '장비코드', width: 90, visible: false },
  { key: 'os_version', label: 'OS버전', width: 120, visible: false },
  { key: 'os_eol_date', label: 'OS EoL', width: 95, visible: false },
  { key: 'os_extended_eol', label: 'OS 연장EoL', width: 105, visible: false },
  { key: 'av_version', label: '백신버전', width: 115, visible: false },
  { key: 'av_support_end', label: '백신지원종료', width: 115, visible: false },
  { key: 'manager_name', label: '담당자', width: 90, visible: false },
  { key: 'manager_title', label: '담당자 직급', width: 100, visible: false },
  { key: 'manager_contact', label: '담당자 연락처', width: 130, visible: false },
  { key: 'last_collected_at', label: '최근수집일', width: 115, visible: false },
  { key: 'created_at', label: '등록일', width: 95, visible: false },
  { key: 'updated_at', label: '최종수정일', width: 115, visible: false },
]

const activeColumns = ref(DEFAULT_COLUMNS.map((column) => ({ ...column })))
const visibleCount = computed(() => activeColumns.value.filter((column) => column.visible).length)

function onLayoutApply(columnsJson) {
  if (!Array.isArray(columnsJson)) return
  const keyMap = Object.fromEntries(columnsJson.map((column) => [column.key, column]))
  activeColumns.value = DEFAULT_COLUMNS.map((column) => ({
    ...column,
    visible: keyMap[column.key] !== undefined ? keyMap[column.key].visible : column.visible,
    width: keyMap[column.key]?.width ?? column.width,
  }))
}

function onColumnsUpdate(columns) {
  activeColumns.value = columns
}

const STATUS_LABELS = {
  OPERATING: '운영중',
  MAINTENANCE: '점검중',
  FAULTY: '고장',
  DISPOSED: '폐기',
}

const STATUS_TYPES = {
  OPERATING: 'success',
  MAINTENANCE: 'warning',
  FAULTY: 'error',
  DISPOSED: 'default',
}

const statusOptions = [
  { label: '운영중', value: 'OPERATING' },
  { label: '점검중', value: 'MAINTENANCE' },
  { label: '고장', value: 'FAULTY' },
  { label: '폐기', value: 'DISPOSED' },
]

const search = ref('')
const filterStatus = ref(null)
const searchField = ref('__all__')

const searchFieldOptions = computed(() => [
  { label: '전체 컬럼', value: '__all__' },
  ...activeColumns.value.filter((column) => column.visible).map((column) => ({ label: column.label, value: column.key })),
])

const filteredAssets = computed(() => {
  let data = assets.value
  if (filterStatus.value) {
    data = data.filter((asset) => asset.status === filterStatus.value)
  }
  if (search.value.trim()) {
    const query = search.value.trim().toLowerCase()
    if (searchField.value === '__all__') {
      const visibleKeys = activeColumns.value.filter((column) => column.visible).map((column) => column.key)
      data = data.filter((asset) =>
        visibleKeys.some((key) => String(asset[key] ?? '').toLowerCase().includes(query))
      )
    } else {
      data = data.filter((asset) => String(asset[searchField.value] ?? '').toLowerCase().includes(query))
    }
  }
  return data
})

const dragKey = ref(null)
const dropKey = ref(null)

function reorderColumns(fromKey, toKey) {
  const columns = [...activeColumns.value]
  const fromIndex = columns.findIndex((column) => column.key === fromKey)
  const toIndex = columns.findIndex((column) => column.key === toKey)
  if (fromIndex === -1 || toIndex === -1 || fromIndex === toIndex) return
  const [moved] = columns.splice(fromIndex, 1)
  columns.splice(toIndex, 0, moved)
  activeColumns.value = columns
}

function estimateColumnWidth(column) {
  const headerWidth = String(column.label ?? '').length * 14 + 48
  let contentWidth = 0

  for (const row of filteredAssets.value) {
    const value = row[column.key]
    const text = value == null || value === '' ? '-' : String(value)
    contentWidth = Math.max(contentWidth, text.length * 8 + 32)
  }

  return Math.min(Math.max(column.width ?? 150, headerWidth, contentWidth), 720)
}

const tableColumns = computed(() => {
  const currentDragKey = dragKey.value
  const currentDropKey = dropKey.value

  return activeColumns.value
    .filter((column) => column.visible)
    .map((column) => {
      const isDropTarget = currentDropKey === column.key && currentDragKey !== column.key
      const computedWidth = estimateColumnWidth(column)

      return {
        key: column.key,
        width: computedWidth,
        title: () =>
          h(
            'div',
            {
              draggable: true,
              style: {
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                cursor: 'grab',
                userSelect: 'none',
                padding: '0 2px',
                height: '100%',
                borderLeft: isDropTarget ? '3px solid #4098fc' : '3px solid transparent',
                opacity: currentDragKey === column.key ? 0.45 : 1,
                transition: 'border-color 0.1s, opacity 0.1s',
                whiteSpace: 'nowrap',
              },
              onDragstart: (event) => {
                event.dataTransfer.effectAllowed = 'move'
                event.dataTransfer.setData('text/plain', column.key)
                dragKey.value = column.key
              },
              onDragover: (event) => {
                event.preventDefault()
                event.dataTransfer.dropEffect = 'move'
                if (dropKey.value !== column.key) dropKey.value = column.key
              },
              onDragleave: () => {
                if (dropKey.value === column.key) dropKey.value = null
              },
              onDrop: (event) => {
                event.preventDefault()
                const from = event.dataTransfer.getData('text/plain') || dragKey.value
                if (from && from !== column.key) reorderColumns(from, column.key)
                dragKey.value = null
                dropKey.value = null
              },
              onDragend: () => {
                dragKey.value = null
                dropKey.value = null
              },
            },
            [
              h('span', { style: 'color:#bbb; font-size:11px; flex-shrink:0;' }, '⠿'),
              h('span', { style: 'white-space: nowrap; overflow: visible; text-overflow: clip;' }, column.label),
            ]
          ),
        render: (row) => {
          const value = row[column.key]
          if (column.key === 'status') {
            return h(
              NTag,
              {
                type: STATUS_TYPES[value] ?? 'default',
                size: 'small',
              },
              { default: () => STATUS_LABELS[value] ?? value ?? '-' }
            )
          }
          return h(
            'div',
            {
              style: {
                whiteSpace: 'nowrap',
                overflow: 'visible',
                textOverflow: 'clip',
              },
            },
            value != null && value !== '' ? String(value) : '-'
          )
        },
      }
    })
})

const scrollX = computed(() =>
  tableColumns.value.reduce((sum, column) => sum + (column.width ?? 150), 0)
)
const SCROLL_END_GUTTER = 56
const scrollContentWidth = computed(() => scrollX.value + SCROLL_END_GUTTER)

const windowHeight = ref(window.innerHeight)
const tableMaxHeight = computed(() => windowHeight.value - 200)

function rowProps(row) {
  return {
    style: 'cursor:pointer;',
    onClick: () => router.push({ path: '/assets/details', query: { id: row.id } }),
  }
}

const topScrollRef = ref(null)
const tableHostRef = ref(null)
let tableScrollEl = null
let syncing = false

function onTopScroll() {
  if (syncing || !tableScrollEl) return
  syncing = true
  tableScrollEl.scrollLeft = topScrollRef.value.scrollLeft
  syncing = false
}

function onTableScroll() {
  if (syncing || !topScrollRef.value) return
  syncing = true
  topScrollRef.value.scrollLeft = tableScrollEl.scrollLeft
  syncing = false
}

const onResize = () => {
  windowHeight.value = window.innerHeight
}

onMounted(async () => {
  await fetchAssets()
  await nextTick()
  tableScrollEl = tableHostRef.value?.querySelector('.n-data-table .n-scrollbar-container')
  tableScrollEl?.addEventListener('scroll', onTableScroll, { passive: true })
  window.addEventListener('resize', onResize)
})

onUnmounted(() => {
  tableScrollEl?.removeEventListener('scroll', onTableScroll)
  window.removeEventListener('resize', onResize)
})
</script>
