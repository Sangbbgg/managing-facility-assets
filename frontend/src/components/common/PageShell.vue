<template>
  <div>
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px">
      <n-h3 style="margin:0">{{ title }}</n-h3>
      <n-space>
        <slot name="actions" />
      </n-space>
    </div>
    <slot />
  </div>
</template>

<script setup>
defineProps({ title: { type: String, required: true } })
</script>
