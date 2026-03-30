import { defineStore } from 'pinia'
import { ref } from 'vue'
import formTemplatesApi from '@/api/formTemplatesApi'

export const useFormTemplateStore = defineStore('formTemplate', () => {
  const templates = ref([])
  const currentTemplate = ref(null)
  const mappings = ref([])
  const fieldCatalog = ref([])
  const loading = ref(false)
  const previewHtml = ref('')
  const workbookPreview = ref(null)

  async function fetchList(params = {}) {
    loading.value = true
    try {
      const { data } = await formTemplatesApi.list(params)
      templates.value = data
    } finally {
      loading.value = false
    }
  }

  async function fetchOne(id) {
    const { data } = await formTemplatesApi.get(id)
    currentTemplate.value = data
    return data
  }

  async function create(formData) {
    const { data } = await formTemplatesApi.create(formData)
    await fetchList()
    return data
  }

  async function update(id, body) {
    const { data } = await formTemplatesApi.update(id, body)
    await fetchList()
    return data
  }

  async function remove(id) {
    await formTemplatesApi.remove(id)
    await fetchList()
  }

  async function fetchMappings(templateId) {
    const { data } = await formTemplatesApi.listMappings(templateId)
    mappings.value = data
    return data
  }

  async function bulkSaveMappings(templateId, items) {
    const { data } = await formTemplatesApi.bulkSaveMappings(templateId, items)
    mappings.value = data
    return data
  }

  async function fetchFieldCatalog() {
    if (fieldCatalog.value.length > 0) return fieldCatalog.value
    const { data } = await formTemplatesApi.fieldCatalog()
    fieldCatalog.value = data
    return data
  }

  async function fetchPreview(templateId, assetId) {
    loading.value = true
    try {
      const { data } = await formTemplatesApi.preview(templateId, assetId)
      previewHtml.value = data.html
      return data.html
    } finally {
      loading.value = false
    }
  }

  async function fetchWorkbookPreview(templateId) {
    loading.value = true
    try {
      const { data } = await formTemplatesApi.workbookPreview(templateId)
      workbookPreview.value = data
      return data
    } finally {
      loading.value = false
    }
  }

  function clearWorkbookPreview() {
    workbookPreview.value = null
  }

  async function downloadReport(templateId, assetId) {
    const response = await formTemplatesApi.generate(templateId, assetId)
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const disposition = response.headers['content-disposition'] || ''
    const match = disposition.match(/filename\*?=(?:UTF-8'')?(.+)/i)
    const filename = match ? decodeURIComponent(match[1]) : 'form_report.xlsx'
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    window.URL.revokeObjectURL(url)
  }

  return {
    templates, currentTemplate, mappings, fieldCatalog, loading, previewHtml, workbookPreview,
    fetchList, fetchOne, create, update, remove,
    fetchMappings, bulkSaveMappings,
    fetchFieldCatalog, fetchPreview, fetchWorkbookPreview, clearWorkbookPreview, downloadReport,
  }
})
