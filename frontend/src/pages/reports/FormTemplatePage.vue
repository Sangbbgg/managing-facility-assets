<template>
  <PageShell title="양식 템플릿">
    <div class="page-header">
      <div>
        <h2 class="page-title">양식 템플릿 관리</h2>
        <p class="page-description">
          왼쪽에서 템플릿을 관리하고, 오른쪽에서 실제 엑셀 화면처럼 시트를 확인할 수 있습니다.
        </p>
      </div>
      <div class="header-actions">
        <n-button quaternary @click="togglePreview">
          {{ showPreview ? '프리뷰 접기' : '프리뷰 펼치기' }}
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

        <n-card class="mapping-card" :bordered="false">
          <template #header>
            <div class="mapping-header">
              <div>
                <div class="mapping-title">셀 매핑</div>
                <div class="mapping-subtitle">
                  {{ selectedCellLabel || '프리뷰에서 셀을 클릭하세요.' }}
                </div>
              </div>
              <n-button
                type="primary"
                size="small"
                :disabled="!canSaveMapping"
                :loading="mappingSaving"
                @click="saveSelectedMapping"
              >
                매핑 저장
              </n-button>
            </div>
          </template>

          <div v-if="selectedTemplate" class="mapping-body">
            <n-form label-placement="top">
              <n-form-item label="시트 / 셀">
                <n-input :value="selectedCellLabel" readonly placeholder="프리뷰에서 셀을 선택하세요." />
              </n-form-item>
              <n-form-item label="데이터 소스">
                <n-select
                  v-model:value="mappingForm.data_source"
                  :options="sourceOptions"
                  placeholder="데이터 소스를 선택하세요"
                  @update:value="handleSourceChange"
                />
              </n-form-item>
              <n-form-item label="필드">
                <n-select
                  v-model:value="mappingForm.field"
                  :options="fieldOptions"
                  filterable
                  placeholder="필드를 선택하세요"
                />
              </n-form-item>
              <n-form-item label="포맷">
                <n-input v-model:value="mappingForm.format" placeholder="예: YYYY년 MM월 DD일" />
              </n-form-item>
              <n-form-item label="반복 데이터">
                <n-switch v-model:value="mappingForm.is_repeat" />
              </n-form-item>
              <n-form-item v-if="mappingForm.is_repeat" label="최대 행 수">
                <n-input-number v-model:value="mappingForm.repeat_max_rows" :min="1" :max="200" />
              </n-form-item>
            </n-form>

            <div class="mapping-list-header">
              <span>저장된 매핑 {{ currentSheetMappings.length }}개</span>
            </div>
            <n-scrollbar style="max-height: 260px">
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
                    <span v-if="mapping.repeat_direction" class="mapping-repeat">반복</span>
                  </div>
                  <n-button size="tiny" type="error" @click.stop="removeMapping(mapping)">삭제</n-button>
                </button>
              </div>
              <n-empty v-else size="small" description="현재 시트에는 저장된 매핑이 없습니다." />
            </n-scrollbar>
          </div>
          <n-empty v-else size="small" description="템플릿을 선택하면 매핑 편집이 열립니다." />
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
        <n-form-item v-if="editingTemplate" label="활성 상태">
          <n-switch v-model:value="templateForm.is_active" />
        </n-form-item>
        <n-form-item v-else label="엑셀 파일">
          <n-upload accept=".xlsx,.xls" :max="1" @change="handleFileChange">
            <n-button>엑셀 파일 선택</n-button>
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
  </PageShell>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useMessage } from 'naive-ui'
import PageShell from '@/components/common/PageShell.vue'
import FormTemplateList from '@/components/reports/FormTemplateList.vue'
import FormTemplateWorkbookPreview from '@/components/reports/FormTemplateWorkbookPreview.vue'
import { useFormTemplateStore } from '@/stores/formTemplateStore'

const store = useFormTemplateStore()
const message = useMessage()

const showTemplateModal = ref(false)
const saving = ref(false)
const selectedTemplateId = ref(null)
const editingTemplate = ref(null)
const uploadFile = ref(null)
const showPreview = ref(true)
const templateForm = ref(emptyTemplateForm())
const selectedCell = ref(null)
const mappingSaving = ref(false)
const mappingForm = ref(emptyMappingForm())

const categoryOptions = [
  { label: '일반', value: 'general' },
  { label: '점검', value: 'inspection' },
  { label: '보안', value: 'security' },
]

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
    format: '',
    is_repeat: false,
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

function togglePreview() {
  showPreview.value = !showPreview.value
}

async function handleSelect(template) {
  selectedTemplateId.value = template?.id || null
  selectedCell.value = null
  resetMappingForm()
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
}

function handleSelectCell(cellInfo) {
  selectedCell.value = cellInfo
  const existing = store.mappings.find(
    (item) =>
      (item.sheet_name || '') === (cellInfo.sheetName || '')
      && item.cell === cellInfo.cell,
  )
  if (existing) {
    mappingForm.value = {
      data_source: existing.data_source,
      field: existing.field,
      format: existing.format || '',
      is_repeat: !!existing.repeat_direction,
      repeat_max_rows: existing.repeat_max_rows || 10,
    }
  } else {
    resetMappingForm()
  }
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
  mappingForm.value = {
    data_source: mapping.data_source,
    field: mapping.field,
    format: mapping.format || '',
    is_repeat: !!mapping.repeat_direction,
    repeat_max_rows: mapping.repeat_max_rows || 10,
  }
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
      display_label: '',
      format: mappingForm.value.format || null,
      repeat_direction: mappingForm.value.is_repeat ? 'down' : null,
      repeat_max_rows: mappingForm.value.is_repeat ? mappingForm.value.repeat_max_rows : null,
      sort_order: nextMappings.length,
    })
    await store.bulkSaveMappings(selectedTemplateId.value, nextMappings)
    message.success('셀 매핑을 저장했습니다.')
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
      handleSelect(created)
    }
    closeModal()
  } catch (error) {
    message.error(`템플릿 저장에 실패했습니다: ${error.message || ''}`)
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await Promise.all([store.fetchFolders(), store.fetchList()])
  if (store.templates.length > 0) {
    await handleSelect(store.templates[0])
  }
})

watch(selectedTemplateId, () => {
  selectedCell.value = null
  resetMappingForm()
})
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
  grid-template-columns: minmax(340px, 420px) minmax(0, 1fr);
  gap: 18px;
  align-items: stretch;
  transition: grid-template-columns 0.2s ease;
}

.page-grid.collapsed {
  grid-template-columns: minmax(340px, 420px);
}

.left-column {
  display: grid;
  gap: 18px;
}

.pane-card {
  min-height: 680px;
  background: #fff;
}

.pane-left {
  overflow: hidden;
  width: 100%;
}

.mapping-card {
  background: #fff;
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

.mapping-body {
  display: grid;
  gap: 14px;
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
}
</style>
