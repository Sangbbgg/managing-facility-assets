import { defineStore } from 'pinia'
import { ref } from 'vue'
import { assetsApi } from '@/api/assetsApi'

export const useAssetStore = defineStore('asset', () => {
  const list    = ref([])
  const current = ref(null)
  const loading = ref(false)
  const total   = ref(0)

  async function fetchList(params = {}) {
    loading.value = true
    try {
      const data = await assetsApi.list(params)
      list.value  = data.items ?? data
      total.value = data.total ?? data.length
    } finally { loading.value = false }
  }

  async function fetchOne(id) { current.value = await assetsApi.get(id) }

  async function create(body) {
    const item = await assetsApi.create(body)
    list.value.unshift(item)
    return item
  }

  async function update(id, body) {
    const item = await assetsApi.update(id, body)
    const idx = list.value.findIndex(a => a.id === id)
    if (idx !== -1) list.value[idx] = item
    return item
  }

  async function remove(id) {
    await assetsApi.remove(id)
    list.value = list.value.filter(a => a.id !== id)
  }

  return { list, current, loading, total, fetchList, fetchOne, create, update, remove }
})
