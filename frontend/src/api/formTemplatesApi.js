import client from './client'

export default {
  list(params = {}) {
    return client.get('/api/form-templates', { params })
  },
  get(id) {
    return client.get(`/api/form-templates/${id}`)
  },
  create(formData) {
    return client.post('/api/form-templates', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  update(id, body) {
    return client.patch(`/api/form-templates/${id}`, body)
  },
  remove(id) {
    return client.delete(`/api/form-templates/${id}`)
  },
  listMappings(templateId) {
    return client.get(`/api/form-templates/${templateId}/mappings`)
  },
  bulkSaveMappings(templateId, mappings) {
    return client.put(`/api/form-templates/${templateId}/mappings/bulk`, { mappings })
  },
  analyze(templateId) {
    return client.get(`/api/form-templates/${templateId}/analyze`)
  },
  fieldCatalog() {
    return client.get('/api/form-templates/field-catalog')
  },
  generate(templateId, assetId) {
    return client.post('/api/form-templates/generate', null, {
      params: { template_id: templateId, asset_id: assetId },
      responseType: 'blob',
    })
  },
  preview(templateId, assetId) {
    return client.post('/api/form-templates/preview', null, {
      params: { template_id: templateId, asset_id: assetId },
    })
  },
}
