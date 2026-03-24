<template>
  <n-layout style="min-height:100vh">
    <n-layout-content style="padding:24px">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px">
        <n-h2 style="margin:0">양식 관리</n-h2>
      </div>

      <FormTemplateList @upload="showUpload = true" @edit="openEditor" />

      <!-- 업로드 모달 -->
      <n-modal v-model:show="showUpload" preset="card" title="새 양식 업로드" style="width:480px">
        <n-form label-placement="left" label-width="80">
          <n-form-item label="양식명">
            <n-input v-model:value="uploadForm.name" placeholder="자산 상세 보고서" />
          </n-form-item>
          <n-form-item label="분류">
            <n-select v-model:value="uploadForm.category" :options="categoryOptions" />
          </n-form-item>
          <n-form-item label="설명">
            <n-input v-model:value="uploadForm.description" type="textarea" :rows="2" />
          </n-form-item>
          <n-form-item label="파일">
            <n-upload
              accept=".xlsx,.xls"
              :max="1"
              @change="handleFileChange"
            >
              <n-button>xlsx 파일 선택</n-button>
            </n-upload>
          </n-form-item>
        </n-form>
        <template #footer>
          <div style="text-align:right;display:flex;gap:8px;justify-content:flex-end">
            <n-button @click="showUpload = false">취소</n-button>
            <n-button
              type="primary"
              :loading="uploading"
              :disabled="!uploadForm.name || !uploadFile"
              @click="doUpload"
            >
              업로드
            </n-button>
          </div>
        </template>
      </n-modal>

      <!-- 매핑 편집 영역 -->
      <n-card v-if="editingTemplate" style="margin-top:24px">
        <template #header>
          <div style="display:flex;align-items:center;gap:12px">
            <span>매핑 편집: {{ editingTemplate.name }}</span>
            <n-button size="small" @click="editingTemplate = null">닫기</n-button>
          </div>
        </template>
        <FormMappingEditor :template-id="editingTemplate.id" />
      </n-card>
    </n-layout-content>
  </n-layout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { useFormTemplateStore } from '@/stores/formTemplateStore'
import FormTemplateList from '@/components/reports/FormTemplateList.vue'
import FormMappingEditor from '@/components/reports/FormMappingEditor.vue'

const store = useFormTemplateStore()
const message = useMessage()

const showUpload = ref(false)
const uploading = ref(false)
const editingTemplate = ref(null)
const uploadFile = ref(null)
const uploadForm = ref({ name: '', category: 'general', description: '' })

const categoryOptions = [
  { label: '일반', value: 'general' },
  { label: '점검', value: 'inspection' },
  { label: '보안', value: 'security' },
]

function handleFileChange({ file }) {
  uploadFile.value = file?.file || null
}

async function doUpload() {
  if (!uploadForm.value.name || !uploadFile.value) return
  uploading.value = true
  try {
    const fd = new FormData()
    fd.append('name', uploadForm.value.name)
    fd.append('category', uploadForm.value.category)
    if (uploadForm.value.description) fd.append('description', uploadForm.value.description)
    fd.append('file', uploadFile.value)
    await store.create(fd)
    message.success('업로드 완료')
    showUpload.value = false
    uploadForm.value = { name: '', category: 'general', description: '' }
    uploadFile.value = null
  } catch (e) {
    message.error('업로드 실패: ' + (e.message || ''))
  } finally {
    uploading.value = false
  }
}

function openEditor(template) {
  editingTemplate.value = template
}

onMounted(() => store.fetchList())
</script>
