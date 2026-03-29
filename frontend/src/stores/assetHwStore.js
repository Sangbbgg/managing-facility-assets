import { defineStore } from 'pinia'
import { ref } from 'vue'
import { hardwareApi } from '@/api/hardwareApi'

export const useAssetHwStore = defineStore('assetHw', () => {
  const all     = ref({})  // { systems:[], cpus:[], memories:[], disks:[], gpus:[], nics:[] }
  const loading = ref(false)

  async function fetchAll(assetId) {
    loading.value = true
    try { all.value = await hardwareApi.getAll(assetId) }
    catch { all.value = {} }
    finally { loading.value = false }
  }

  async function removeItem(assetId, type, hwId) {
    await hardwareApi.remove(assetId, type, hwId)
    if (all.value[type]) {
      all.value[type] = all.value[type].filter(i => i.id !== hwId)
    }
  }

  async function updateUnusedNics(assetId, nicIds) {
    const result = await hardwareApi.updateUnusedNics(assetId, nicIds)
    if (all.value.nics) {
      const selected = new Set(result.unused_nic_ids || [])
      all.value.nics = all.value.nics.map((nic) => ({
        ...nic,
        is_unused: selected.has(nic.id),
      }))
    }
    return result
  }

  function reset() { all.value = {} }

  return { all, loading, fetchAll, removeItem, updateUnusedNics, reset }
})
