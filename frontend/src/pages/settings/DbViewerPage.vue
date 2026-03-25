<template>
  <PageShell title="PostgreSQL DB">
    <div style="display:flex;gap:16px">

      <!-- 왼쪽: 테이블 목록 -->
      <n-card style="width:240px;flex-shrink:0" :content-style="{ padding: 0 }">
        <template #header>
          <div style="display:flex;justify-content:space-between;align-items:center">
            <span style="font-size:0.9em;font-weight:600">테이블 ({{ tables.length }})</span>
            <n-button size="tiny" @click="loadTables" :loading="loadingTables">새로고침</n-button>
          </div>
        </template>
        <n-spin :show="loadingTables">
          <div :style="{ maxHeight: listHeight + 'px', overflowY: 'auto' }">
            <n-list hoverable clickable>
              <n-list-item
                v-for="t in tables"
                :key="t.name"
                :style="selectedTable === t.name ? 'background:#f0f9eb' : ''"
                @click="selectTable(t)"
              >
                <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;padding:0 12px">
                  <span style="font-size:0.85em;font-family:monospace;word-break:break-all">{{ t.name }}</span>
                  <n-tag size="small" :type="t.rows > 0 ? 'success' : 'default'" style="flex-shrink:0">
                    {{ t.rows }}
                  </n-tag>
                </div>
              </n-list-item>
            </n-list>
          </div>
        </n-spin>
      </n-card>

      <!-- 오른쪽: 테이블 데이터 -->
      <n-card style="flex:1;min-width:0">
        <template #header>
          <div v-if="selectedTable" style="display:flex;justify-content:space-between;align-items:center">
            <div style="display:flex;align-items:center;gap:12px">
              <span style="font-family:monospace;font-weight:600">{{ selectedTable }}</span>
              <n-tag size="small" type="info">총 {{ tableTotal }}행</n-tag>
            </div>
            <span style="font-size:0.8em;color:#666">{{ columns.length }}개 컬럼</span>
          </div>
          <span v-else style="color:#999">← 테이블을 선택하세요</span>
        </template>

        <template v-if="selectedTable">
          <!-- 컬럼 정보 -->
          <n-collapse style="margin-bottom:12px">
            <n-collapse-item title="컬럼 정보" name="cols">
              <div style="display:flex;flex-wrap:wrap;gap:6px">
                <n-tag
                  v-for="col in currentTableMeta?.columns"
                  :key="col.name"
                  size="small"
                  :type="col.name === 'id' ? 'warning' : 'default'"
                >
                  {{ col.name }}
                  <span style="color:#999;font-size:0.8em;margin-left:4px">{{ col.type }}</span>
                </n-tag>
              </div>
            </n-collapse-item>
          </n-collapse>

          <!-- 데이터 테이블: max-height로 내부 스크롤 -->
          <n-data-table
            :columns="tableColumns"
            :data="rows"
            :loading="loadingData"
            :scroll-x="tableScrollX"
            :max-height="tableBodyHeight"
            size="small"
          />

          <!-- 페이지네이션 -->
          <div style="display:flex;justify-content:flex-end;padding-top:12px">
            <n-pagination
              v-model:page="page"
              :page-count="Math.ceil(tableTotal / pageSize)"
              :page-size="pageSize"
              show-size-picker
              :page-sizes="[20, 50, 100]"
              @update:page="loadData"
              @update:page-size="onSizeChange"
            />
          </div>
        </template>

        <n-empty v-else description="테이블을 선택하면 데이터가 표시됩니다" style="margin-top:80px" />
      </n-card>

    </div>
  </PageShell>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, h } from 'vue'
import { NText } from 'naive-ui'
import PageShell from '@/components/common/PageShell.vue'
import { adminApi } from '@/api/adminApi'

const tables         = ref([])
const loadingTables  = ref(false)
const selectedTable  = ref(null)
const columns        = ref([])
const rows           = ref([])
const tableTotal     = ref(0)
const loadingData    = ref(false)
const page           = ref(1)
const pageSize       = ref(50)

// 창 높이 반응형
const windowHeight = ref(window.innerHeight)
function onResize() { windowHeight.value = window.innerHeight }
onMounted(() => window.addEventListener('resize', onResize))
onUnmounted(() => window.removeEventListener('resize', onResize))

// PageShell 헤더(56) + 페이지 패딩(48) + 카드 헤더(52) + collapse(40) + 페이지네이션(52) + 여유(20)
const tableBodyHeight = computed(() => windowHeight.value - 328)
// 왼쪽 목록: PageShell 헤더 + 페이지 패딩 + 카드 헤더
const listHeight = computed(() => windowHeight.value - 180)

const currentTableMeta = computed(() => tables.value.find(t => t.name === selectedTable.value))

// 문자열 픽셀 너비 추정 (약 8px/char + 패딩)
function estimateWidth(text) {
  if (text === null || text === undefined) return 48
  const len = String(text).length
  return Math.min(Math.max(len * 8 + 24, 60), 400)
}

const tableColumns = computed(() => {
  return columns.value.map(col => {
    let width = estimateWidth(col)
    for (const row of rows.value) {
      const val = row[col]
      const str = (val === null || val === undefined) ? 'NULL'
        : typeof val === 'object' ? JSON.stringify(val) : String(val)
      const w = estimateWidth(str)
      if (w > width) width = w
    }
    return {
      key: col,
      title: col,
      width,
      ellipsis: { tooltip: true },
      render: (row) => {
        const val = row[col]
        if (val === null || val === undefined) {
          return h(NText, { depth: 3, style: 'font-style:italic;font-size:0.85em' }, { default: () => 'NULL' })
        }
        return typeof val === 'object' ? JSON.stringify(val) : String(val)
      },
    }
  })
})

const tableScrollX = computed(() => tableColumns.value.reduce((sum, c) => sum + (c.width || 120), 0))

async function loadTables() {
  loadingTables.value = true
  try {
    tables.value = await adminApi.listTables()
  } finally {
    loadingTables.value = false
  }
}

async function selectTable(t) {
  selectedTable.value = t.name
  page.value = 1
  await loadData()
}

async function loadData() {
  if (!selectedTable.value) return
  loadingData.value = true
  try {
    const res = await adminApi.getTableData(selectedTable.value, page.value, pageSize.value)
    columns.value    = res.columns
    rows.value       = res.rows
    tableTotal.value = res.total
  } finally {
    loadingData.value = false
  }
}

function onSizeChange(size) {
  pageSize.value = size
  page.value = 1
  loadData()
}

onMounted(loadTables)
</script>
