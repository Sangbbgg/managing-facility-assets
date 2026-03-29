<template>
  <n-popover v-model:show="visible" trigger="click" placement="bottom-end" :width="420">
    <template #trigger>
      <n-button size="small">컬럼 설정</n-button>
    </template>

    <div style="padding: 4px 0;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <div>
          <n-text strong style="font-size: 13px;">표시 컬럼 선택</n-text>
          <n-text depth="3" style="display: block; font-size: 11px;">
            DB에서 실제 조회 가능한 컬럼만 표시합니다.
          </n-text>
        </div>
        <n-space size="small">
          <n-button size="tiny" @click="checkAll">전체</n-button>
          <n-button size="tiny" @click="uncheckAll">해제</n-button>
          <n-button size="tiny" @click="reset">초기화</n-button>
        </n-space>
      </div>

      <n-divider style="margin: 8px 0;" />

      <div style="max-height: 460px; overflow-y: auto; padding-right: 4px;">
        <div
          v-for="section in sections"
          :key="section.key"
          style="margin-bottom: 12px; border: 1px solid #ececf2; border-radius: 8px; padding: 10px;"
        >
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <div>
              <n-text strong style="font-size: 13px;">{{ section.title }}</n-text>
              <n-text depth="3" style="display: block; font-size: 11px;">
                {{ section.stage }}
              </n-text>
            </div>
            <n-space size="small">
              <n-button size="tiny" tertiary @click="checkSection(section.key)">전체</n-button>
              <n-button size="tiny" tertiary @click="uncheckSection(section.key)">해제</n-button>
            </n-space>
          </div>

          <div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 6px 10px;">
            <n-checkbox
              v-for="column in section.columns"
              :key="column.key"
              v-model:checked="column.visible"
            >
              <span style="font-size: 13px;">{{ column.label }}</span>
            </n-checkbox>
          </div>
        </div>
      </div>

      <n-divider style="margin: 10px 0;" />
      <n-button size="small" type="primary" block @click="apply">적용</n-button>
    </div>
  </n-popover>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const visible = ref(false)

const props = defineProps({
  columns: { type: Array, default: () => [] },
  defaultColumns: { type: Array, default: () => [] },
})

const emit = defineEmits(['update:columns'])

const localCols = ref([])

watch(
  () => props.columns,
  (columns) => {
    localCols.value = columns.map((column) => ({ ...column }))
  },
  { immediate: true, deep: true }
)

const sections = computed(() => {
  const map = new Map()
  for (const column of localCols.value) {
    const sectionKey = column.section || 'misc'
    if (!map.has(sectionKey)) {
      map.set(sectionKey, {
        key: sectionKey,
        title: column.sectionLabel || '기타',
        stage: column.stageLabel || '',
        columns: [],
      })
    }
    map.get(sectionKey).columns.push(column)
  }
  return Array.from(map.values())
})

function checkAll() {
  localCols.value.forEach((column) => {
    column.visible = true
  })
}

function uncheckAll() {
  localCols.value.forEach((column) => {
    column.visible = false
  })
}

function checkSection(sectionKey) {
  localCols.value
    .filter((column) => column.section === sectionKey)
    .forEach((column) => {
      column.visible = true
    })
}

function uncheckSection(sectionKey) {
  localCols.value
    .filter((column) => column.section === sectionKey)
    .forEach((column) => {
      column.visible = false
    })
}

function reset() {
  const defaults = props.defaultColumns.length ? props.defaultColumns : props.columns
  localCols.value = defaults.map((column) => ({ ...column }))
}

function apply() {
  emit(
    'update:columns',
    localCols.value.map((column) => ({ ...column }))
  )
  visible.value = false
}
</script>
