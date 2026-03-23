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
    const item = await locationsApi.create(body)
    list.value.push(item)
  }

  async function update(id, body) {
    const item = await locationsApi.update(id, body)
    const idx = list.value.findIndex(n => n.id === id)
    if (idx !== -1) list.value[idx] = item
  }

  async function remove(id) {
    await locationsApi.remove(id)
    list.value = list.value.filter(n => n.id !== id)
  }

  return { list, loading, fetchList, create, update, remove }
})
