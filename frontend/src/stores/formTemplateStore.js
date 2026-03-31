import { defineStore } from 'pinia'
import { ref } from 'vue'
import formTemplatesApi from '@/api/formTemplatesApi'

export const useFormTemplateStore = defineStore('formTemplate', () => {
  const folders = ref([])
  const templates = ref([])
  const currentTemplate = ref(null)
  const mappings = ref([])
  const fieldCatalog = ref([])
  const loading = ref(false)
  const previewHtml = ref('')
  const workbookPreview = ref(null)
  const previewWorkbookBinary = ref(null)
  const previewWorkbookName = ref('')
  const dataPreview = ref(null)

  function syncTemplateMappingCount(templateId, mappingCount) {
    templates.value = templates.value.map((template) =>
      template.id === templateId
        ? { ...template, mapping_count: mappingCount }
        : template,
    )

    if (currentTemplate.value?.id === templateId) {
      currentTemplate.value = {
        ...currentTemplate.value,
        mapping_count: mappingCount,
      }
    }
  }

  async function fetchList(params = {}) {
    loading.value = true
    try {
      const { data } = await formTemplatesApi.list(params)
      templates.value = data
    } finally {
      loading.value = false
    }
  }

  async function fetchFolders() {
    const { data } = await formTemplatesApi.listFolders()
    folders.value = data
    return data
  }

  async function fetchOne(id) {
    const { data } = await formTemplatesApi.get(id)
    currentTemplate.value = data
    return data
  }

  async function create(formData) {
    const { data } = await formTemplatesApi.create(formData)
    await Promise.all([fetchList(), fetchFolders()])
    return data
  }

  async function update(id, body) {
    const { data } = await formTemplatesApi.update(id, body)
    await Promise.all([fetchList(), fetchFolders()])
    return data
  }

  async function remove(id) {
    await formTemplatesApi.remove(id)
    await Promise.all([fetchList(), fetchFolders()])
  }

  async function createFolder(body) {
    const { data } = await formTemplatesApi.createFolder(body)
    await fetchFolders()
    return data
  }

  async function updateFolder(id, body) {
    const { data } = await formTemplatesApi.updateFolder(id, body)
    await Promise.all([fetchFolders(), fetchList()])
    return data
  }

  async function removeFolder(id) {
    await formTemplatesApi.removeFolder(id)
    await Promise.all([fetchFolders(), fetchList()])
  }

  async function fetchMappings(templateId) {
    const { data } = await formTemplatesApi.listMappings(templateId)
    mappings.value = data
    return data
  }

  async function bulkSaveMappings(templateId, items) {
    const { data } = await formTemplatesApi.bulkSaveMappings(templateId, items)
    mappings.value = data
    syncTemplateMappingCount(templateId, data.length)
    return data
  }

  async function fetchFieldCatalog() {
    if (fieldCatalog.value.length > 0) return fieldCatalog.value
    const { data } = await formTemplatesApi.fieldCatalog()
    fieldCatalog.value = data
    return data
  }

  function extractFilename(headers = {}, fallback = 'form_report.xlsx') {
    const disposition = headers['content-disposition'] || ''
    const match = disposition.match(/filename\*?=(?:UTF-8'')?(.+)/i)
    return match ? decodeURIComponent(match[1]).replace(/^["']|["']$/g, '') : fallback
  }

  async function fetchPreview(templateId, assetId) {
    loading.value = true
    try {
      const response = await formTemplatesApi.generate(templateId, assetId)
      previewWorkbookBinary.value = await response.data.arrayBuffer()
      previewWorkbookName.value = extractFilename(response.headers)
      previewHtml.value = ''
      return previewWorkbookBinary.value
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

  function clearRenderedPreview() {
    previewWorkbookBinary.value = null
    previewWorkbookName.value = ''
    previewHtml.value = ''
  }

  async function fetchDataPreview(assetId, dataSource, maxRows = 5) {
    const { data } = await formTemplatesApi.dataPreview(assetId, dataSource, maxRows)
    dataPreview.value = data
    return data
  }

  function clearDataPreview() {
    dataPreview.value = null
  }

  async function downloadReport(templateId, assetId) {
    const response = await formTemplatesApi.generate(templateId, assetId)
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const filename = extractFilename(response.headers)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    window.URL.revokeObjectURL(url)
  }

  return {
    folders, templates, currentTemplate, mappings, fieldCatalog, loading, previewHtml, workbookPreview, previewWorkbookBinary, previewWorkbookName, dataPreview,
    fetchFolders, fetchList, fetchOne, create, update, remove,
    createFolder, updateFolder, removeFolder,
    fetchMappings, bulkSaveMappings,
    fetchFieldCatalog, fetchPreview, fetchWorkbookPreview, clearWorkbookPreview,
    clearRenderedPreview, fetchDataPreview, clearDataPreview, downloadReport,
  }
})
