<template>
  <PageShell title="위치 관리">
    <n-card>
      <TreeEditor
        title="위치"
        :nodes="store.list"
        :on-add="store.create"
        :on-update="store.update"
        :on-delete="store.remove"
      />
    </n-card>
  </PageShell>
</template>

<script setup>
import { onMounted } from 'vue'
import PageShell  from '@/components/common/PageShell.vue'
import TreeEditor from '@/components/common/TreeEditor.vue'
import { useLocationStore } from '@/stores/locationStore'

const store = useLocationStore()
onMounted(() => store.fetchList())
</script>
