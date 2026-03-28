<template>
  <div>
    <ListHeader :title="title" :count="data.length">
      <template #extra>
        <slot name="header-extra" />
      </template>
    </ListHeader>

    <n-data-table
      :columns="columns"
      :data="data"
      :loading="loading"
      :pagination="pagination || false"
      :row-key="(row) => row.id"
      striped
    />
  </div>
</template>

<script setup>
import ListHeader from '@/components/common/ListHeader.vue'

defineProps({
  title:      { type: String,  default: '목록' },
  columns:    { type: Array,   required: true },
  data:       { type: Array,   default: () => [] },
  loading:    { type: Boolean, default: false },
  pagination: { type: [Object, Boolean], default: false },
})
</script>
