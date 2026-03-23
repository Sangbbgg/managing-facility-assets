import { defineStore } from 'pinia'
import { ref } from 'vue'
import { layoutsApi } from '@/api/layoutsApi'

export const useLayoutStore = defineStore('layout', () => {
  const list    = ref([])
  const current = ref(null)
  const loading = ref(false)

  async function fetchList(pageKey = 'asset_list') {
    loading.value = true
    try { list.value = await layoutsApi.list(pageKey) }
    finally { loading.value = false }
  }

  async function create(body) {
    const item = await layoutsApi.create(body)
    list.value.push(item)
    return item
  }

  async function update(id, body) {
    const item = await layoutsApi.update(id, body)
    const idx = list.value.findIndex(l => l.id === id)
    if (idx !== -1) list.value[idx] = item
    return item
  }

  async function remove(id) {
    await layoutsApi.remove(id)
    list.value = list.value.filter(l => l.id !== id)
    if (current.value?.id === id) current.value = null
  }

  async function setDefault(id) {
    await layoutsApi.setDefault(id)
    list.value.forEach(l => { l.is_default = (l.id === id) })
  }

  function applyCurrent(layout) { current.value = layout }

  return { list, current, loading, fetchList, create, update, remove, setDefault, applyCurrent }
})
