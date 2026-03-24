<template>
  <n-layout style="min-height:100vh">
    <n-layout-content style="padding:24px">
      <n-h2 style="margin-bottom:20px">양식 보고서</n-h2>
      <n-card style="margin-bottom:16px">
        <FormReportGenerator />
      </n-card>
      <FormPreviewRenderer />
    </n-layout-content>
  </n-layout>
</template>

<script setup>
import FormReportGenerator from '@/components/reports/FormReportGenerator.vue'
import FormPreviewRenderer from '@/components/reports/FormPreviewRenderer.vue'
</script>
