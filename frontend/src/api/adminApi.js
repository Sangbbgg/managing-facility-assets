import client from './client'

export const adminApi = {
  listTables: ()                     => client.get('/api/admin/tables').then(r => r.data),
  getTableData: (name, page, size)   => client.get(`/api/admin/tables/${name}`, { params: { page, size } }).then(r => r.data),
  listSnapshots: ()                  => client.get('/api/admin/snapshots').then(r => r.data),
  createSnapshot: (payload)          => client.post('/api/admin/snapshots', payload).then(r => r.data),
  restoreSnapshot: (snapshotId)      => client.post(`/api/admin/snapshots/${snapshotId}/restore`).then(r => r.data),
  rollbackSnapshot: ()               => client.post('/api/admin/snapshots/rollback').then(r => r.data),
}
