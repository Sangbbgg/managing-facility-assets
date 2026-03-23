import client from './client'

export const customFieldsApi = {
  list:    (assetId)              => client.get(`/api/assets/${assetId}/custom-fields`).then(r => r.data),
  create:  (assetId, body)        => client.post(`/api/assets/${assetId}/custom-fields`, body).then(r => r.data),
  update:  (assetId, fid, body)   => client.patch(`/api/assets/${assetId}/custom-fields/${fid}`, body).then(r => r.data),
  remove:  (assetId, fid)         => client.delete(`/api/assets/${assetId}/custom-fields/${fid}`),
  reorder: (assetId, order)       => client.patch(`/api/assets/${assetId}/custom-fields/reorder`, order).then(r => r.data),
}
