<template>
  <PageShell title="양식 템플릿">
    <div class="page-header">
      <div>
        <h2 class="page-title">양식 템플릿 관리</h2>
        <p class="page-description">
          템플릿을 선택하고 셀을 클릭하면 바로 매핑을 편집할 수 있습니다.
        </p>
      </div>
      <div class="header-actions">
        <n-button quaternary @click="togglePreview">
          {{ showPreview ? '미리보기 숨기기' : '미리보기 펼치기' }}
        </n-button>
      </div>
    </div>

    <div class="page-grid" :class="{ collapsed: !showPreview }">
      <div class="left-column">
        <n-card class="pane-card pane-left" :bordered="false">
          <FormTemplateList
            :selected-id="selectedTemplateId"
            @create="openCreateModal"
            @edit="openEditModal"
            @select="handleSelect"
          />
        </n-card>
      </div>

      <FormTemplateWorkbookPreview
        v-if="showPreview"
        :template="selectedTemplate"
        :mappings="store.mappings"
        :selected-cell="selectedCell"
        @select-cell="handleSelectCell"
      />
    </div>

    <n-modal
      v-model:show="showTemplateModal"
      preset="card"
      :title="editingTemplate ? '템플릿 수정' : '새 템플릿 등록'"
      style="width: 560px; max-width: 92vw"
      :mask-closable="false"
    >
      <n-form label-placement="left" label-width="96">
        <n-form-item label="템플릿명">
          <n-input v-model:value="templateForm.name" placeholder="예: 자산 상세 보고서" />
        </n-form-item>
        <n-form-item label="분류">
          <n-select v-model:value="templateForm.category" :options="categoryOptions" />
        </n-form-item>
        <n-form-item label="폴더">
          <n-select
            v-model:value="templateForm.folder_id"
            :options="folderOptions"
            clearable
            placeholder="미분류"
          />
        </n-form-item>
        <n-form-item label="설명">
          <n-input v-model:value="templateForm.description" type="textarea" :rows="3" />
        </n-form-item>
        <n-form-item v-if="editingTemplate" label="사용 여부">
          <n-switch v-model:value="templateForm.is_active" />
        </n-form-item>
        <n-form-item v-else label="양식 파일">
          <n-upload accept=".xlsx,.xls" :max="1" @change="handleFileChange">
            <n-button>양식 파일 선택</n-button>
          </n-upload>
        </n-form-item>
      </n-form>

      <template #footer>
        <div class="modal-footer">
          <n-button @click="closeModal">취소</n-button>
          <n-button
            type="primary"
            :loading="saving"
            :disabled="!canSubmit"
            @click="submitTemplate"
          >
            {{ editingTemplate ? '저장' : '등록' }}
          </n-button>
        </div>
      </template>
    </n-modal>

    <n-modal
      v-model:show="showMappingModal"
      preset="card"
      title="셀 매핑"
      style="width: min(1800px, 99vw)"
      content-style="padding: 0"
      :mask-closable="true"
    >
      <div v-if="selectedTemplate" class="mapping-modal-content">
        <n-scrollbar class="mapping-modal-scroll">
          <div class="mapping-body">
            <div class="mapping-header">
              <div>
                <div class="mapping-title">{{ selectedCellLabel || '셀을 선택해 주세요' }}</div>
                <div class="mapping-subtitle">
                  데이터 소스와 필드를 선택하면 샘플 자산 기준 실제 값을 바로 확인할 수 있습니다.
                </div>
              </div>
              <n-button
                type="primary"
                :disabled="!canSaveMapping"
                :loading="mappingSaving"
                @click="saveSelectedMapping"
              >
                매핑 저장
              </n-button>
            </div>

            <div class="mapping-layout">
              <n-form label-placement="top" class="mapping-form">
                <n-form-item label="시트 / 셀">
                  <n-input
                    :value="selectedCellLabel"
                    readonly
                    placeholder="미리보기에서 셀을 선택해 주세요"
                  />
                </n-form-item>
                <n-form-item label="데이터 소스">
                  <n-select
                    v-model:value="mappingForm.data_source"
                    :options="sourceOptions"
                    placeholder="데이터 소스를 선택해 주세요"
                    @update:value="handleSourceChange"
                  />
                </n-form-item>
                <n-form-item label="필드">
                  <n-select
                    v-model:value="mappingForm.field"
                    :options="fieldOptions"
                    filterable
                    placeholder="필드를 선택해 주세요"
                  />
                </n-form-item>
                <n-form-item label="보조 필드">
                  <n-select
                    v-model:value="mappingForm.secondary_field"
                    :options="secondaryFieldOptions"
                    filterable
                    clearable
                    placeholder="필요할 때만 선택해 주세요"
                  />
                </n-form-item>
                <n-form-item label="샘플 자산">
                  <n-select
                    v-model:value="previewAssetId"
                    :options="assetOptions"
                    filterable
                    clearable
                    placeholder="미리볼 자산을 선택해 주세요"
                  />
                </n-form-item>
                <n-form-item v-if="!mappingForm.repeat_direction" label="집계 방식">
                  <n-select
                    v-model:value="mappingForm.aggregate_mode"
                    :options="aggregateOptions"
                    placeholder="집계 방식을 선택해 주세요"
                  />
                </n-form-item>
                <n-form-item label="출력 템플릿">
                  <n-input
                    v-model:value="mappingForm.output_template"
                    placeholder="예: {value} / {secondary} 또는 {value} * {count}"
                  />
                </n-form-item>
                <div class="mapping-help">
                  `{value}` 기본값, `{secondary}` 보조 필드, `{count}` 반복 데이터 개수
                </div>
                <n-form-item label="서식">
                  <n-input v-model:value="mappingForm.format" placeholder="예: YYYY-MM-DD" />
                </n-form-item>
                <n-form-item label="반복 방향">
                  <n-select
                    v-model:value="mappingForm.repeat_direction"
                    :options="repeatDirectionOptions"
                    placeholder="반복 없음"
                  />
                </n-form-item>
                <n-form-item v-if="mappingForm.repeat_direction" label="최대 개수">
                  <n-input-number v-model:value="mappingForm.repeat_max_rows" :min="1" :max="200" />
                </n-form-item>
              </n-form>

              <div class="mapping-side">
                <div class="mapping-preview-panel">
                  <div class="mapping-list-header">데이터 미리보기</div>
                  <div class="mapping-preview-summary">
                    <span v-if="mappingForm.data_source">{{ mappingForm.data_source }}</span>
                    <span v-if="mappingForm.field">.{{ mappingForm.field }}</span>
                    <span v-if="selectedFieldMeta?.is_repeatable" class="mapping-repeat">반복</span>
                    <span v-if="!mappingForm.repeat_direction && mappingForm.aggregate_mode" class="mapping-aggregate">
                      {{ aggregateLabel }}
                    </span>
                  </div>

                  <n-spin :show="previewLoading">
                    <div v-if="!previewAssetId" class="mapping-preview-empty">
                      샘플 자산을 선택하면 실제 데이터를 확인할 수 있습니다.
                    </div>
                    <div v-else-if="!mappingForm.data_source" class="mapping-preview-empty">
                      데이터 소스를 먼저 선택해 주세요.
                    </div>
                    <div v-else-if="!store.dataPreview?.total_rows" class="mapping-preview-empty">
                      선택한 자산에 이 데이터 소스의 값이 없습니다.
                    </div>
                    <div v-else class="mapping-preview-content">
                      <div v-if="previewExampleText" class="mapping-preview-example">
                        예상 출력: {{ previewExampleText }}
                      </div>
                      <div class="mapping-row-list">
                        <div class="mapping-list-header">행 샘플</div>
                        <div class="mapping-table-wrap">
                          <n-scrollbar x-scrollable>
                            <n-data-table
                              :columns="previewTableColumns"
                              :data="previewTableData"
                              :pagination="false"
                              :max-height="360"
                              :scroll-x="previewTableScrollX"
                              size="small"
                              striped
                            />
                          </n-scrollbar>
                        </div>
                        <div v-if="store.dataPreview?.truncated" class="mapping-preview-note">
                          상위 {{ previewRows.length }}개 행만 표시하고 있습니다.
                        </div>
                      </div>
                    </div>
                  </n-spin>
                </div>

                <div class="mapping-list-header">
                  현재 시트 매핑 {{ currentSheetMappings.length }}개
                </div>
                <n-scrollbar style="max-height: 360px">
                  <div v-if="currentSheetMappings.length" class="mapping-list">
                    <button
                      v-for="mapping in currentSheetMappings"
                      :key="mapping.id || `${mapping.sheet_name}-${mapping.cell}`"
                      type="button"
                      class="mapping-item"
                      :class="{ active: isSelectedMapping(mapping) }"
                      @click="selectExistingMapping(mapping)"
                    >
                      <div class="mapping-item-main">
                        <strong>{{ mapping.cell }}</strong>
                        <span>{{ mapping.data_source }}.{{ mapping.field }}</span>
                        <span v-if="mapping.aggregate_mode && !mapping.repeat_direction" class="mapping-aggregate">
                          {{ aggregateOptionMap[mapping.aggregate_mode] || mapping.aggregate_mode }}
                        </span>
                        <span v-if="mapping.repeat_direction" class="mapping-repeat">
                          {{ repeatDirectionMap[mapping.repeat_direction] || mapping.repeat_direction }}
                        </span>
                      </div>
                      <n-button size="tiny" type="error" @click.stop="removeMapping(mapping)">
                        삭제
                      </n-button>
                    </button>
                  </div>
                  <n-empty
                    v-else
                    size="small"
                    description="현재 시트에는 등록된 매핑이 없습니다."
                  />
                </n-scrollbar>
              </div>
            </div>
          </div>
        </n-scrollbar>
      </div>
      <n-empty
        v-else
        size="small"
        description="템플릿을 선택한 뒤 셀을 클릭하면 매핑을 편집할 수 있습니다."
      />

      <template #footer>
        <div class="modal-footer">
          <n-button @click="closeMappingModal">닫기</n-button>
        </div>
      </template>
    </n-modal>
  </PageShell>
</template>

<script setup>
import { computed, h, onMounted, ref, watch } from 'vue'
import { useMessage } from 'naive-ui'
import PageShell from '@/components/common/PageShell.vue'
import FormTemplateList from '@/components/reports/FormTemplateList.vue'
import FormTemplateWorkbookPreview from '@/components/reports/FormTemplateWorkbookPreview.vue'
import { useFormTemplateStore } from '@/stores/formTemplateStore'
import { useAssetStore } from '@/stores/assetStore'

const store = useFormTemplateStore()
const assetStore = useAssetStore()
const message = useMessage()

const showTemplateModal = ref(false)
const showMappingModal = ref(false)
const saving = ref(false)
const selectedTemplateId = ref(null)
const editingTemplate = ref(null)
const uploadFile = ref(null)
const showPreview = ref(true)
const templateForm = ref(emptyTemplateForm())
const selectedCell = ref(null)
const mappingSaving = ref(false)
const mappingForm = ref(emptyMappingForm())
const previewLoading = ref(false)
const previewAssetId = ref(null)

const categoryOptions = [
  { label: '일반', value: 'general' },
  { label: '점검', value: 'inspection' },
  { label: '보안', value: 'security' },
]

const aggregateOptions = [
  { label: '기본값', value: 'value' },
  { label: '첫 번째 값', value: 'first' },
  { label: '개수', value: 'count' },
  { label: '쉼표 연결', value: 'join' },
  { label: '중복 제거 후 연결', value: 'join_unique' },
]

const repeatDirectionOptions = [
  { label: '반복 없음', value: null },
  { label: '아래로', value: 'down' },
  { label: '오른쪽', value: 'right' },
]

const aggregateOptionMap = {
  value: '기본값',
  first: '첫 번째 값',
  count: '개수',
  join: '쉼표 연결',
  join_unique: '중복 제거 후 연결',
}

const repeatDirectionMap = {
  down: '아래로',
  right: '오른쪽',
}

const selectedTemplate = computed(() =>
  store.templates.find((template) => template.id === selectedTemplateId.value) || null,
)

const selectedCellLabel = computed(() =>
  selectedCell.value?.cell
    ? `${selectedCell.value.sheetName || '-'} / ${selectedCell.value.cell}`
    : '',
)

const folderOptions = computed(() =>
  store.folders.map((folder) => ({
    label: folder.name,
    value: folder.id,
  })),
)

const assetOptions = computed(() =>
  assetStore.list.map((asset) => ({
    label: `${asset.asset_code || '-'} ${asset.asset_name || ''}`.trim(),
    value: asset.id,
  })),
)

const sourceOptions = computed(() => {
  const sources = [...new Set(store.fieldCatalog.map((item) => item.data_source))]
  return sources.map((source) => ({ label: source, value: source }))
})

const fieldOptions = computed(() =>
  store.fieldCatalog
    .filter((item) => item.data_source === mappingForm.value.data_source)
    .map((item) => ({
      label: `${item.label} (${item.field})`,
      value: item.field,
    })),
)

const secondaryFieldOptions = computed(() =>
  fieldOptions.value.filter((item) => item.value !== mappingForm.value.field),
)

const selectedFieldMeta = computed(() =>
  store.fieldCatalog.find(
    (item) =>
      item.data_source === mappingForm.value.data_source
      && item.field === mappingForm.value.field,
  ) || null,
)

const aggregateLabel = computed(() =>
  aggregateOptionMap[mappingForm.value.aggregate_mode] || '',
)

const previewRows = computed(() => store.dataPreview?.rows || [])

const previewTableData = computed(() =>
  previewRows.value.map((row) => ({
    row_index: row.row_index,
    ...(row.values || {}),
  })),
)

const previewFieldKeys = computed(() => {
  const firstRow = previewRows.value[0]
  return firstRow ? Object.keys(firstRow.values || {}) : []
})

const previewTableColumns = computed(() => {
  const baseColumn = {
    key: 'row_index',
    title: '#',
    width: 56,
    fixed: 'left',
  }

  const dataColumns = previewFieldKeys.value.map((key) => ({
    key,
    title: key,
    minWidth: 160,
    className: key === mappingForm.value.field ? 'mapping-preview-column-active' : '',
    render: (row) => h(
      'span',
      { class: key === mappingForm.value.field ? 'mapping-preview-cell-active' : '' },
      row[key] || '(빈 값)',
    ),
  }))

  return [baseColumn, ...dataColumns]
})

const previewTableScrollX = computed(() =>
  56 + (previewFieldKeys.value.length * 160),
)

const previewExampleText = computed(() => {
  if (!mappingForm.value.field || !previewRows.value.length || mappingForm.value.repeat_direction) {
    return ''
  }

  const values = previewRows.value
    .map((row) => row.values?.[mappingForm.value.field] ?? '')
    .filter((value) => value !== '')
  const secondaryValues = previewRows.value
    .map((row) => row.values?.[mappingForm.value.secondary_field] ?? '')
    .filter((value) => value !== '')
  const firstValue = values[0] || ''
  const firstSecondaryValue = secondaryValues[0] || ''
  const countValue = previewRows.value.length
  let value = firstValue

  switch (mappingForm.value.aggregate_mode) {
    case 'count':
      value = String(countValue)
      break
    case 'join':
      value = values.join(', ')
      break
    case 'join_unique':
      value = [...new Set(values)].join(', ')
      break
    case 'first':
    case 'value':
    default:
      value = firstValue
      break
  }

  if (mappingForm.value.output_template) {
    return mappingForm.value.output_template
      .replaceAll('{value}', value)
      .replaceAll('{secondary}', firstSecondaryValue)
      .replaceAll('{count}', String(countValue))
  }
  return value
})

const currentSheetMappings = computed(() =>
  store.mappings.filter((item) => (item.sheet_name || '') === (selectedCell.value?.sheetName || '')),
)

const canSaveMapping = computed(() =>
  !!selectedTemplate.value
  && !!selectedCell.value?.cell
  && !!mappingForm.value.data_source
  && !!mappingForm.value.field,
)

const canSubmit = computed(() => {
  if (!templateForm.value.name) {
    return false
  }
  if (!editingTemplate.value && !uploadFile.value) {
    return false
  }
  return true
})

function emptyTemplateForm() {
  return {
    name: '',
    category: 'general',
    description: '',
    folder_id: null,
    is_active: true,
  }
}

function emptyMappingForm() {
  return {
    data_source: null,
    field: null,
    secondary_field: null,
    format: '',
    aggregate_mode: 'value',
    output_template: '',
    repeat_direction: null,
    repeat_max_rows: 10,
  }
}

function handleFileChange({ file }) {
  uploadFile.value = file?.file || null
}

function openCreateModal() {
  editingTemplate.value = null
  templateForm.value = emptyTemplateForm()
  uploadFile.value = null
  showTemplateModal.value = true
}

function openEditModal(template) {
  editingTemplate.value = template
  templateForm.value = {
    name: template.name,
    category: template.category,
    description: template.description || '',
    folder_id: template.folder_id || null,
    is_active: template.is_active,
  }
  uploadFile.value = null
  showTemplateModal.value = true
}

function closeModal() {
  showTemplateModal.value = false
  editingTemplate.value = null
  uploadFile.value = null
}

function resetMappingForm() {
  mappingForm.value = emptyMappingForm()
}

function closeMappingModal() {
  showMappingModal.value = false
}

function togglePreview() {
  showPreview.value = !showPreview.value
}

async function handleSelect(template) {
  selectedTemplateId.value = template?.id || null
  selectedCell.value = null
  closeMappingModal()
  resetMappingForm()
  store.clearDataPreview()
  if (!template?.id) {
    store.clearWorkbookPreview()
    store.mappings = []
    return
  }
  await Promise.all([
    store.fetchMappings(template.id),
    store.fetchFieldCatalog(),
  ])
}

function handleSourceChange() {
  mappingForm.value.field = null
  mappingForm.value.secondary_field = null
  mappingForm.value.aggregate_mode = 'value'
  mappingForm.value.output_template = ''
}

async function loadDataPreview() {
  if (!previewAssetId.value || !mappingForm.value.data_source || !showMappingModal.value) {
    store.clearDataPreview()
    return
  }
  previewLoading.value = true
  try {
    await store.fetchDataPreview(previewAssetId.value, mappingForm.value.data_source)
  } catch (error) {
    store.clearDataPreview()
    message.error(`데이터 미리보기를 불러오지 못했습니다: ${error.message || ''}`)
  } finally {
    previewLoading.value = false
  }
}

function applyMappingToForm(mapping) {
  mappingForm.value = {
    data_source: mapping.data_source,
    field: mapping.field,
    secondary_field: mapping.secondary_field || null,
    format: mapping.format || '',
    aggregate_mode: mapping.aggregate_mode || 'value',
    output_template: mapping.output_template || '',
    repeat_direction: mapping.repeat_direction || null,
    repeat_max_rows: mapping.repeat_max_rows || 10,
  }
}

function handleSelectCell(cellInfo) {
  selectedCell.value = cellInfo
  const existing = store.mappings.find(
    (item) =>
      (item.sheet_name || '') === (cellInfo.sheetName || '')
      && item.cell === cellInfo.cell,
  )
  if (existing) {
    applyMappingToForm(existing)
  } else {
    resetMappingForm()
  }
  showMappingModal.value = true
}

function isSelectedMapping(mapping) {
  return (
    selectedCell.value?.cell === mapping.cell
    && (selectedCell.value?.sheetName || '') === (mapping.sheet_name || '')
  )
}

function selectExistingMapping(mapping) {
  selectedCell.value = {
    sheetName: mapping.sheet_name || '',
    cell: mapping.cell,
  }
  applyMappingToForm(mapping)
  showMappingModal.value = true
}

async function saveSelectedMapping() {
  if (!canSaveMapping.value) {
    return
  }
  mappingSaving.value = true
  try {
    const nextMappings = store.mappings.filter(
      (item) =>
        !(
          (item.sheet_name || '') === (selectedCell.value?.sheetName || '')
          && item.cell === selectedCell.value?.cell
        ),
    )
    nextMappings.push({
      sheet_name: selectedCell.value?.sheetName || null,
      cell: selectedCell.value?.cell,
      data_source: mappingForm.value.data_source,
      field: mappingForm.value.field,
      secondary_field: mappingForm.value.secondary_field || null,
      display_label: '',
      format: mappingForm.value.format || null,
      aggregate_mode: mappingForm.value.repeat_direction ? null : mappingForm.value.aggregate_mode || 'value',
      output_template: mappingForm.value.output_template || null,
      repeat_direction: mappingForm.value.repeat_direction || null,
      repeat_max_rows: mappingForm.value.repeat_direction ? mappingForm.value.repeat_max_rows : null,
      sort_order: nextMappings.length,
    })
    await store.bulkSaveMappings(selectedTemplateId.value, nextMappings)
    message.success('셀 매핑을 저장했습니다.')
    closeMappingModal()
  } catch (error) {
    message.error(`매핑 저장에 실패했습니다: ${error.message || ''}`)
  } finally {
    mappingSaving.value = false
  }
}

async function removeMapping(mapping) {
  try {
    const nextMappings = store.mappings
      .filter((item) => item.id !== mapping.id)
      .map((item, index) => ({ ...item, sort_order: index }))
    await store.bulkSaveMappings(selectedTemplateId.value, nextMappings)
    if (isSelectedMapping(mapping)) {
      resetMappingForm()
    }
    message.success('매핑을 삭제했습니다.')
  } catch (error) {
    message.error(`매핑 삭제에 실패했습니다: ${error.message || ''}`)
  }
}

async function submitTemplate() {
  if (!canSubmit.value) {
    return
  }

  saving.value = true
  try {
    if (editingTemplate.value) {
      await store.update(editingTemplate.value.id, {
        name: templateForm.value.name,
        category: templateForm.value.category,
        description: templateForm.value.description,
        folder_id: templateForm.value.folder_id,
        is_active: templateForm.value.is_active,
      })
      message.success('템플릿 정보를 수정했습니다.')
    } else {
      const formData = new FormData()
      formData.append('name', templateForm.value.name)
      formData.append('category', templateForm.value.category)
      if (templateForm.value.description) {
        formData.append('description', templateForm.value.description)
      }
      if (templateForm.value.folder_id != null) {
        formData.append('folder_id', String(templateForm.value.folder_id))
      }
      formData.append('file', uploadFile.value)
      const created = await store.create(formData)
      message.success('템플릿을 등록했습니다.')
      await handleSelect(created)
    }
    closeModal()
  } catch (error) {
    message.error(`템플릿 저장에 실패했습니다: ${error.message || ''}`)
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await Promise.all([store.fetchFolders(), store.fetchList(), assetStore.fetchList()])
  if (assetStore.list.length > 0) {
    previewAssetId.value = assetStore.list[0].id
  }
  if (store.templates.length > 0) {
    await handleSelect(store.templates[0])
  }
})

watch(selectedTemplateId, () => {
  selectedCell.value = null
  closeMappingModal()
  resetMappingForm()
  store.clearDataPreview()
})

watch(
  () => [previewAssetId.value, mappingForm.value.data_source, showMappingModal.value],
  async ([assetId, dataSource, modalOpen]) => {
    if (!assetId || !dataSource || !modalOpen) {
      store.clearDataPreview()
      return
    }
    await loadDataPreview()
  },
)
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.header-actions {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.page-title {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  color: #0f172a;
}

.page-description {
  margin: 8px 0 0;
  color: #64748b;
}

.page-grid {
  display: grid;
  grid-template-columns: minmax(320px, 380px) minmax(0, 1fr);
  gap: 18px;
  align-items: stretch;
  transition: grid-template-columns 0.2s ease;
}

.page-grid.collapsed {
  grid-template-columns: minmax(320px, 380px);
}

.left-column {
  min-width: 0;
}

.pane-card {
  min-height: 680px;
  background: #fff;
}

.pane-left {
  overflow: hidden;
  width: 100%;
}

.mapping-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.mapping-title {
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
}

.mapping-subtitle {
  margin-top: 4px;
  font-size: 12px;
  color: #64748b;
}

.mapping-modal-content {
  max-height: min(84vh, 980px);
}

.mapping-modal-scroll {
  max-height: min(84vh, 980px);
}

.mapping-body {
  display: grid;
  gap: 14px;
  padding: 24px;
  min-width: 0;
}

.mapping-layout {
  display: grid;
  grid-template-columns: minmax(320px, 380px) minmax(0, 1.25fr);
  gap: 18px;
  align-items: start;
}

.mapping-form {
  min-width: 0;
}

.mapping-side {
  display: grid;
  gap: 14px;
  min-width: 0;
}

.mapping-preview-panel {
  display: grid;
  gap: 10px;
  padding: 14px;
  border: 1px solid #dbe3f0;
  border-radius: 12px;
  background: linear-gradient(180deg, #f8fbff 0%, #ffffff 100%);
  min-width: 0;
}

.mapping-preview-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  font-size: 12px;
  color: #475569;
}

.mapping-preview-empty {
  padding: 20px 12px;
  border: 1px dashed #cbd5e1;
  border-radius: 10px;
  color: #64748b;
  background: rgba(255, 255, 255, 0.8);
}

.mapping-preview-content {
  display: grid;
  gap: 12px;
  min-width: 0;
}

.mapping-row-list {
  display: grid;
  gap: 8px;
  min-width: 0;
}

.mapping-table-wrap {
  width: 100%;
  min-width: 0;
  overflow: hidden;
}

.mapping-preview-note {
  font-size: 12px;
  color: #64748b;
}

.mapping-help {
  margin: -4px 0 12px;
  font-size: 12px;
  color: #64748b;
}

.mapping-preview-example {
  padding: 10px 12px;
  border-radius: 10px;
  background: #eff6ff;
  color: #1d4ed8;
  font-size: 12px;
  font-weight: 600;
}

.mapping-aggregate {
  color: #2563eb;
  font-weight: 600;
}

:deep(.mapping-preview-column-active) {
  background: #f0f7ff;
}

:deep(.mapping-preview-cell-active) {
  display: inline-block;
  width: 100%;
  color: #1d4ed8;
  font-weight: 600;
}

.mapping-list-header {
  font-size: 13px;
  font-weight: 600;
  color: #0f172a;
}

.mapping-list {
  display: grid;
  gap: 8px;
}

.mapping-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #fff;
  text-align: left;
}

.mapping-item.active {
  border-color: #60a5fa;
  background: #eff6ff;
}

.mapping-item-main {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  font-size: 12px;
  color: #334155;
}

.mapping-repeat {
  color: #16a34a;
  font-weight: 600;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

@media (max-width: 1100px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
  }

  .header-actions {
    justify-content: flex-end;
  }

  .page-grid {
    grid-template-columns: 1fr;
  }

  .pane-card {
    min-height: auto;
  }

  .mapping-layout {
    grid-template-columns: 1fr;
  }
}
</style>
