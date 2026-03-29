<template>
  <PageShell title="이벤트 로그 (evtx) 업로드">
    <n-card style="max-width: 560px">
      <n-space vertical>
        <n-upload accept=".evtx" :max="10" multiple :custom-request="() => {}" @change="handleChange">
          <n-upload-dragger>
            <n-text>.evtx 파일을 드래그하거나 클릭해서 선택</n-text>
          </n-upload-dragger>
        </n-upload>

        <n-form label-placement="left" label-width="100">
          <n-form-item label="자산 ID">
            <n-input-number v-model:value="assetId" :min="1" placeholder="자산 ID 입력" style="width: 100%" />
          </n-form-item>
          <n-form-item label="기록 일자">
            <n-date-picker v-model:value="recordDate" type="date" style="width: 100%" />
          </n-form-item>
        </n-form>

        <n-button
          type="primary"
          :loading="loading"
          :disabled="!files.length || !assetId || !recordDate"
          @click="upload"
        >
          업로드
        </n-button>
      </n-space>
    </n-card>
  </PageShell>
</template>

<script setup>
import { ref } from 'vue'
import { useMessage } from 'naive-ui'

import { evtxApi } from '@/api/evtxApi'
import PageShell from '@/components/common/PageShell.vue'

const message = useMessage()
const files = ref([])
const assetId = ref(null)
const recordDate = ref(null)
const loading = ref(false)

function handleChange({ fileList }) {
  files.value = fileList
}

function toDateStr(ts) {
  const date = new Date(ts)
  const yyyy = date.getFullYear()
  const mm = String(date.getMonth() + 1).padStart(2, '0')
  const dd = String(date.getDate()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd}`
}

async function upload() {
  if (!files.value.length || !assetId.value || !recordDate.value) return

  loading.value = true
  try {
    const formData = new FormData()
    for (const file of files.value) {
      formData.append('files', file.file)
    }
    formData.append('asset_id', assetId.value)
    formData.append('record_date', toDateStr(recordDate.value))

    const data = await evtxApi.upload(formData)
    message.success(`업로드 완료, 이벤트 유형 ${data.parsed_event_types}건 파싱`)
    files.value = []
  } catch (error) {
    message.error(error.message || '업로드 실패')
  } finally {
    loading.value = false
  }
}
</script>
