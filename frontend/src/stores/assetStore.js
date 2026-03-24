import { defineStore } from 'pinia'
import { ref } from 'vue'
import client from '@/api/client'

export const useAssetStore = defineStore('asset', () => {
  const list = ref([])
  const loading = ref(false)

  async function fetchList(params = {}) {
    loading.value = true
    try {
      const { data } = await client.get('/api/assets', { params })
      list.value = Array.isArray(data) ? data : (data.items || [])
    } finally {
      loading.value = false
    }
  }

  return { list, loading, fetchList }
})
