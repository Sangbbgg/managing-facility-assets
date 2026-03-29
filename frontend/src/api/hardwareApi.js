import client from './client'

export const hardwareApi = {
  getAll: (assetId) => client.get(`/api/assets/${assetId}/hardware`).then((r) => r.data),
  remove: (assetId, type, hwId) => client.delete(`/api/assets/${assetId}/hardware/${type}/${hwId}`),
  updateUnusedNics: (assetId, nicIds) =>
    client.patch(`/api/assets/${assetId}/hardware/nics/unused`, { nic_ids: nicIds }).then((r) => r.data),
}
