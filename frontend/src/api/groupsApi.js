import client from './client'

export const groupsApi = {
  list:      ()           => client.get('/api/groups').then(r => r.data),
  codeable:  ()           => client.get('/api/groups/codeable').then(r => r.data),
  create:    (body)       => client.post('/api/groups', body).then(r => r.data),
  update:    (id, body)   => client.patch(`/api/groups/${id}`, body).then(r => r.data),
  remove:    (id)         => client.delete(`/api/groups/${id}`),
}
