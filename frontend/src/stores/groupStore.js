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
    await groupsApi.create(body)
    await fetchList()
    await fetchCodeable()
  }

  async function update(id, body) {
    await groupsApi.update(id, body)
    await fetchList()
    await fetchCodeable()
  }

  async function remove(id) {
    await groupsApi.remove(id)
    await fetchList()
    await fetchCodeable()
  }

  return { list, codeable, loading, fetchList, fetchCodeable, create, update, remove }
})
