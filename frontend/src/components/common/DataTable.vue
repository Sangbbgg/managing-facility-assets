<template>
  <n-data-table
    :columns="columns"
    :data="data"
    :loading="loading"
    :pagination="pagination || false"
    :row-key="(row) => row.id"
    striped
  />
</template>

<script setup>
defineProps({
  columns:    { type: Array,   required: true },
  data:       { type: Array,   default: () => [] },
  loading:    { type: Boolean, default: false },
  pagination: { type: [Object, Boolean], default: false },
})
</script>
