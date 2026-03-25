<template>
  <PageShell title="자산 현황">
    <!-- 툴바 -->
    <n-space justify="space-between" style="margin-bottom:12px;" wrap>
      <n-space wrap align="center">
        <LayoutSelector
          :columns="activeColumns"
          page-key="asset_list"
          @apply="onLayoutApply"
        />
        <ColumnConfigPopover
          :columns="activeColumns"
          :default-columns="DEFAULT_COLUMNS"
          @update:columns="onColumnsUpdate"
        />
        <n-text depth="3" style="font-size:12px;">
          {{ visibleCount }}개 컬럼 표시 / 전체 {{ assets.length }}건
        </n-text>
      </n-space>

      <n-space wrap align="center">
        <n-select
          v-model:value="searchField"
          :options="searchFieldOptions"
          style="width:150px;"
          size="small"
        />
        <n-input
          v-model:value="search"
          placeholder="검색어 입력"
          clearable
          style="width:200px;"
          size="small"
          @keydown.enter="() => {}"
        />
        <n-select
          v-model:value="filterStatus"
          :options="statusOptions"
          clearable
          placeholder="상태 필터"
          style="width:110px;"
          size="small"
        />
        <n-text depth="3" style="font-size:12px;">
          {{ filteredAssets.length }}건
        </n-text>
      </n-space>
    </n-space>

    <!-- 드래그 힌트 -->
    <n-text depth="3" style="font-size:11px; display:block; margin-bottom:6px;">
      💡 컬럼 헤더를 드래그하여 순서를 변경할 수 있습니다
    </n-text>

    <!-- 스크롤 래퍼 (세로 네이티브) -->
    <div :style="{ overflowY: 'auto', maxHeight: tableMaxHeight + 'px' }">
      <!-- 상단 미러 가로 스크롤바 (세로 스크롤 시 상단 고정) -->
      <div
        ref="topScrollRef"
        style="overflow-x:auto; overflow-y:hidden; height:14px; position:sticky; top:0; z-index:3; background:var(--n-color, #fff); border-top:1px solid #e0e0e6; border-bottom:1px solid #e0e0e6;"
        @scroll.passive="onTopScroll"
      >
        <div :style="{ width: scrollX + 'px', height: '1px' }"></div>
      </div>

      <n-data-table
        :columns="tableColumns"
        :data="filteredAssets"
        :loading="loading"
        :row-key="row => row.id"
        :row-props="rowProps"
        :scroll-x="scrollX"
        striped
        size="small"
      />
    </div>
  </PageShell>
</template>

<script setup>
import { ref, computed, onMounted, h, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { NTag } from 'naive-ui'
import PageShell from '@/components/common/PageShell.vue'
import LayoutSelector from '@/components/assets/LayoutSelector.vue'
import ColumnConfigPopover from '@/components/assets/ColumnConfigPopover.vue'
import client from '@/api/client'

const router  = useRouter()
const loading = ref(false)
const assets  = ref([])

// ── 데이터 로드 ────────────────────────────────────────────────
async function fetchAssets() {
  loading.value = true
  try {
    const res = await client.get('/api/assets/enriched')
    assets.value = res.data
  } finally {
    loading.value = false
  }
}

// ── 전체 컬럼 정의 ─────────────────────────────────────────────
const DEFAULT_COLUMNS = [
  { key: 'asset_code',          label: '자산코드',      width: 145, visible: true  },
  { key: 'asset_name',          label: '설비명',        width: 160, visible: true  },
  { key: 'importance',          label: '중요도',        width: 65,  visible: true  },
  { key: 'status',              label: '상태',          width: 85,  visible: true  },
  { key: 'group_name',          label: '그룹',          width: 110, visible: true  },
  { key: 'location_full_path',  label: '위치',          width: 180, visible: true  },
  { key: 'equipment_type_name', label: '장비종류',      width: 120, visible: true  },
  { key: 'os_name',             label: 'OS',            width: 155, visible: true  },
  { key: 'av_name',             label: '백신',          width: 130, visible: true  },
  { key: 'ip_address',          label: 'IP 주소',       width: 120, visible: true  },
  { key: 'install_date',        label: '설치일',        width: 95,  visible: true  },
  { key: 'model_name',          label: '모델명',        width: 150, visible: false },
  { key: 'serial_number',       label: '시리얼번호',    width: 140, visible: false },
  { key: 'purpose',             label: '용도',          width: 150, visible: false },
  { key: 'group_full_path',     label: '그룹 경로',     width: 210, visible: false },
  { key: 'group_code',          label: '그룹코드',      width: 95,  visible: false },
  { key: 'location_name',       label: '위치명',        width: 120, visible: false },
  { key: 'equipment_type_code', label: '장비코드',      width: 90,  visible: false },
  { key: 'os_version',          label: 'OS버전',        width: 120, visible: false },
  { key: 'os_eol_date',         label: 'OS EoL',        width: 95,  visible: false },
  { key: 'os_extended_eol',     label: 'OS 연장EoL',    width: 105, visible: false },
  { key: 'av_version',          label: '백신버전',      width: 115, visible: false },
  { key: 'av_support_end',      label: '백신지원종료',  width: 115, visible: false },
  { key: 'manager_name',        label: '담당자',        width: 90,  visible: false },
  { key: 'manager_title',       label: '담당자 직책',   width: 100, visible: false },
  { key: 'manager_dept',        label: '담당 부서',     width: 120, visible: false },
  { key: 'manager_contact',     label: '담당자 연락처', width: 130, visible: false },
  { key: 'supervisor_name',     label: '책임자',        width: 90,  visible: false },
  { key: 'supervisor_title',    label: '책임자 직책',   width: 100, visible: false },
  { key: 'supervisor_dept',     label: '책임자 부서',   width: 120, visible: false },
  { key: 'last_collected_at',   label: '최근수집일',    width: 115, visible: false },
  { key: 'created_at',          label: '등록일',        width: 95,  visible: false },
  { key: 'updated_at',          label: '최종수정일',    width: 115, visible: false },
]

const activeColumns = ref(DEFAULT_COLUMNS.map(c => ({ ...c })))
const visibleCount  = computed(() => activeColumns.value.filter(c => c.visible).length)

function onLayoutApply(colsJson) {
  if (!Array.isArray(colsJson)) return
  const keyMap = Object.fromEntries(colsJson.map(c => [c.key, c]))
  activeColumns.value = DEFAULT_COLUMNS.map(c => ({
    ...c,
    visible: keyMap[c.key] !== undefined ? keyMap[c.key].visible : c.visible,
    width:   keyMap[c.key]?.width ?? c.width,
  }))
}
function onColumnsUpdate(cols) {
  activeColumns.value = cols
}

// ── 상태 ─────────────────────────────────────────────────────
const STATUS_LABELS = { OPERATING: '운영중', MAINTENANCE: '점검중', FAULTY: '장애', DISPOSED: '폐기' }
const STATUS_TYPES  = { OPERATING: 'success', MAINTENANCE: 'warning', FAULTY: 'error', DISPOSED: 'default' }
const statusOptions = [
  { label: '운영중', value: 'OPERATING' },
  { label: '점검중', value: 'MAINTENANCE' },
  { label: '장애',   value: 'FAULTY' },
  { label: '폐기',   value: 'DISPOSED' },
]

// ── 검색 ─────────────────────────────────────────────────────
const search       = ref('')
const filterStatus = ref(null)
const searchField  = ref('__all__')

const searchFieldOptions = computed(() => [
  { label: '전체 컬럼', value: '__all__' },
  ...activeColumns.value
    .filter(c => c.visible)
    .map(c => ({ label: c.label, value: c.key })),
])

const filteredAssets = computed(() => {
  let data = assets.value
  if (filterStatus.value) {
    data = data.filter(a => a.status === filterStatus.value)
  }
  if (search.value.trim()) {
    const q = search.value.trim().toLowerCase()
    if (searchField.value === '__all__') {
      const visibleKeys = activeColumns.value.filter(c => c.visible).map(c => c.key)
      data = data.filter(a => visibleKeys.some(k => String(a[k] ?? '').toLowerCase().includes(q)))
    } else {
      data = data.filter(a => String(a[searchField.value] ?? '').toLowerCase().includes(q))
    }
  }
  return data
})

// ── 컬럼 헤더 드래그앤드롭 ────────────────────────────────────
const dragKey     = ref(null)   // 드래그 중인 컬럼 key
const dropKey     = ref(null)   // 드롭 대상 컬럼 key

function reorderColumns(fromKey, toKey) {
  const cols = [...activeColumns.value]
  const fromIdx = cols.findIndex(c => c.key === fromKey)
  const toIdx   = cols.findIndex(c => c.key === toKey)
  if (fromIdx === -1 || toIdx === -1 || fromIdx === toIdx) return
  const [moved] = cols.splice(fromIdx, 1)
  cols.splice(toIdx, 0, moved)
  activeColumns.value = cols
}

// ── 테이블 컬럼 ───────────────────────────────────────────────
const tableColumns = computed(() => {
  // 반응성 트래킹: drag 상태 변화 시 재계산
  const _dragKey = dragKey.value
  const _dropKey = dropKey.value

  return activeColumns.value
    .filter(c => c.visible)
    .map(c => {
      const isDropTarget = _dropKey === c.key && _dragKey !== c.key

      return {
        key:      c.key,
        width:    c.width,
        ellipsis: { tooltip: true },

        // 드래그 가능한 커스텀 헤더
        title: () => h(
          'div',
          {
            draggable: true,
            style: {
              display:        'flex',
              alignItems:     'center',
              gap:            '4px',
              cursor:         'grab',
              userSelect:     'none',
              padding:        '0 2px',
              height:         '100%',
              borderLeft:     isDropTarget ? '3px solid #4098fc' : '3px solid transparent',
              opacity:        _dragKey === c.key ? 0.45 : 1,
              transition:     'border-color 0.1s, opacity 0.1s',
            },
            onDragstart: (e) => {
              e.dataTransfer.effectAllowed = 'move'
              e.dataTransfer.setData('text/plain', c.key)
              dragKey.value = c.key
            },
            onDragover: (e) => {
              e.preventDefault()
              e.dataTransfer.dropEffect = 'move'
              if (dropKey.value !== c.key) dropKey.value = c.key
            },
            onDragleave: () => {
              if (dropKey.value === c.key) dropKey.value = null
            },
            onDrop: (e) => {
              e.preventDefault()
              const from = e.dataTransfer.getData('text/plain') || dragKey.value
              if (from && from !== c.key) reorderColumns(from, c.key)
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
            h('span', c.label),
          ]
        ),

        // 셀 렌더러
        render: (row) => {
          const val = row[c.key]
          if (c.key === 'status') {
            return h(NTag, {
              type: STATUS_TYPES[val] ?? 'default',
              size: 'small',
            }, { default: () => STATUS_LABELS[val] ?? val ?? '-' })
          }
          return val != null && val !== '' ? val : '-'
        },
      }
    })
})

const scrollX = computed(() =>
  activeColumns.value
    .filter(c => c.visible)
    .reduce((sum, c) => sum + (c.width ?? 150), 0)
)

// 창 높이 반응형 — 툴바·헤더·여백 합산 약 200px
const windowHeight = ref(window.innerHeight)
const tableMaxHeight = computed(() => windowHeight.value - 200)

// ── 행 클릭 ───────────────────────────────────────────────────
function rowProps(row) {
  return {
    style: 'cursor:pointer;',
    onClick: () => router.push({ path: '/assets/details', query: { id: row.id } }),
  }
}

// ── 상단 미러 가로 스크롤바 ────────────────────────────────────
const topScrollRef = ref(null)
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

const onResize = () => { windowHeight.value = window.innerHeight }

onMounted(async () => {
  await fetchAssets()
  await nextTick()
  tableScrollEl = document.querySelector('.n-data-table .n-scrollbar-container')
  tableScrollEl?.addEventListener('scroll', onTableScroll, { passive: true })
  window.addEventListener('resize', onResize)
})
onUnmounted(() => {
  tableScrollEl?.removeEventListener('scroll', onTableScroll)
  window.removeEventListener('resize', onResize)
})
</script>
