<template>
  <div class="asset-code-preview">
    <n-tag v-if="previewCode" type="info" size="large" style="font-size:15px; font-weight:600; letter-spacing:1px;">
      {{ previewCode }}
    </n-tag>
    <n-text v-else depth="3">그룹과 장비종류를 선택하면 자산코드가 표시됩니다</n-text>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { assetsApi } from '@/api/assetsApi'

const props = defineProps({
  groupId: { type: Number, default: null },
  typeId:  { type: Number, default: null },
})

const previewCode = ref('')

watch(
  () => [props.groupId, props.typeId],
  async ([gid, tid]) => {
    if (gid && tid) {
      try {
        const data = await assetsApi.previewCode(gid, tid)
        previewCode.value = data.preview_code
      } catch {
        previewCode.value = ''
      }
    } else {
      previewCode.value = ''
    }
  },
  { immediate: true }
)
</script>
