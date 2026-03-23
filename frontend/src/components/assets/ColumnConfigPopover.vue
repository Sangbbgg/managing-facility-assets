<template>
  <n-popover trigger="click" placement="bottom-end" :width="300" :scrollable="true">
    <template #trigger>
      <n-button size="small">⚙ 컬럼 설정</n-button>
    </template>

    <div style="padding:4px 0;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
        <n-text strong style="font-size:13px;">컬럼 표시/순서</n-text>
        <n-space size="small">
          <n-button size="tiny" @click="checkAll">전체</n-button>
          <n-button size="tiny" @click="uncheckAll">해제</n-button>
          <n-button size="tiny" @click="reset">초기화</n-button>
        </n-space>
      </div>
      <n-text depth="3" style="font-size:11px; display:block; margin-bottom:8px;">
        ⠿ 드래그하여 순서 변경
      </n-text>
      <n-divider style="margin:6px 0;" />

      <div style="max-height:400px; overflow-y:auto;">
        <div
          v-for="(col, idx) in localCols"
          :key="col.key"
          draggable="true"
          @dragstart="onDragStart(idx)"
          @dragover.prevent="onDragOver(idx)"
          @dragleave="dragOverIdx = -1"
          @drop.prevent="onDrop(idx)"
          :style="{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            marginBottom: '4px',
            padding: '4px 6px',
            borderRadius: '4px',
            cursor: 'grab',
            background: dragOverIdx === idx ? '#e8f4ff' : 'transparent',
            border: dragOverIdx === idx ? '1px dashed #4098fc' : '1px solid transparent',
            transition: 'background 0.1s',
          }"
        >
          <span style="color:#bbb; font-size:14px; flex-shrink:0; cursor:grab;">⠿</span>
          <n-checkbox v-model:checked="col.visible" style="flex:1;">
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

const props = defineProps({
  columns:        { type: Array, default: () => [] },
  defaultColumns: { type: Array, default: () => [] },
})
const emit = defineEmits(['update:columns'])

const localCols   = ref([])
const dragIdx     = ref(-1)
const dragOverIdx = ref(-1)

watch(
  () => props.columns,
  (cols) => { localCols.value = cols.map(c => ({ ...c })) },
  { immediate: true, deep: true }
)

function onDragStart(idx) {
  dragIdx.value = idx
}
function onDragOver(idx) {
  dragOverIdx.value = idx
}
function onDrop(idx) {
  if (dragIdx.value === -1 || dragIdx.value === idx) {
    dragOverIdx.value = -1
    return
  }
  const cols = [...localCols.value]
  const [moved] = cols.splice(dragIdx.value, 1)
  cols.splice(idx, 0, moved)
  localCols.value = cols
  dragIdx.value     = -1
  dragOverIdx.value = -1
}

function checkAll()   { localCols.value.forEach(c => c.visible = true) }
function uncheckAll() { localCols.value.forEach(c => c.visible = false) }
function reset() {
  const defaults = props.defaultColumns.length ? props.defaultColumns : props.columns
  localCols.value = defaults.map(c => ({ ...c }))
}
function apply() {
  emit('update:columns', localCols.value.map(c => ({ ...c })))
}
</script>
