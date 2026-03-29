<template>
  <PageShell title="자산 현황">
    <n-space justify="space-between" style="margin-bottom: 12px" wrap>
      <n-space wrap align="center">
        <LayoutSelector :columns="activeColumns" page-key="asset_list" @apply="onLayoutApply" />
        <ColumnConfigPopover
          :columns="activeColumns"
          :default-columns="defaultColumns"
          @update:columns="onColumnsUpdate"
        />
        <n-text depth="3" style="font-size: 12px">
          {{ visibleCount }}개 컬럼 표시 / 전체 {{ assets.length }}건
        </n-text>
      </n-space>

      <n-space wrap align="center">
        <n-select v-model:value="searchField" :options="searchFieldOptions" style="width: 160px" size="small" />
        <n-input
          v-model:value="search"
          placeholder="검색어 입력"
          clearable
          style="width: 220px"
          size="small"
        />
        <n-select
          v-model:value="filterStatus"
          :options="statusOptions"
          clearable
          placeholder="상태 필터"
          style="width: 120px"
          size="small"
        />
        <n-text depth="3" style="font-size: 12px">
          {{ filteredAssets.length }}건
        </n-text>
      </n-space>
    </n-space>

    <n-text depth="3" style="font-size: 11px; display: block; margin-bottom: 6px">
      실제 DB/API에서 조회 가능한 컬럼만 선택할 수 있으며, 헤더 드래그로 순서를 바꿀 수 있습니다.
    </n-text>
    <ListHeader title="자산 목록" :count="filteredAssets.length" />

    <div :style="{ overflowY: 'auto', maxHeight: `${tableMaxHeight}px` }">
      <div
        ref="topScrollRef"
        style="overflow-x: auto; overflow-y: hidden; height: 14px; position: sticky; top: 0; z-index: 3; background: var(--n-color, #fff); border-top: 1px solid #e0e0e6; border-bottom: 1px solid #e0e0e6"
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

const BASE_COLUMN_DEFINITIONS = [
  { key: 'asset_code', label: '자산코드', width: 145, visible: true, section: 'assets', sectionLabel: 'assets', stageLabel: '기본 자산 테이블' },
  { key: 'asset_name', label: '설비명', width: 160, visible: true, section: 'assets', sectionLabel: 'assets', stageLabel: '기본 자산 테이블' },
  { key: 'purpose', label: '용도', width: 150, visible: true, section: 'assets', sectionLabel: 'assets', stageLabel: '기본 자산 테이블' },
  { key: 'importance', label: '중요도', width: 70, visible: true, section: 'assets', sectionLabel: 'assets', stageLabel: '기본 자산 테이블' },
  { key: 'status', label: '상태', width: 85, visible: true, section: 'assets', sectionLabel: 'assets', stageLabel: '기본 자산 테이블' },
  { key: 'install_date', label: '설치일', width: 95, visible: true, section: 'assets', sectionLabel: 'assets', stageLabel: '기본 자산 테이블' },
  { key: 'last_collected_at', label: '최종 수집일', width: 120, visible: true, section: 'assets', sectionLabel: 'assets', stageLabel: '기본 자산 테이블' },
  { key: 'created_at', label: '등록일', width: 100, visible: true, section: 'assets', sectionLabel: 'assets', stageLabel: '기본 자산 테이블' },
  { key: 'updated_at', label: '최종 수정일', width: 120, visible: true, section: 'assets', sectionLabel: 'assets', stageLabel: '기본 자산 테이블' },

  { key: 'active_ip_addresses', label: '사용 IP', width: 180, visible: true, section: 'asset_hw_nics', sectionLabel: 'asset_hw_nics', stageLabel: '대표+사용 IP' },
  { key: 'unused_ip_addresses', label: '미사용 IP', width: 180, visible: false, section: 'asset_hw_nics', sectionLabel: 'asset_hw_nics', stageLabel: 'is_unused IP' },
  { key: 'representative_nic_name', label: '대표 NIC', width: 220, visible: true, section: 'asset_hw_nics', sectionLabel: 'asset_hw_nics', stageLabel: '대표 NIC 조인' },
  { key: 'used_nic_names', label: '사용 NIC', width: 220, visible: false, section: 'asset_hw_nics', sectionLabel: 'asset_hw_nics', stageLabel: '대표/미사용 제외 NIC' },
  { key: 'unused_nic_names', label: '미사용 NIC', width: 220, visible: false, section: 'asset_hw_nics', sectionLabel: 'asset_hw_nics', stageLabel: 'is_unused NIC' },

  { key: 'group_name', label: '그룹', width: 120, visible: true, section: 'group_nodes', sectionLabel: 'group_nodes', stageLabel: '그룹 트리 조인' },
  { key: 'group_full_path', label: '그룹 경로', width: 220, visible: true, section: 'group_nodes', sectionLabel: 'group_nodes', stageLabel: '그룹 트리 조인' },

  { key: 'location_name', label: '위치명', width: 120, visible: true, section: 'location_nodes', sectionLabel: 'location_nodes', stageLabel: '위치 트리 조인' },
  { key: 'location_full_path', label: '위치', width: 200, visible: true, section: 'location_nodes', sectionLabel: 'location_nodes', stageLabel: '위치 트리 조인' },

  { key: 'equipment_type_name', label: '장비종류', width: 120, visible: true, section: 'equipment_types', sectionLabel: 'equipment_types', stageLabel: '장비 종류 조인' },

  { key: 'manager_name', label: '담당자', width: 100, visible: true, section: 'persons', sectionLabel: 'persons', stageLabel: '담당자 조인' },
  { key: 'manager_title', label: '담당자 직급', width: 110, visible: true, section: 'persons', sectionLabel: 'persons', stageLabel: '담당자 조인' },
  { key: 'manager_contact', label: '담당자 연락처', width: 140, visible: true, section: 'persons', sectionLabel: 'persons', stageLabel: '담당자 조인' },

  { key: 'representative_account_name', label: '대표 계정', width: 140, visible: true, section: 'asset_sw_accounts', sectionLabel: 'asset_sw_accounts', stageLabel: '로컬 계정 수집' },
  { key: 'local_account_names', label: '로컬 계정', width: 180, visible: true, section: 'asset_sw_accounts', sectionLabel: 'asset_sw_accounts', stageLabel: '로컬 계정 수집' },
  { key: 'disabled_account_names', label: '미사용 계정', width: 180, visible: false, section: 'asset_sw_accounts', sectionLabel: 'asset_sw_accounts', stageLabel: '로컬 계정 수집' },
]

const activeColumns = ref([])

const dynamicCustomFieldDefinitions = computed(() => {
  const keys = Array.from(
    new Set(
      assets.value.flatMap((asset) =>
        Object.keys(asset.custom_fields_json || {}).filter((key) => String(key).trim())
      )
    )
  ).sort((a, b) => a.localeCompare(b, 'ko'))

  return keys.map((fieldKey) => ({
    key: `custom_field::${fieldKey}`,
    label: fieldKey,
    width: 160,
    visible: false,
    section: 'asset_custom_fields',
    sectionLabel: 'asset_custom_fields',
    stageLabel: '보완 메모 JSON',
  }))
})

const allColumnDefinitions = computed(() => {
  const assetColumns = BASE_COLUMN_DEFINITIONS.filter((column) => column.section === 'assets')
  const nonAssetColumns = BASE_COLUMN_DEFINITIONS.filter((column) => column.section !== 'assets')
  return [
    ...assetColumns.map((column) => ({ ...column })),
    ...dynamicCustomFieldDefinitions.value.map((column) => ({ ...column })),
    ...nonAssetColumns.map((column) => ({ ...column })),
  ]
})

const defaultColumns = computed(() => allColumnDefinitions.value.map((column) => ({ ...column })))

async function fetchAssets() {
  loading.value = true
  try {
    const response = await client.get('/api/assets/enriched')
    assets.value = response.data
    syncColumnsWithAvailableKeys()
  } finally {
    loading.value = false
  }
}

function availableKeys() {
  if (!assets.value.length) {
    return new Set(BASE_COLUMN_DEFINITIONS.map((column) => column.key))
  }
  return new Set(Object.keys(assets.value[0] || {}))
}

function isCustomFieldColumn(key) {
  return String(key || '').startsWith('custom_field::')
}

function syncColumnsWithAvailableKeys() {
  const keys = availableKeys()
  const syncedDefaults = allColumnDefinitions.value
    .filter((column) => isCustomFieldColumn(column.key) || keys.has(column.key))
    .map((column) => ({ ...column }))

  const currentMap = new Map(activeColumns.value.map((column) => [column.key, column]))
  activeColumns.value = syncedDefaults.map((column) => {
    const current = currentMap.get(column.key)
    return {
      ...column,
      visible: current?.visible ?? column.visible,
      width: current?.width ?? column.width,
    }
  })
}

const visibleCount = computed(() => activeColumns.value.filter((column) => column.visible).length)

function onLayoutApply(columnsJson) {
  if (!Array.isArray(columnsJson)) return
  const availableMap = new Map(allColumnDefinitions.value.map((column) => [column.key, column]))
  activeColumns.value = columnsJson
    .filter((column) => availableMap.has(column.key))
    .map((column) => ({
      ...availableMap.get(column.key),
      visible: column.visible,
      width: column.width ?? availableMap.get(column.key).width,
    }))

  const missingColumns = allColumnDefinitions.value.filter(
    (column) => !activeColumns.value.some((active) => active.key === column.key)
  )
  activeColumns.value = [...activeColumns.value, ...missingColumns.map((column) => ({ ...column }))]
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
  ...activeColumns.value
    .filter((column) => column.visible)
    .map((column) => ({ label: column.label, value: column.key })),
])

function getColumnValue(row, key) {
  if (isCustomFieldColumn(key)) {
    const fieldKey = String(key).slice('custom_field::'.length)
    return row.custom_fields_json?.[fieldKey] ?? ''
  }
  return row[key]
}

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
        visibleKeys.some((key) => String(getColumnValue(asset, key) ?? '').toLowerCase().includes(query))
      )
    } else {
      data = data.filter((asset) => String(getColumnValue(asset, searchField.value) ?? '').toLowerCase().includes(query))
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

function getMultiLineValues(row, key) {
  if (key === 'active_ip_addresses') return getIpLines(row, key)
  if (key === 'unused_ip_addresses') return getIpLines(row, key)
  const value = getColumnValue(row, key)
  if (Array.isArray(value)) return value.length ? value.map((item) => String(item)) : ['-']
  return [value == null || value === '' ? '-' : String(value)]
}

function estimateColumnWidth(column) {
  const headerWidth = String(column.label ?? '').length * 14 + 48
  let contentWidth = 0

  for (const row of filteredAssets.value) {
    const values = getMultiLineValues(row, column.key)
    for (const text of values) {
      contentWidth = Math.max(contentWidth, String(text).length * 8 + 32)
    }
  }

  return Math.min(Math.max(column.width ?? 150, headerWidth, contentWidth), 720)
}

const tableColumns = computed(() =>
  activeColumns.value
    .filter((column) => column.visible)
    .map((column) => {
      const isDropTarget = dropKey.value === column.key && dragKey.value !== column.key
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
                opacity: dragKey.value === column.key ? 0.45 : 1,
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
          const value = getColumnValue(row, column.key)
          if (column.key === 'status') {
            return h(
              NTag,
              { type: STATUS_TYPES[value] ?? 'default', size: 'small' },
              { default: () => STATUS_LABELS[value] ?? value ?? '-' }
            )
          }

          const lines = getMultiLineValues(row, column.key)
          return h(
            'div',
            {
              style: {
                display: 'flex',
                flexDirection: 'column',
                gap: '2px',
                whiteSpace: 'nowrap',
              },
            },
            lines.map((line) =>
              h(
                'div',
                {
                  style: {
                    whiteSpace: 'nowrap',
                    overflow: 'visible',
                    textOverflow: 'clip',
                  },
                },
                line
              )
            )
          )
        },
      }
    })
)

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

function getIpLines(row, key) {
  if (key === 'active_ip_addresses') {
    const ips = Array.isArray(row.active_ip_addresses)
      ? row.active_ip_addresses.filter(Boolean).map((value) => String(value))
      : []
    return ips.length ? ips : ['-']
  }
  if (key === 'unused_ip_addresses') {
    const ips = Array.isArray(row.unused_ip_addresses)
      ? row.unused_ip_addresses.filter(Boolean).map((value) => String(value))
      : []
    return ips.length ? ips : ['-']
  }
  const ips = Array.isArray(row.active_ip_addresses)
    ? row.active_ip_addresses.filter(Boolean).map((value) => String(value))
    : []
  if (ips.length) return ips
  return ['-']
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
