import { defineStore } from 'pinia'
import { ref } from 'vue'
import { osCatalogApi, avCatalogApi } from '@/api/catalogsApi'

export const useCatalogStore = defineStore('catalog', () => {
  const osList    = ref([])
  const avList    = ref([])
  const loading   = ref(false)

  async function fetchOs() {
    loading.value = true
    try { osList.value = await osCatalogApi.list() }
    finally { loading.value = false }
  }

  async function fetchAv() {
    loading.value = true
    try { avList.value = await avCatalogApi.list() }
    finally { loading.value = false }
  }

  async function createOs(body)       { const item = await osCatalogApi.create(body); osList.value.push(item) }
  async function updateOs(id, body)   { const item = await osCatalogApi.update(id, body); const idx = osList.value.findIndex(o => o.id === id); if (idx !== -1) osList.value[idx] = item }
  async function removeOs(id)         { await osCatalogApi.remove(id); osList.value = osList.value.filter(o => o.id !== id) }

  async function createAv(body)       { const item = await avCatalogApi.create(body); avList.value.push(item) }
  async function updateAv(id, body)   { const item = await avCatalogApi.update(id, body); const idx = avList.value.findIndex(o => o.id === id); if (idx !== -1) avList.value[idx] = item }
  async function removeAv(id)         { await avCatalogApi.remove(id); avList.value = avList.value.filter(o => o.id !== id) }

  return { osList, avList, loading, fetchOs, fetchAv, createOs, updateOs, removeOs, createAv, updateAv, removeAv }
})
