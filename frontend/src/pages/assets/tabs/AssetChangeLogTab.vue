<template>
  <div>
    <n-data-table
      :columns="columns"
      :data="logs"
      :loading="loading"
      size="small"
      :max-height="420"
      :pagination="{ pageSize: 20 }"
    />
    <n-empty v-if="!loading && !logs.length" description="변경 이력이 없습니다" style="margin-top:24px;" />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import client from '@/api/client'

const props = defineProps({ assetId: { type: Number, required: true } })

const logs    = ref([])
const loading = ref(false)

const columns = [
  { title: '변경일시', key: 'changed_at', width: 160, render: r => r.changed_at?.slice(0, 16) ?? '-' },
  { title: '변경자',   key: 'changed_by', width: 100 },
  { title: '필드명',   key: 'field_name', width: 120 },
  { title: '이전값',   key: 'old_value',  width: 160, ellipsis: { tooltip: true } },
  { title: '새값',     key: 'new_value',  width: 160, ellipsis: { tooltip: true } },
  { title: '사유',     key: 'reason',     width: 200, ellipsis: { tooltip: true } },
]

async function load(id) {
  if (!id) return
  loading.value = true
  try {
    const res = await client.get(`/api/assets/${id}/change-log`)
    logs.value = res.data
  } catch { logs.value = [] }
  finally { loading.value = false }
}

watch(() => props.assetId, load, { immediate: true })
</script>
