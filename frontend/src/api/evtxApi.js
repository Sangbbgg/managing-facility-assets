import client from './client'

export const evtxApi = {
  upload: (formData) =>
    client.post('/api/evtx/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 120000,
    }).then((r) => r.data),
}
