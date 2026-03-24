<template>
  <div>
    <div style="display:flex;justify-content:flex-end;margin-bottom:12px">
      <n-button type="primary" @click="$emit('upload')">+ 새 양식 업로드</n-button>
    </div>
    <n-data-table
      :columns="columns"
      :data="store.templates"
      :loading="store.loading"
      :row-key="r => r.id"
      @update:checked-row-keys="k => $emit('select', k[0])"
    />
  </div>
</template>

<script setup>
import { h, computed } from 'vue'
import { NButton, NTag, NSpace, useMessage } from 'naive-ui'
import { useFormTemplateStore } from '@/stores/formTemplateStore'

const emit = defineEmits(['upload', 'select', 'edit'])
const store = useFormTemplateStore()
const message = useMessage()

const categoryLabel = { general: '일반', inspection: '점검', security: '보안' }

const columns = [
  { title: '양식명', key: 'name', ellipsis: true },
  { title: '분류', key: 'category', width: 80, render: r => h(NTag, { size: 'small' }, () => categoryLabel[r.category] || r.category) },
  { title: '매핑 수', key: 'mapping_count', width: 80 },
  { title: '상태', key: 'is_active', width: 80, render: r => h(NTag, { type: r.is_active ? 'success' : 'default', size: 'small' }, () => r.is_active ? '활성' : '비활성') },
  { title: '파일명', key: 'file_name', ellipsis: true },
  {
    title: '작업', key: 'actions', width: 140,
    render(row) {
      return h(NSpace, {}, () => [
        h(NButton, { size: 'tiny', onClick: () => emit('edit', row) }, () => '매핑 편집'),
        h(NButton, { size: 'tiny', type: 'error', onClick: () => handleDelete(row.id) }, () => '삭제'),
      ])
    },
  },
]

async function handleDelete(id) {
  try {
    await store.remove(id)
    message.success('삭제되었습니다')
  } catch {
    message.error('삭제 실패')
  }
}
</script>
