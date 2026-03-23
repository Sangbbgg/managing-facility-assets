<template>
  <PageShell title="보고서">
    <n-tabs v-model:value="tab" type="line" animated style="margin-top:8px;">

      <!-- ── 보고서 생성 ───────────────────────────────────────── -->
      <n-tab-pane name="generate" tab="보고서 생성">
        <n-card style="max-width:480px; margin-top:16px;">
          <n-form label-placement="left" label-width="90">
            <n-form-item label="서식 선택">
              <n-select
                v-model:value="genTemplateId"
                :options="templateOptions"
                placeholder="서식을 선택하세요"
                filterable
              />
            </n-form-item>
            <n-form-item label="연도">
              <n-select v-model:value="genYear" :options="yearOptions" style="width:130px" />
            </n-form-item>
            <n-form-item label="월">
              <n-select
                v-model:value="genMonth"
                :options="monthOptions"
                style="width:130px"
                placeholder="전체"
                clearable
              />
            </n-form-item>
          </n-form>
          <n-button
            type="primary"
            :loading="generating"
            :disabled="!genTemplateId || !genYear"
            @click="doGenerate"
            block
          >
            📥 보고서 생성 (xlsx 다운로드)
          </n-button>
        </n-card>
      </n-tab-pane>

      <!-- ── 서식 관리 ─────────────────────────────────────────── -->
      <n-tab-pane name="manage" tab="서식 관리">
        <div style="margin:12px 0; display:flex; justify-content:flex-end;">
          <n-button type="primary" @click="openCreate">+ 새 서식</n-button>
        </div>
        <n-data-table
          :columns="tableColumns"
          :data="templates"
          :loading="loading"
          :row-key="r => r.id"
          size="small"
          striped
        />
      </n-tab-pane>
    </n-tabs>

    <!-- ── 서식 편집 모달 ─────────────────────────────────────── -->
    <n-modal
      v-model:show="showModal"
      :title="editingId ? '서식 수정' : '새 서식'"
      preset="card"
      style="width:860px; max-width:96vw;"
      :mask-closable="false"
    >
      <n-form ref="formRef" :model="form" label-placement="left" label-width="90">
        <n-grid :cols="2" :x-gap="16">
          <n-gi>
            <n-form-item label="서식명" path="name" :rule="{ required: true, message: '필수' }">
              <n-input v-model:value="form.name" placeholder="고유 식별자 (영문/한글)" />
            </n-form-item>
          </n-gi>
          <n-gi>
            <n-form-item label="표시명" path="display_name" :rule="{ required: true, message: '필수' }">
              <n-input v-model:value="form.display_name" placeholder="화면 표시 이름" />
            </n-form-item>
          </n-gi>
          <n-gi>
            <n-form-item label="데이터소스" path="data_source" :rule="{ required: true, message: '필수' }">
              <n-select
                v-model:value="form.data_source"
                :options="dataSourceOptions"
                placeholder="데이터소스 선택"
                @update:value="onDataSourceChange"
              />
            </n-form-item>
          </n-gi>
          <n-gi>
            <n-form-item label="시트명">
              <n-input v-model:value="form.sheet_name" placeholder="엑셀 시트명" />
            </n-form-item>
          </n-gi>
          <n-gi>
            <n-form-item label="헤더색상">
              <n-input v-model:value="form.header_color" style="width:140px" />
              <div
                :style="{
                  width: '28px', height: '28px',
                  background: form.header_color,
                  border: '1px solid #ccc',
                  borderRadius: '4px',
                  marginLeft: '8px',
                  flexShrink: 0,
                }"
              />
            </n-form-item>
          </n-gi>
          <n-gi>
            <n-form-item label="활성">
              <n-switch v-model:value="form.is_active" />
            </n-form-item>
          </n-gi>
        </n-grid>

        <n-divider style="margin:12px 0;">컬럼 구성</n-divider>

        <!-- 필드 추가 -->
        <div style="display:flex; gap:8px; align-items:center; margin-bottom:10px;">
          <span style="font-size:13px; color:#555; white-space:nowrap;">필드 추가:</span>
          <n-select
            v-model:value="addFieldKey"
            :options="availableFieldOptions"
            placeholder="추가할 필드 선택..."
            style="flex:1; max-width:280px;"
            filterable
            clearable
          />
          <n-button size="small" :disabled="!addFieldKey" @click="addColumn">+ 추가</n-button>
          <span style="font-size:12px; color:#999; margin-left:4px;">
            ({{ form.columns.length }}개 컬럼)
          </span>
        </div>

        <!-- 컬럼 목록 -->
        <div style="max-height:340px; overflow-y:auto; border:1px solid #e0e0e0; border-radius:4px;">
          <table style="width:100%; border-collapse:collapse; font-size:13px;">
            <thead>
              <tr style="background:#f5f5f5;">
                <th style="padding:6px 10px; text-align:left; width:180px;">헤더명</th>
                <th style="padding:6px 10px; text-align:left;">필드</th>
                <th style="padding:6px 10px; text-align:center; width:80px;">너비</th>
                <th style="padding:6px 10px; text-align:center; width:80px;">순서</th>
                <th style="padding:6px 10px; text-align:center; width:40px;"></th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(col, idx) in form.columns"
                :key="idx"
                style="border-top:1px solid #eee;"
              >
                <td style="padding:4px 8px;">
                  <n-input v-model:value="col.header" size="small" />
                </td>
                <td style="padding:4px 8px; color:#666; font-size:12px;">
                  {{ col.field }}
                </td>
                <td style="padding:4px 8px;">
                  <n-input-number
                    v-model:value="col.width"
                    size="small"
                    :min="5" :max="80"
                    style="width:70px;"
                  />
                </td>
                <td style="padding:4px 8px; text-align:center;">
                  <n-button-group size="tiny">
                    <n-button :disabled="idx === 0" @click="moveCol(idx, -1)">↑</n-button>
                    <n-button :disabled="idx === form.columns.length - 1" @click="moveCol(idx, 1)">↓</n-button>
                  </n-button-group>
                </td>
                <td style="padding:4px 8px; text-align:center;">
                  <n-button size="tiny" type="error" @click="removeCol(idx)">✕</n-button>
                </td>
              </tr>
              <tr v-if="form.columns.length === 0">
                <td colspan="5" style="padding:16px; text-align:center; color:#999;">
                  위에서 필드를 추가하세요
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </n-form>

      <template #footer>
        <n-space justify="end">
          <n-button @click="showModal = false">취소</n-button>
          <n-button type="primary" :loading="saving" @click="doSave">저장</n-button>
        </n-space>
      </template>
    </n-modal>
  </PageShell>
</template>

<script setup>
import { ref, computed, h, onMounted } from 'vue'
import { NButton, useMessage, useDialog } from 'naive-ui'
import PageShell from '@/components/common/PageShell.vue'
import { reportsApi } from '@/api/reportsApi'

const message = useMessage()
const dialog  = useDialog()

// ── 탭 ────────────────────────────────────────────────────────
const tab = ref('generate')

// ── 서식 목록 ─────────────────────────────────────────────────
const templates    = ref([])
const loading      = ref(false)
const dataSources  = ref([])

async function loadTemplates() {
  loading.value = true
  try { templates.value = await reportsApi.listTemplates() }
  finally { loading.value = false }
}

const templateOptions = computed(() =>
  templates.value
    .filter(t => t.is_active)
    .map(t => ({ label: t.display_name, value: t.id }))
)

const dataSourceOptions = computed(() =>
  dataSources.value.map(s => ({ label: s, value: s }))
)

// ── 보고서 생성 ────────────────────────────────────────────────
const genTemplateId = ref(null)
const genYear       = ref(new Date().getFullYear())
const genMonth      = ref(null)
const generating    = ref(false)

const yearOptions = computed(() => {
  const cur = new Date().getFullYear()
  return Array.from({ length: 6 }, (_, i) => cur - i).map(y => ({ label: `${y}년`, value: y }))
})

const monthOptions = [
  { label: '전체', value: null },
  ...Array.from({ length: 12 }, (_, i) => ({ label: `${i + 1}월`, value: i + 1 })),
]

async function doGenerate() {
  if (!genTemplateId.value || !genYear.value) return
  generating.value = true
  try {
    const res = await reportsApi.generate(genTemplateId.value, genYear.value, genMonth.value)
    const tmpl = templates.value.find(t => t.id === genTemplateId.value)
    const monthStr = genMonth.value ? `_${String(genMonth.value).padStart(2, '0')}월` : '_전체'
    const filename = `${tmpl?.display_name || 'report'}_${genYear.value}년${monthStr}.xlsx`
    const url = URL.createObjectURL(new Blob([res.data]))
    const a = document.createElement('a')
    a.href = url; a.download = filename; a.click()
    URL.revokeObjectURL(url)
    message.success('보고서가 다운로드되었습니다')
  } catch {
    message.error('보고서 생성 실패')
  } finally {
    generating.value = false
  }
}

// ── 서식 목록 테이블 컬럼 ─────────────────────────────────────
const tableColumns = [
  { title: '서식명',    key: 'name',         width: 160 },
  { title: '표시명',   key: 'display_name',  width: 160 },
  { title: '데이터소스', key: 'data_source', width: 140 },
  { title: '컬럼수',   key: 'columns',       width: 70, render: r => r.columns?.length ?? 0 },
  { title: '활성',     key: 'is_active',     width: 60, render: r => r.is_active ? '✓' : '-' },
  { title: '수정일',   key: 'updated_at',    width: 110, render: r => r.updated_at?.slice(0, 10) },
  {
    title: '액션', key: 'actions', width: 130,
    render: (row) => h('div', { style: 'display:flex;gap:6px;' }, [
      h(NButton, { size: 'tiny', onClick: () => openEdit(row) }, { default: () => '편집' }),
      h(NButton, { size: 'tiny', type: 'error', onClick: () => confirmDelete(row) }, { default: () => '삭제' }),
    ]),
  },
]

// ── 서식 편집 모달 ─────────────────────────────────────────────
const showModal    = ref(false)
const editingId    = ref(null)
const saving       = ref(false)
const formRef      = ref(null)
const fieldCatalog = ref([])
const addFieldKey  = ref(null)

const availableFieldOptions = computed(() =>
  fieldCatalog.value.map(f => ({
    label: `${f.label}  (${f.field})`,
    value: f.field,
  }))
)

const emptyForm = () => ({
  name: '', display_name: '', data_source: '',
  sheet_name: '', columns: [], header_color: '#1F4E79', is_active: true,
})

const form = ref(emptyForm())

async function onDataSourceChange(val) {
  form.value.sheet_name = val || ''
  fieldCatalog.value = val ? await reportsApi.getFields(val) : []
  addFieldKey.value = null
}

function addColumn() {
  if (!addFieldKey.value) return
  const f = fieldCatalog.value.find(x => x.field === addFieldKey.value)
  if (!f) return
  // 중복 방지
  if (form.value.columns.some(c => c.field === f.field)) {
    message.warning('이미 추가된 필드입니다')
    return
  }
  form.value.columns.push({ header: f.label, field: f.field, width: f.width ?? 15 })
  addFieldKey.value = null
}

function moveCol(idx, dir) {
  const cols = form.value.columns
  const target = idx + dir
  if (target < 0 || target >= cols.length) return
  ;[cols[idx], cols[target]] = [cols[target], cols[idx]]
}

function removeCol(idx) {
  form.value.columns.splice(idx, 1)
}

function openCreate() {
  editingId.value = null
  form.value = emptyForm()
  fieldCatalog.value = []
  addFieldKey.value = null
  showModal.value = true
}

async function openEdit(row) {
  editingId.value = row.id
  form.value = {
    name: row.name,
    display_name: row.display_name,
    data_source: row.data_source,
    sheet_name: row.sheet_name,
    columns: JSON.parse(JSON.stringify(row.columns || [])),
    header_color: row.header_color || '#1F4E79',
    is_active: row.is_active,
  }
  fieldCatalog.value = row.data_source ? await reportsApi.getFields(row.data_source) : []
  addFieldKey.value = null
  showModal.value = true
}

async function doSave() {
  try { await formRef.value?.validate() } catch { return }
  saving.value = true
  try {
    const body = { ...form.value }
    if (editingId.value) {
      const updated = await reportsApi.updateTemplate(editingId.value, body)
      const idx = templates.value.findIndex(t => t.id === editingId.value)
      if (idx !== -1) templates.value[idx] = updated
    } else {
      const created = await reportsApi.createTemplate(body)
      templates.value.push(created)
    }
    showModal.value = false
    message.success('저장되었습니다')
  } catch (e) {
    message.error(e.response?.data?.detail || '저장 실패')
  } finally {
    saving.value = false
  }
}

function confirmDelete(row) {
  dialog.warning({
    title: '서식 삭제',
    content: `"${row.display_name}" 서식을 삭제하시겠습니까?`,
    positiveText: '삭제',
    negativeText: '취소',
    onPositiveClick: async () => {
      await reportsApi.deleteTemplate(row.id)
      templates.value = templates.value.filter(t => t.id !== row.id)
      message.success('삭제되었습니다')
    },
  })
}

onMounted(async () => {
  dataSources.value = await reportsApi.getDataSources()
  await loadTemplates()
})
</script>
