import client from './client'

export const personsApi = {
  list:   (params) => client.get('/api/persons', { params }).then(r => r.data),
  create: (body)   => client.post('/api/persons', body).then(r => r.data),
  update: (id, body) => client.patch(`/api/persons/${id}`, body).then(r => r.data),
  remove: (id)     => client.delete(`/api/persons/${id}`),
}

export const departmentsApi = {
  list:   ()       => client.get('/api/departments').then(r => r.data),
  create: (body)   => client.post('/api/departments', body).then(r => r.data),
  update: (id, body) => client.patch(`/api/departments/${id}`, body).then(r => r.data),
  remove: (id)     => client.delete(`/api/departments/${id}`),
}
