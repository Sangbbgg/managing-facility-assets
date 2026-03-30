<template>
  <div class="template-list">
    <ListHeader title="템플릿 목록" :count="store.templates.length">
      <template #extra>
        <n-button type="primary" @click="$emit('create')">새 템플릿 등록</n-button>
      </template>
    </ListHeader>

    <n-data-table
      :columns="columns"
      :data="store.templates"
      :loading="store.loading"
      :row-key="row => row.id"
      size="small"
      striped
      :single-line="false"
      :row-props="rowProps"
    />
  </div>
</template>

<script setup>
import { computed, h } from 'vue'
import { NButton, NSpace, NTag, useDialog, useMessage } from 'naive-ui'
import ListHeader from '@/components/common/ListHeader.vue'
import { useFormTemplateStore } from '@/stores/formTemplateStore'

const props = defineProps({
  selectedId: {
    type: Number,
    default: null,
  },
})

const emit = defineEmits(['create', 'select', 'edit'])
const store = useFormTemplateStore()
const message = useMessage()
const dialog = useDialog()

const categoryLabel = {
  general: '일반',
  inspection: '점검',
  security: '보안',
}

const columns = computed(() => [
  {
    title: '템플릿명',
    key: 'name',
    minWidth: 150,
    render: (row) => h('div', { class: 'name-cell' }, [
      h('div', { class: 'name-title' }, row.name),
      h('div', { class: 'name-meta' }, row.file_name),
    ]),
  },
  {
    title: '분류',
    key: 'category',
    width: 88,
    render: (row) => h(NTag, { size: 'small', bordered: false }, () => categoryLabel[row.category] || row.category),
  },
  {
    title: '매핑 수',
    key: 'mapping_count',
    width: 84,
  },
  {
    title: '상태',
    key: 'is_active',
    width: 84,
    render: (row) => h(
      NTag,
      { size: 'small', type: row.is_active ? 'success' : 'default', bordered: false },
      () => (row.is_active ? '활성' : '비활성'),
    ),
  },
  {
    title: '작업',
    key: 'actions',
    width: 130,
    render: (row) => h(NSpace, { size: 4, justify: 'end' }, () => [
      h(NButton, {
        size: 'tiny',
        onClick: (event) => {
          event.stopPropagation()
          emit('edit', row)
        },
      }, () => '수정'),
      h(NButton, {
        size: 'tiny',
        type: 'error',
        onClick: (event) => {
          event.stopPropagation()
          handleDelete(row)
        },
      }, () => '삭제'),
    ]),
  },
])

function rowProps(row) {
  return {
    class: row.id === props.selectedId ? 'template-row selected' : 'template-row',
    onClick: () => emit('select', row),
  }
}

function handleDelete(row) {
  dialog.warning({
    title: '템플릿 삭제',
    content: `"${row.name}" 템플릿을 삭제하시겠습니까?`,
    positiveText: '삭제',
    negativeText: '취소',
    onPositiveClick: async () => {
      try {
        await store.remove(row.id)
        message.success('템플릿을 삭제했습니다.')
        if (row.id === props.selectedId) {
          emit('select', null)
        }
      } catch {
        message.error('템플릿 삭제에 실패했습니다.')
      }
    },
  })
}
</script>

<style scoped>
.template-list :deep(.template-row) {
  cursor: pointer;
}

.template-list :deep(.template-row.selected td) {
  background: #eef6ff;
}

.name-cell {
  display: grid;
  gap: 4px;
  white-space: normal;
}

.name-title {
  font-weight: 600;
  color: #1f2937;
}

.name-meta {
  font-size: 12px;
  color: #6b7280;
  word-break: break-all;
}
</style>
