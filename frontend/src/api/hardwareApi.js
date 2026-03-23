import client from './client'

export const hardwareApi = {
  getAll:     (assetId)              => client.get(`/api/assets/${assetId}/hardware`).then(r => r.data),
  getByType:  (assetId, type)        => client.get(`/api/assets/${assetId}/hardware/${type}`).then(r => r.data),
  remove:     (assetId, type, hwId)  => client.delete(`/api/assets/${assetId}/hardware/${type}/${hwId}`),
}
