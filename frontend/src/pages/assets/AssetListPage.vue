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
          @update:columns="onColumnsUpdate"
        />
      </n-space>
      <n-space wrap>
        <n-input
          v-model:value="search"
          placeholder="자산코드/자산명 검색"
          clearable
          style="width:200px;"
          @keydown.enter="doSearch"
        />
        <n-select
          v-model:value="filterStatus"
          :options="statusOptions"
          clearable
          placeholder="상태"
          style="width:120px;"
        />
        <n-button @click="doSearch">검색</n-button>
      </n-space>
    </n-space>

    <!-- 데이터 테이블 (읽기 전용) -->
    <n-data-table
      :columns="tableColumns"
      :data="filteredAssets"
      :loading="assetStore.loading"
      :row-key="row => row.id"
      :pagination="{ pageSize: 30, showSizePicker: true, pageSizes: [20, 30, 50] }"
      :row-props="rowProps"
      striped
      size="small"
    />
  </PageShell>
</template>

<script setup>
import { ref, computed, onMounted, reactive, h } from 'vue'
import { useRouter } from 'vue-router'
import { NTag } from 'naive-ui'
import PageShell from '@/components/common/PageShell.vue'
import LayoutSelector from '@/components/assets/LayoutSelector.vue'
import ColumnConfigPopover from '@/components/assets/ColumnConfigPopover.vue'
import { useAssetStore } from '@/stores/assetStore'

const router     = useRouter()
const assetStore = useAssetStore()

const search       = ref('')
const filterStatus = ref(null)

const statusOptions = [
  { label: '운영중', value: 'OPERATING' },
  { label: '점검중', value: 'MAINTENANCE' },
  { label: '장애',   value: 'FAULTY' },
  { label: '폐기',   value: 'DISPOSED' },
]

const STATUS_LABELS = { OPERATING: '운영중', MAINTENANCE: '점검중', FAULTY: '장애', DISPOSED: '폐기' }
const STATUS_TYPES  = { OPERATING: 'success', MAINTENANCE: 'warning', FAULTY: 'error', DISPOSED: 'default' }

// 전체 컬럼 정의
const ALL_COLUMNS = [
  { key: 'asset_code',        label: '자산코드',   width: 160, visible: true },
  { key: 'asset_name',        label: '자산명',     width: 200, visible: true },
  { key: 'importance',        label: '중요도',     width: 70,  visible: true },
  { key: 'status',            label: '상태',       width: 90,  visible: true },
  { key: 'model_name',        label: '모델명',     width: 150, visible: true },
  { key: 'serial_number',     label: '시리얼번호', width: 130, visible: false },
  { key: 'ip_address',        label: 'IP주소',     width: 120, visible: true },
  { key: 'purpose',           label: '용도',       width: 150, visible: false },
  { key: 'install_date',      label: '설치일',     width: 100, visible: true },
  { key: 'last_collected_at', label: '최근수집일', width: 130, visible: true },
  { key: 'created_at',        label: '등록일',     width: 100, visible: false },
]

const activeColumns = ref(ALL_COLUMNS.map(c => ({ ...c })))

function onLayoutApply(colsJson) {
  if (!Array.isArray(colsJson)) return
  const keyMap = Object.fromEntries(colsJson.map(c => [c.key, c]))
  activeColumns.value = ALL_COLUMNS.map(c => ({
    ...c,
    visible: keyMap[c.key] !== undefined ? keyMap[c.key].visible : c.visible,
    width:   keyMap[c.key]?.width ?? c.width,
  }))
}

function onColumnsUpdate(cols) {
  activeColumns.value = cols
}

const tableColumns = computed(() =>
  activeColumns.value
    .filter(c => c.visible)
    .map(c => ({
      title: c.label,
      key:   c.key,
      width: c.width,
      ellipsis: { tooltip: true },
      render: (row) => {
        const val = row[c.key]
        if (c.key === 'status') {
          return h(NTag, { type: STATUS_TYPES[val] ?? 'default', size: 'small' }, { default: () => STATUS_LABELS[val] ?? val ?? '-' })
        }
        if ((c.key === 'last_collected_at' || c.key === 'created_at') && val) {
          return val.slice(0, 10)
        }
        return val ?? '-'
      },
    }))
)

const filteredAssets = computed(() => {
  let data = assetStore.list
  if (search.value) {
    const q = search.value.toLowerCase()
    data = data.filter(a =>
      a.asset_code?.toLowerCase().includes(q) ||
      a.asset_name?.toLowerCase().includes(q)
    )
  }
  if (filterStatus.value) {
    data = data.filter(a => a.status === filterStatus.value)
  }
  return data
})

function doSearch() {
  // 필터는 computed로 처리되므로 별도 호출 불필요
}

// 행 클릭 → 세부사항 페이지
function rowProps(row) {
  return {
    style: 'cursor:pointer;',
    onClick: () => router.push({ path: '/assets/details', query: { id: row.id } }),
  }
}

onMounted(() => assetStore.fetchList())
</script>
