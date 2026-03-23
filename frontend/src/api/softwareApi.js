import client from './client'

export const softwareApi = {
  getAll:    (assetId)              => client.get(`/api/assets/${assetId}/software`).then(r => r.data),
  getByType: (assetId, type)        => client.get(`/api/assets/${assetId}/software/${type}`).then(r => r.data),
  remove:    (assetId, type, swId)  => client.delete(`/api/assets/${assetId}/software/${type}/${swId}`),
}
