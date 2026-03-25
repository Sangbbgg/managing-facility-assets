import client from './client'

export const adminApi = {
  listTables: ()                     => client.get('/api/admin/tables').then(r => r.data),
  getTableData: (name, page, size)   => client.get(`/api/admin/tables/${name}`, { params: { page, size } }).then(r => r.data),
}
