<template>
  <div>
    <ListHeader title="변경 이력" :count="logs.length" />
    <div class="table-scroll-wrap">
      <div class="table-scroll-inner" style="width: 980px;">
        <n-data-table
          :columns="columns"
          :data="logs"
          :loading="loading"
          size="small"
          :max-height="420"
          :pagination="{ pageSize: 20 }"
          :scroll-x="980"
        />
      </div>
    </div>
    <n-empty v-if="!loading && !logs.length" description="변경 이력이 없습니다." style="margin-top: 24px" />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

import { assetsApi } from '@/api/assetsApi'
import ListHeader from '@/components/common/ListHeader.vue'

const props = defineProps({ assetId: { type: Number, required: true } })

const logs = ref([])
const loading = ref(false)

const columns = [
  { title: '변경일시', key: 'changed_at', width: 160, render: (row) => row.changed_at?.slice(0, 16) ?? '-' },
  { title: '변경자', key: 'changed_by', width: 100 },
  { title: '필드명', key: 'field_name', width: 120 },
  { title: '이전값', key: 'old_value', width: 160, ellipsis: { tooltip: true } },
  { title: '새값', key: 'new_value', width: 160, ellipsis: { tooltip: true } },
  { title: '사유', key: 'reason', width: 200, ellipsis: { tooltip: true } },
]

async function load(id) {
  if (!id) return
  loading.value = true
  try {
    logs.value = await assetsApi.changeLog(id)
  } catch {
    logs.value = []
  } finally {
    loading.value = false
  }
}

watch(() => props.assetId, load, { immediate: true })
</script>

<style scoped>
.table-scroll-wrap {
  overflow-x: auto;
  padding-bottom: 4px;
  width: 100%;
}

.table-scroll-inner {
  max-width: none;
}
</style>
