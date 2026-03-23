import { defineStore } from 'pinia'
import { ref } from 'vue'
import { softwareApi } from '@/api/softwareApi'

export const useAssetSwStore = defineStore('assetSw', () => {
  const all     = ref({})  // { products:[], hotfixes:[], processes:[] }
  const loading = ref(false)

  async function fetchAll(assetId) {
    loading.value = true
    try { all.value = await softwareApi.getAll(assetId) }
    catch { all.value = {} }
    finally { loading.value = false }
  }

  async function removeItem(assetId, type, swId) {
    await softwareApi.remove(assetId, type, swId)
    if (all.value[type]) {
      all.value[type] = all.value[type].filter(i => i.id !== swId)
    }
  }

  function reset() { all.value = {} }

  return { all, loading, fetchAll, removeItem, reset }
})
