import client from './client'

export const locationsApi = {
  list:   ()           => client.get('/api/locations').then(r => r.data),
  create: (body)       => client.post('/api/locations', body).then(r => r.data),
  update: (id, body)   => client.patch(`/api/locations/${id}`, body).then(r => r.data),
  remove: (id)         => client.delete(`/api/locations/${id}`),
}
