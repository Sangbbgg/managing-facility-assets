<template>
  <n-button :loading="loading" @click="handleClick">
    <template #icon><n-icon><DownloadOutline /></n-icon></template>
    엑셀 내보내기
  </n-button>
</template>

<script setup>
import { ref } from 'vue'
import { DownloadOutline } from '@vicons/ionicons5'

const props = defineProps({ onClick: { type: Function, required: true } })
const loading = ref(false)

async function handleClick() {
  loading.value = true
  try { await props.onClick() }
  finally { loading.value = false }
}
</script>
