<template>
  <n-popover v-model:show="visible" trigger="click" placement="bottom-end" :width="280">
    <template #trigger>
      <n-button size="small">⚙ 컬럼 설정</n-button>
    </template>

    <div style="padding:4px 0;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
        <n-text strong style="font-size:13px;">표시할 컬럼 선택</n-text>
        <n-space size="small">
          <n-button size="tiny" @click="checkAll">전체</n-button>
          <n-button size="tiny" @click="uncheckAll">해제</n-button>
          <n-button size="tiny" @click="reset">초기화</n-button>
        </n-space>
      </div>
      <n-text depth="3" style="font-size:11px; display:block; margin-bottom:6px;">
        컬럼 순서는 헤더를 드래그하여 변경하세요
      </n-text>
      <n-divider style="margin:6px 0;" />

      <div style="max-height:400px; overflow-y:auto;">
        <div
          v-for="col in localCols"
          :key="col.key"
          style="display:flex; align-items:center; gap:8px; margin-bottom:4px; padding:3px 4px;"
        >
          <n-checkbox v-model:checked="col.visible">
            <span style="font-size:13px;">{{ col.label }}</span>
          </n-checkbox>
        </div>
      </div>

      <n-divider style="margin:8px 0;" />
      <n-button size="small" type="primary" block @click="apply">적용</n-button>
    </div>
  </n-popover>
</template>

<script setup>
import { ref, watch } from 'vue'

const visible = ref(false)

const props = defineProps({
  columns:        { type: Array, default: () => [] },
  defaultColumns: { type: Array, default: () => [] },
})
const emit = defineEmits(['update:columns'])

const localCols = ref([])

watch(
  () => props.columns,
  (cols) => { localCols.value = cols.map(c => ({ ...c })) },
  { immediate: true, deep: true }
)

function checkAll()   { localCols.value.forEach(c => c.visible = true) }
function uncheckAll() { localCols.value.forEach(c => c.visible = false) }
function reset() {
  const defaults = props.defaultColumns.length ? props.defaultColumns : props.columns
  localCols.value = defaults.map(c => ({ ...c }))
}
function apply() {
  emit('update:columns', localCols.value.map(c => ({ ...c })))
  visible.value = false
}
</script>
