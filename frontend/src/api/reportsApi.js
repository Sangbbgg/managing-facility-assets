import client from './client'

export const reportsApi = {
  // 데이터소스 목록
  getDataSources: () => client.get('/api/reports/data-sources').then(r => r.data),

  // 필드 카탈로그
  getFields: (dataSource) =>
    client.get(`/api/reports/fields/${encodeURIComponent(dataSource)}`).then(r => r.data),

  // 서식 CRUD
  listTemplates:  ()           => client.get('/api/reports/templates').then(r => r.data),
  getTemplate:    (id)         => client.get(`/api/reports/templates/${id}`).then(r => r.data),
  createTemplate: (body)       => client.post('/api/reports/templates', body).then(r => r.data),
  updateTemplate: (id, body)   => client.patch(`/api/reports/templates/${id}`, body).then(r => r.data),
  deleteTemplate: (id)         => client.delete(`/api/reports/templates/${id}`),

  // 보고서 생성 (blob)
  generate: (templateId, year, month) => {
    const params = new URLSearchParams({ template_id: templateId, year })
    if (month) params.append('month', month)
    return client.post(`/api/reports/generate?${params}`, null, {
      responseType: 'blob',
      timeout: 60000,
    })
  },
}
