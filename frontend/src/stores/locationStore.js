import { defineStore } from 'pinia'
import { ref } from 'vue'
import { locationsApi } from '@/api/locationsApi'

export const useLocationStore = defineStore('location', () => {
  const list    = ref([])
  const loading = ref(false)

  async function fetchList() {
    loading.value = true
    try { list.value = await locationsApi.list() }
    finally { loading.value = false }
  }

  async function create(body) {
    await locationsApi.create(body)
    await fetchList()
  }

  async function update(id, body) {
    await locationsApi.update(id, body)
    await fetchList()
  }

  async function remove(id) {
    await locationsApi.remove(id)
    await fetchList()
  }

  return { list, loading, fetchList, create, update, remove }
})
