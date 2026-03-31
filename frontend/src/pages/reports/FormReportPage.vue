<template>
  <PageShell title="양식 보고서">
    <n-card class="generator-card" :bordered="false">
      <FormReportGenerator />
    </n-card>
    <FormPreviewRenderer />
  </PageShell>
</template>

<script setup>
import PageShell from '@/components/common/PageShell.vue'
import FormReportGenerator from '@/components/reports/FormReportGenerator.vue'
import FormPreviewRenderer from '@/components/reports/FormPreviewRenderer.vue'
</script>

<style scoped>
.generator-card {
  margin-bottom: 16px;
}
</style>
