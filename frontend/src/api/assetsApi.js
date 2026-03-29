import client from './client'

export const assetsApi = {
  list:        (params)       => client.get('/api/assets', { params }).then(r => r.data),
  get:         (id)           => client.get(`/api/assets/${id}`).then(r => r.data),
  create:      (body)         => client.post('/api/assets', body).then(r => r.data),
  update:      (id, body)     => client.patch(`/api/assets/${id}`, body).then(r => r.data),
  remove:      (id)           => client.delete(`/api/assets/${id}`),
  // v2 확장
  detailList:  () =>
    client.get('/api/assets/detail-list').then(r => r.data),
  previewCode: (groupId, typeId) =>
    client.get('/api/assets/preview-code', { params: { group_id: groupId, type_id: typeId } }).then(r => r.data),
  bulkTemplate: () =>
    client.get('/api/assets/bulk-template', { responseType: 'blob' }).then(r => r),
  bulkRegister: (formData) =>
    client.post('/api/assets/bulk-register', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then(r => r.data),
  changeLog: (id) =>
    client.get(`/api/assets/${id}/change-log`).then(r => r.data).catch(() => []),
}
