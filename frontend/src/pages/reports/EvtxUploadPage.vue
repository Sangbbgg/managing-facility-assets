<template>
  <PageShell title="이벤트 로그 (evtx) 업로드">
    <n-card style="max-width:560px">
      <n-space vertical>
        <n-upload
          accept=".evtx"
          :max="10"
          multiple
          :custom-request="() => {}"
          @change="handleChange"
        >
          <n-upload-dragger>
            <n-text>.evtx 파일을 드래그하거나 클릭하여 선택</n-text>
          </n-upload-dragger>
        </n-upload>
        <n-form label-placement="left" label-width="100">
          <n-form-item label="자산 ID">
            <n-input-number v-model:value="assetId" :min="1" placeholder="자산 ID 입력" style="width:100%" />
          </n-form-item>
          <n-form-item label="기록 일자">
            <n-date-picker v-model:value="recordDate" type="date" style="width:100%" />
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
import PageShell from '@/components/common/PageShell.vue'
import client from '@/api/client'

const message = useMessage()
const files = ref([])
const assetId = ref(null)
const recordDate = ref(null)
const loading = ref(false)

function handleChange({ fileList }) { files.value = fileList }

function toDateStr(ts) {
  const d = new Date(ts)
  const yyyy = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd}`
}

async function upload() {
  if (!files.value.length || !assetId.value || !recordDate.value) return
  loading.value = true
  try {
    const form = new FormData()
    for (const f of files.value) {
      form.append('files', f.file)
    }
    form.append('asset_id', assetId.value)
    form.append('record_date', toDateStr(recordDate.value))
    const res = await client.post('/api/evtx/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 120000,
    })
    message.success(`업로드 완료 — 이벤트 유형 ${res.data.parsed_event_types}건 파싱`)
    files.value = []
  } catch (e) {
    message.error(e.message || '업로드 실패')
  } finally {
    loading.value = false
  }
}
</script>
