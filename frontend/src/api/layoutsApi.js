import client from './client'

export const layoutsApi = {
  list:       (pageKey = 'asset_list') => client.get('/api/layouts', { params: { page_key: pageKey } }).then(r => r.data),
  create:     (body)  => client.post('/api/layouts', body).then(r => r.data),
  update:     (id, body) => client.patch(`/api/layouts/${id}`, body).then(r => r.data),
  remove:     (id)    => client.delete(`/api/layouts/${id}`),
  setDefault: (id)    => client.patch(`/api/layouts/${id}/default`).then(r => r.data),
}
