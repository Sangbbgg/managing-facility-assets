import client from './client'

export const assetsApi = {
  list:   (params) => client.get('/api/assets', { params }).then(r => r.data),
  get:    (id)     => client.get(`/api/assets/${id}`).then(r => r.data),
  create: (body)   => client.post('/api/assets', body).then(r => r.data),
  update: (id, body) => client.patch(`/api/assets/${id}`, body).then(r => r.data),
  remove: (id)     => client.delete(`/api/assets/${id}`),
}
