import client from './client'

export const customFieldsApi = {
  listKeys: () => client.get('/api/assets/custom-fields/keys').then((r) => r.data),
  createKey: (fieldKey) => client.post('/api/assets/custom-fields/keys', { field_key: fieldKey }).then((r) => r.data),
  removeKey: (fieldKey) => client.delete(`/api/assets/custom-fields/keys/${encodeURIComponent(fieldKey)}`),
  list: (assetId) => client.get(`/api/assets/${assetId}/custom-fields`).then((r) => r.data),
  create: (assetId, body) => client.post(`/api/assets/${assetId}/custom-fields`, body).then((r) => r.data),
  upsertByKey: (assetId, fieldKey, fieldValue) =>
    client.put(`/api/assets/${assetId}/custom-fields/by-key/${encodeURIComponent(fieldKey)}`, { field_value: fieldValue }).then((r) => r.data),
  update: (assetId, fieldId, body) =>
    client.patch(`/api/assets/${assetId}/custom-fields/${fieldId}`, body).then((r) => r.data),
  remove: (assetId, fieldId) => client.delete(`/api/assets/${assetId}/custom-fields/${fieldId}`),
}
