import client from './client'

export default {
  list(params = {}) {
    return client.get('/api/form-templates', { params })
  },
  listFolders() {
    return client.get('/api/form-templates/folders')
  },
  createFolder(body) {
    return client.post('/api/form-templates/folders', body)
  },
  updateFolder(id, body) {
    return client.patch(`/api/form-templates/folders/${id}`, body)
  },
  removeFolder(id) {
    return client.delete(`/api/form-templates/folders/${id}`)
  },
  get(id) {
    return client.get(`/api/form-templates/${id}`)
  },
  file(id) {
    return client.get(`/api/form-templates/${id}/file`, {
      responseType: 'arraybuffer',
    })
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
  workbookPreview(templateId) {
    return client.get(`/api/form-templates/${templateId}/workbook-preview`)
  },
  fieldCatalog() {
    return client.get('/api/form-templates/field-catalog')
  },
  dataPreview(assetId, dataSource, maxRows = 5) {
    return client.get('/api/form-templates/data-preview', {
      params: { asset_id: assetId, data_source: dataSource, max_rows: maxRows },
    })
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
