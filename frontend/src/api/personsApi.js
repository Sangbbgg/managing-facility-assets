import client from './client'

export const personsApi = {
  list:   (params) => client.get('/api/persons', { params }).then(r => r.data),
  create: (body)   => client.post('/api/persons', body).then(r => r.data),
  update: (id, body) => client.patch(`/api/persons/${id}`, body).then(r => r.data),
  remove: (id)     => client.delete(`/api/persons/${id}`),
}

export const departmentsApi = {
  list:   ()         => client.get('/api/persons/departments').then(r => r.data),
  create: (body)     => client.post('/api/persons/departments', body).then(r => r.data),
  update: (id, body) => client.patch(`/api/persons/departments/${id}`, body).then(r => r.data),
  remove: (id)       => client.delete(`/api/persons/departments/${id}`),
}
