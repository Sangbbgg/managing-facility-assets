<template>
  <PageShell title="양식 템플릿">
    <div class="page-header">
      <div>
        <h2 class="page-title">양식 템플릿 관리</h2>
        <p class="page-description">
          왼쪽에서 템플릿을 관리하고, 오른쪽에서 실제 엑셀 화면처럼 시트를 확인할 수 있습니다.
        </p>
      </div>
    </div>

    <div class="page-grid">
      <n-card class="pane-card pane-left" :bordered="false">
        <FormTemplateList
          :selected-id="selectedTemplateId"
          @create="openCreateModal"
          @edit="openEditModal"
          @select="handleSelect"
        />
      </n-card>

      <FormTemplateWorkbookPreview :template="selectedTemplate" />
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
import { computed, onMounted, ref } from 'vue'
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
const templateForm = ref(emptyTemplateForm())

const categoryOptions = [
  { label: '일반', value: 'general' },
  { label: '점검', value: 'inspection' },
  { label: '보안', value: 'security' },
]

const selectedTemplate = computed(() =>
  store.templates.find((template) => template.id === selectedTemplateId.value) || null,
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
    is_active: true,
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

async function handleSelect(template) {
  selectedTemplateId.value = template?.id || null
  if (!template?.id) {
    store.clearWorkbookPreview()
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
  await store.fetchList()
  if (store.templates.length > 0) {
    await handleSelect(store.templates[0])
  }
})
</script>

<style scoped>
.page-header {
  margin-bottom: 18px;
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
  grid-template-columns: minmax(360px, 420px) minmax(0, 1fr);
  gap: 18px;
  align-items: stretch;
}

.pane-card {
  min-height: 680px;
  background: #fff;
}

.pane-left {
  overflow: hidden;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

@media (max-width: 1100px) {
  .page-grid {
    grid-template-columns: 1fr;
  }

  .pane-card {
    min-height: auto;
  }
}
</style>
