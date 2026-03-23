import client from './client'

export const osCatalogApi = {
  list:   ()           => client.get('/api/catalogs/os').then(r => r.data),
  create: (body)       => client.post('/api/catalogs/os', body).then(r => r.data),
  update: (id, body)   => client.patch(`/api/catalogs/os/${id}`, body).then(r => r.data),
  remove: (id)         => client.delete(`/api/catalogs/os/${id}`),
}

export const avCatalogApi = {
  list:   ()           => client.get('/api/catalogs/av').then(r => r.data),
  create: (body)       => client.post('/api/catalogs/av', body).then(r => r.data),
  update: (id, body)   => client.patch(`/api/catalogs/av/${id}`, body).then(r => r.data),
  remove: (id)         => client.delete(`/api/catalogs/av/${id}`),
}

export const equipmentTypeApi = {
  list:   ()           => client.get('/api/catalogs/equipment-types').then(r => r.data),
  create: (body)       => client.post('/api/catalogs/equipment-types', body).then(r => r.data),
  update: (id, body)   => client.patch(`/api/catalogs/equipment-types/${id}`, body).then(r => r.data),
  remove: (id)         => client.delete(`/api/catalogs/equipment-types/${id}`),
}
