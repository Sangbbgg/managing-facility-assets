<template>
  <n-popover trigger="click" placement="bottom-end" :width="280">
    <template #trigger>
      <n-button size="small">⚙ 컬럼 설정</n-button>
    </template>

    <div style="padding:4px 0;">
      <n-text strong style="font-size:13px;">표시할 컬럼 선택</n-text>
      <n-divider style="margin:8px 0;" />
      <div
        v-for="col in localCols"
        :key="col.key"
        style="display:flex; align-items:center; gap:8px; margin-bottom:6px;"
      >
        <n-checkbox v-model:checked="col.visible">{{ col.label }}</n-checkbox>
      </div>
      <n-divider style="margin:8px 0;" />
      <n-button size="small" type="primary" block @click="apply">적용</n-button>
    </div>
  </n-popover>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  columns: { type: Array, default: () => [] },
})
const emit = defineEmits(['update:columns'])

const localCols = ref([])

watch(
  () => props.columns,
  (cols) => { localCols.value = cols.map(c => ({ ...c })) },
  { immediate: true, deep: true }
)

function apply() {
  emit('update:columns', localCols.value.map(c => ({ ...c })))
}
</script>
