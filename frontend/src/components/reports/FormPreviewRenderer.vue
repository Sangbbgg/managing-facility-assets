<template>
  <div class="form-preview-container">
    <n-spin :show="store.loading">
      <div v-if="store.previewHtml" class="preview-content" v-html="store.previewHtml" />
      <n-empty v-else description="양식과 자산을 선택하고 미리보기를 클릭하세요" style="padding:40px 0" />
    </n-spin>
  </div>
</template>

<script setup>
import { useFormTemplateStore } from '@/stores/formTemplateStore'
const store = useFormTemplateStore()
</script>

<style scoped>
.form-preview-container {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  overflow-x: auto;
  background: #fff;
  min-height: 200px;
}
.preview-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
}
.preview-content :deep(td) {
  border: 1px solid #C4A882;
  padding: 6px 8px;
  font-size: 12px;
}
</style>
