<template>
  <n-space>
    <n-select
      v-model:value="selectedId"
      :options="options"
      placeholder="레이아웃 선택"
      style="width:180px;"
      clearable
      @update:value="onSelect"
    />
    <n-button size="small" @click="showSave = true">💾 저장</n-button>
    <n-button
      v-if="selectedId"
      size="small"
      @click="handleSetDefault"
    >★ 기본</n-button>
    <n-button
      v-if="selectedId"
      size="small"
      type="error"
      @click="handleDelete"
    >삭제</n-button>

    <!-- 저장 모달 -->
    <n-modal v-model:show="showSave" preset="dialog" title="레이아웃 저장">
      <n-input v-model:value="saveName" placeholder="레이아웃 이름 입력" />
      <template #action>
        <n-button type="primary" @click="handleSave">저장</n-button>
      </template>
    </n-modal>
  </n-space>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { useLayoutStore } from '@/stores/layoutStore'

const props = defineProps({
  columns:    { type: Array, default: () => [] },
  pageKey:    { type: String, default: 'asset_list' },
})
const emit = defineEmits(['apply'])

const message     = useMessage()
const layoutStore = useLayoutStore()
const selectedId  = ref(null)
const showSave    = ref(false)
const saveName    = ref('')

const options = computed(() =>
  layoutStore.list.map(l => ({
    label: l.is_default ? `★ ${l.name}` : l.name,
    value: l.id,
  }))
)

function onSelect(id) {
  if (!id) return
  const layout = layoutStore.list.find(l => l.id === id)
  if (layout) {
    layoutStore.applyCurrent(layout)
    emit('apply', layout.columns_json)
  }
}

async function handleSave() {
  if (!saveName.value.trim()) return
  try {
    const item = await layoutStore.create({
      name:         saveName.value.trim(),
      page_key:     props.pageKey,
      columns_json: props.columns,
      is_default:   false,
    })
    selectedId.value = item.id
    showSave.value = false
    saveName.value = ''
    message.success('레이아웃이 저장되었습니다')
  } catch { message.error('저장 실패') }
}

async function handleSetDefault() {
  if (!selectedId.value) return
  try {
    await layoutStore.setDefault(selectedId.value)
    message.success('기본 레이아웃으로 설정되었습니다')
  } catch { message.error('설정 실패') }
}

async function handleDelete() {
  if (!selectedId.value) return
  try {
    await layoutStore.remove(selectedId.value)
    selectedId.value = null
    message.success('삭제되었습니다')
  } catch { message.error('삭제 실패') }
}

onMounted(() => layoutStore.fetchList(props.pageKey))
</script>
