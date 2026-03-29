import client from './client'

export const reportsApi = {
  getDataSources: () => client.get('/api/reports/data-sources').then((r) => r.data),
  getFields: (dataSource) =>
    client.get(`/api/reports/fields/${encodeURIComponent(dataSource)}`).then((r) => r.data),
  listTemplates: () => client.get('/api/reports/templates').then((r) => r.data),
  createTemplate: (body) => client.post('/api/reports/templates', body).then((r) => r.data),
  updateTemplate: (id, body) => client.patch(`/api/reports/templates/${id}`, body).then((r) => r.data),
  deleteTemplate: (id) => client.delete(`/api/reports/templates/${id}`),
  generate: (templateId, year, month) => {
    const params = new URLSearchParams({ template_id: templateId, year })
    if (month) params.append('month', month)
    return client.post(`/api/reports/generate?${params}`, null, {
      responseType: 'blob',
      timeout: 60000,
    })
  },
}
