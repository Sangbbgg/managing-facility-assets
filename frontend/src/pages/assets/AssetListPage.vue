<template>
  <PageShell title="자산 현황">
    <!-- 툴바 -->
    <n-space justify="space-between" style="margin-bottom:12px;" wrap>
      <n-space wrap>
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
        <n-text depth="3" style="font-size:12px; line-height:32px;">
          {{ visibleCount }}개 컬럼 / {{ filteredAssets.length }}건
        </n-text>
      </n-space>

      <n-space wrap align="center">
        <!-- 검색 컬럼 선택 -->
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
        />
        <n-select
          v-model:value="filterStatus"
          :options="statusOptions"
          clearable
          placeholder="상태"
          style="width:110px;"
          size="small"
        />
      </n-space>
    </n-space>

    <!-- 데이터 테이블 -->
    <n-data-table
      :columns="tableColumns"
      :data="filteredAssets"
      :loading="loading"
      :row-key="row => row.id"
      :pagination="{ pageSize: 30, showSizePicker: true, pageSizes: [20, 30, 50, 100] }"
      :row-props="rowProps"
      :scroll-x="scrollX"
      striped
      size="small"
      style="min-height:400px;"
    />
  </PageShell>
</template>

<script setup>
import { ref, computed, onMounted, h } from 'vue'
import { useRouter } from 'vue-router'
import { NTag } from 'naive-ui'
import PageShell from '@/components/common/PageShell.vue'
import LayoutSelector from '@/components/assets/LayoutSelector.vue'
import ColumnConfigPopover from '@/components/assets/ColumnConfigPopover.vue'
import client from '@/api/client'

const router  = useRouter()
const loading = ref(false)
const assets  = ref([])   // enriched rows

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
  { key: 'asset_code',          label: '자산코드',      width: 160, visible: true },
  { key: 'asset_name',          label: '설비명',        width: 180, visible: true },
  { key: 'importance',          label: '중요도',        width: 70,  visible: true },
  { key: 'status',              label: '상태',          width: 90,  visible: true },
  { key: 'group_name',          label: '그룹',          width: 150, visible: true },
  { key: 'location_full_path',  label: '위치',          width: 200, visible: true },
  { key: 'equipment_type_name', label: '장비종류',      width: 110, visible: true },
  { key: 'os_name',             label: 'OS',            width: 180, visible: true },
  { key: 'av_name',             label: '백신',          width: 150, visible: true },
  { key: 'ip_address',          label: 'IP 주소',       width: 130, visible: true },
  { key: 'install_date',        label: '설치일',        width: 100, visible: true },
  { key: 'model_name',          label: '모델명',        width: 160, visible: false },
  { key: 'serial_number',       label: '시리얼번호',    width: 140, visible: false },
  { key: 'purpose',             label: '용도',          width: 160, visible: false },
  { key: 'group_full_path',     label: '그룹 경로',     width: 220, visible: false },
  { key: 'group_code',          label: '그룹코드',      width: 100, visible: false },
  { key: 'location_name',       label: '위치명',        width: 130, visible: false },
  { key: 'equipment_type_code', label: '장비코드',      width: 100, visible: false },
  { key: 'os_version',          label: 'OS버전',        width: 120, visible: false },
  { key: 'os_eol_date',         label: 'OS EoL',        width: 100, visible: false },
  { key: 'os_extended_eol',     label: 'OS 연장EoL',    width: 110, visible: false },
  { key: 'av_version',          label: '백신버전',      width: 120, visible: false },
  { key: 'av_support_end',      label: '백신지원종료',  width: 120, visible: false },
  { key: 'manager_name',        label: '담당자',        width: 100, visible: false },
  { key: 'manager_title',       label: '담당자 직책',   width: 100, visible: false },
  { key: 'manager_dept',        label: '담당 부서',     width: 130, visible: false },
  { key: 'manager_contact',     label: '담당자 연락처', width: 140, visible: false },
  { key: 'supervisor_name',     label: '책임자',        width: 100, visible: false },
  { key: 'supervisor_title',    label: '책임자 직책',   width: 100, visible: false },
  { key: 'supervisor_dept',     label: '책임자 부서',   width: 130, visible: false },
  { key: 'last_collected_at',   label: '최근수집일',    width: 120, visible: false },
  { key: 'created_at',          label: '등록일',        width: 100, visible: false },
  { key: 'updated_at',          label: '최종수정일',    width: 120, visible: false },
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

// ── 상태 관련 ─────────────────────────────────────────────────
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
const searchField  = ref('__all__')   // '__all__' = 전체 컬럼

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
      // 표시 중인 모든 컬럼에서 검색
      const visibleKeys = activeColumns.value.filter(c => c.visible).map(c => c.key)
      data = data.filter(a =>
        visibleKeys.some(k => String(a[k] ?? '').toLowerCase().includes(q))
      )
    } else {
      data = data.filter(a =>
        String(a[searchField.value] ?? '').toLowerCase().includes(q)
      )
    }
  }
  return data
})

// ── 테이블 컬럼 빌더 ──────────────────────────────────────────
const tableColumns = computed(() =>
  activeColumns.value
    .filter(c => c.visible)
    .map(c => ({
      title:    c.label,
      key:      c.key,
      width:    c.width,
      ellipsis: { tooltip: true },
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
    }))
)

const scrollX = computed(() =>
  activeColumns.value.filter(c => c.visible).reduce((sum, c) => sum + (c.width ?? 150), 0)
)

// ── 행 클릭 ───────────────────────────────────────────────────
function rowProps(row) {
  return {
    style: 'cursor:pointer;',
    onClick: () => router.push({ path: '/assets/details', query: { id: row.id } }),
  }
}

onMounted(fetchAssets)
</script>
