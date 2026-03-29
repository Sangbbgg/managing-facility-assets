import client from './client'

export const collectApi = {
  scripts: () => client.get('/api/collect/scripts').then((r) => r.data),
  downloadScript: (key) =>
    client.get(`/api/collect/scripts/${key}/download`, { responseType: 'blob' }).then((r) => r),
  downloadBundle: () =>
    client.get('/api/collect/script-bundle', { responseType: 'blob' }).then((r) => r),
  parsePreview: (assetId, formData) =>
    client.post('/api/collect/parse-preview', formData, {
      params: { asset_id: assetId },
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then((r) => r.data),
  confirm: (assetId, formData) =>
    client.post('/api/collect/confirm', formData, {
      params: { asset_id: assetId },
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then((r) => r.data),
}
