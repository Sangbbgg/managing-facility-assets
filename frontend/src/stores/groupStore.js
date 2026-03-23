import { defineStore } from 'pinia'
import { ref } from 'vue'
import { groupsApi } from '@/api/groupsApi'

export const useGroupStore = defineStore('group', () => {
  const list      = ref([])
  const codeable  = ref([])
  const loading   = ref(false)

  async function fetchList() {
    loading.value = true
    try { list.value = await groupsApi.list() }
    finally { loading.value = false }
  }

  async function fetchCodeable() {
    codeable.value = await groupsApi.codeable()
  }

  async function create(body) {
    const item = await groupsApi.create(body)
    list.value.push(item)
  }

  async function update(id, body) {
    const item = await groupsApi.update(id, body)
    const idx = list.value.findIndex(n => n.id === id)
    if (idx !== -1) list.value[idx] = item
  }

  async function remove(id) {
    await groupsApi.remove(id)
    list.value = list.value.filter(n => n.id !== id)
  }

  return { list, codeable, loading, fetchList, fetchCodeable, create, update, remove }
})
