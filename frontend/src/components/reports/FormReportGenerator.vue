<template>
  <div style="display:flex;gap:16px;align-items:flex-end;flex-wrap:wrap">
    <div style="min-width:200px">
      <div style="margin-bottom:4px;font-size:13px;color:#555">양식 선택</div>
      <n-select
        v-model:value="selectedTemplate"
        :options="templateOptions"
        placeholder="양식을 선택하세요"
      />
    </div>
    <div style="min-width:280px">
      <div style="margin-bottom:4px;font-size:13px;color:#555">자산 선택</div>
      <n-select
        v-model:value="selectedAsset"
        :options="assetOptions"
        filterable
        placeholder="자산을 검색하세요"
      />
    </div>
    <n-button
      type="primary"
      :disabled="!canGenerate"
      :loading="store.loading"
      @click="handlePreview"
    >
      미리보기
    </n-button>
    <n-button
      :disabled="!canGenerate"
      @click="handleDownload"
    >
      xlsx 다운로드
    </n-button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { useFormTemplateStore } from '@/stores/formTemplateStore'
import { useAssetStore } from '@/stores/assetStore'

const store = useFormTemplateStore()
const assetStore = useAssetStore()
const message = useMessage()

const selectedTemplate = ref(null)
const selectedAsset = ref(null)

const templateOptions = computed(() =>
  store.templates.filter(t => t.is_active).map(t => ({ label: t.name, value: t.id }))
)

const assetOptions = computed(() =>
  assetStore.list.map(a => ({
    label: `${a.asset_code} ${a.asset_name}`,
    value: a.id,
  }))
)

const canGenerate = computed(() => selectedTemplate.value && selectedAsset.value)

async function handlePreview() {
  try {
    await store.fetchPreview(selectedTemplate.value, selectedAsset.value)
  } catch (e) {
    message.error('미리보기 실패: ' + (e.message || ''))
  }
}

async function handleDownload() {
  try {
    await store.downloadReport(selectedTemplate.value, selectedAsset.value)
    message.success('다운로드 완료')
  } catch (e) {
    message.error('다운로드 실패: ' + (e.message || ''))
  }
}

onMounted(async () => {
  await Promise.all([
    store.fetchList({ is_active: true }),
    assetStore.fetchList(),
  ])
})
</script>
