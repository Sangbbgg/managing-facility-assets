<template>
  <PageShell title="양식 보고서">
    <n-card class="generator-card" :bordered="false">
      <FormReportGenerator @preview-open="openPreviewModal" />
    </n-card>

    <n-modal
      v-model:show="previewModalVisible"
      @update:show="handlePreviewModalChange"
      preset="card"
      title="양식 보고서 미리보기"
      style="width: min(1800px, 96vw)"
      content-style="padding: 16px 20px; overflow: hidden"
    >
      <div class="preview-modal-body">
        <FormPreviewRenderer />
      </div>

      <template #footer>
        <div class="preview-footer">
          <n-button @click="closePreviewModal">닫기</n-button>
        </div>
      </template>
    </n-modal>
  </PageShell>
</template>

<script setup>
import { ref } from 'vue'
import PageShell from '@/components/common/PageShell.vue'
import FormReportGenerator from '@/components/reports/FormReportGenerator.vue'
import FormPreviewRenderer from '@/components/reports/FormPreviewRenderer.vue'
import { useFormTemplateStore } from '@/stores/formTemplateStore'

const store = useFormTemplateStore()
const previewModalVisible = ref(false)

function openPreviewModal() {
  previewModalVisible.value = true
}

function closePreviewModal() {
  previewModalVisible.value = false
  store.clearRenderedPreview()
}

function handlePreviewModalChange(value) {
  previewModalVisible.value = value
  if (!value) {
    store.clearRenderedPreview()
  }
}
</script>

<style scoped>
.generator-card {
  margin-bottom: 16px;
}

.preview-footer {
  display: flex;
  justify-content: flex-end;
}

.preview-modal-body {
  height: min(78vh, 920px);
  min-height: 520px;
  overflow: hidden;
}
</style>
