<template>
  <div class="list-header">
    <n-space justify="space-between" align="center" style="width: 100%">
      <n-space align="center" :size="8">
        <n-text strong>{{ title }}</n-text>
        <n-tag size="small" type="info">총 {{ count }}건</n-tag>
      </n-space>
      <slot name="extra" />
    </n-space>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  count: { type: Number, default: 0 },
})
</script>

<style scoped>
.list-header {
  margin-bottom: 10px;
}
</style>
