<template>
  <div>
    <n-space vertical :size="16">
      <!-- 수집 스크립트 목록 -->
      <n-card title="수집 스크립트" size="small">
        <n-spin :show="scriptsLoading">
          <ListHeader title="수집 스크립트 목록" :count="scripts.length" />
          <n-space wrap>
            <n-button
              v-for="s in scripts"
              :key="s.script_key"
              size="small"
              @click="downloadScript(s.script_key, s.display_name)"
            >
              📄 {{ s.display_name }}
            </n-button>
          </n-space>
          <div style="margin-top:8px;">
            <n-button type="primary" size="small" @click="downloadBundle">
              ⬇ 통합 스크립트 다운로드 (collect_asset.ps1)
            </n-button>
          </div>
        </n-spin>
      </n-card>

      <!-- 파일 업로드 -->
      <n-card title="수집 데이터 업로드" size="small">
        <n-upload
          ref="uploadRef"
          :max="1"
          accept=".json,.zip"
          :default-upload="false"
          @change="onFileChange"
        >
          <n-upload-dragger>
            <n-text>JSON 또는 ZIP 파일을 드래그하거나 클릭하여 선택</n-text>
            <n-text depth="3" style="display:block; font-size:12px;">.json (PowerShell 수집) 또는 .zip (레거시)</n-text>
          </n-upload-dragger>
        </n-upload>

        <div v-if="selectedFile" style="margin-top:12px;">
          <n-space>
            <n-button :loading="previewing" @click="doPreview">미리보기</n-button>
            <n-button type="primary" :loading="saving" @click="doSave">저장</n-button>
          </n-space>
        </div>

        <!-- 미리보기 결과 -->
        <div v-if="preview" style="margin-top:12px;">
          <n-alert type="info" title="파싱 미리보기">
            <div v-for="(cnt, key) in preview.counts" :key="key">
              <strong>{{ key }}</strong>: {{ cnt }}건
            </div>
            <div v-if="preview.files">
              파일 {{ preview.file_count }}개 감지: {{ preview.files.join(', ') }}
            </div>
          </n-alert>
        </div>

        <!-- 저장 결과 -->
        <div v-if="saveResult" style="margin-top:12px;">
          <n-alert type="success" title="저장 완료">
            <div v-for="(cnt, key) in saveResult.summary" :key="key">
              {{ key }}: {{ cnt }}건
            </div>
          </n-alert>
        </div>
      </n-card>
    </n-space>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { collectApi } from '@/api/collectApi'
import ListHeader from '@/components/common/ListHeader.vue'

const props = defineProps({ assetId: { type: Number, required: true } })
const emit  = defineEmits(['collected'])
const message = useMessage()

const scripts       = ref([])
const scriptsLoading = ref(false)
const selectedFile  = ref(null)
const previewing    = ref(false)
const saving        = ref(false)
const preview       = ref(null)
const saveResult    = ref(null)

async function loadScripts() {
  scriptsLoading.value = true
  try { scripts.value = await collectApi.scripts() }
  catch { scripts.value = [] }
  finally { scriptsLoading.value = false }
}

function onFileChange({ file }) {
  selectedFile.value = file?.file ?? null
  preview.value = null
  saveResult.value = null
}

async function downloadScript(key, name) {
  try {
    const res = await collectApi.downloadScript(key)
    triggerDownload(res.data, `collect_${key}.ps1`)
  } catch { message.error('다운로드 실패') }
}

async function downloadBundle() {
  try {
    const res = await collectApi.downloadBundle()
    triggerDownload(res.data, 'collect_asset.ps1')
  } catch { message.error('다운로드 실패') }
}

function triggerDownload(blob, filename) {
  const url = URL.createObjectURL(new Blob([blob]))
  const a = document.createElement('a')
  a.href = url; a.download = filename; a.click()
  URL.revokeObjectURL(url)
}

async function doPreview() {
  if (!selectedFile.value) return
  previewing.value = true
  try {
    const fd = new FormData()
    fd.append('file', selectedFile.value)
    preview.value = await collectApi.parsePreview(props.assetId, fd)
  } catch (e) { message.error(e.message || '미리보기 실패') }
  finally { previewing.value = false }
}

async function doSave() {
  if (!selectedFile.value) return
  saving.value = true
  try {
    const fd = new FormData()
    fd.append('file', selectedFile.value)
    saveResult.value = await collectApi.confirm(props.assetId, fd)
    message.success('저장되었습니다')
    emit('collected')
  } catch (e) { message.error(e.message || '저장 실패') }
  finally { saving.value = false }
}

onMounted(loadScripts)
</script>
