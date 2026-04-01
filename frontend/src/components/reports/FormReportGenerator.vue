<template>
  <div class="generator-layout">
    <div class="control-panel">
      <div class="field-block">
        <div class="field-label">그룹 선택</div>
        <div class="group-select-row">
          <n-select
            v-model:value="selectedRootGroupId"
            :options="rootGroupOptions"
            placeholder="계열 선택"
            clearable
          />
          <n-select
            v-model:value="selectedBranchGroupId"
            :options="branchGroupOptions"
            :disabled="!selectedRootGroupId"
            placeholder="세부 그룹 선택"
            clearable
          />
        </div>
      </div>

      <div class="field-block">
        <div class="field-label">양식 선택</div>
        <n-select
          v-model:value="selectedTemplate"
          :options="templateOptions"
          :disabled="!selectedReportGroupId"
          placeholder="그룹을 먼저 선택하세요"
        />
      </div>

      <div class="selection-summary">
        <div class="summary-label">선택 그룹</div>
        <div class="summary-empty">
          {{ selectedReportGroupLabel }}
        </div>
      </div>

      <div class="selection-summary">
        <div class="summary-label">일괄 처리</div>
        <div class="summary-empty">
          선택 {{ selectedAssetIds.length }}건
        </div>
      </div>

      <div class="action-row">
        <n-button
          :disabled="!canDownload"
          :loading="downloading"
          @click="handleBulkDownload"
        >
          선택 {{ selectedAssetIds.length }}건 다운로드
        </n-button>
      </div>
    </div>

    <div class="asset-panel">
      <div class="asset-toolbar">
        <n-input
          v-model:value="assetSearch"
          clearable
          placeholder="자산번호 / 자산명 / 장비종류 / 상태 검색"
        />
      </div>

      <ListHeader title="자산 목록" :count="filteredAssetList.length" />

      <n-data-table
        class="asset-table"
        :columns="tableColumns"
        :data="filteredAssetList"
        :pagination="false"
        :row-key="(row) => row.id"
        :row-props="rowProps"
        :row-class-name="rowClassName"
        :checked-row-keys="selectedAssetIds"
        :single-line="false"
        size="small"
        @update:checked-row-keys="handleCheckedRowKeys"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, h, onMounted, ref, watch } from 'vue'
import { NButton, NTag, useMessage } from 'naive-ui'
import ListHeader from '@/components/common/ListHeader.vue'
import { useFormTemplateStore } from '@/stores/formTemplateStore'
import { useAssetStore } from '@/stores/assetStore'
import { useCatalogStore } from '@/stores/catalogStore'
import { useGroupStore } from '@/stores/groupStore'

const emit = defineEmits(['preview-open'])

const store = useFormTemplateStore()
const assetStore = useAssetStore()
const catalogStore = useCatalogStore()
const groupStore = useGroupStore()
const message = useMessage()

const selectedTemplate = ref(null)
const selectedAssetIds = ref([])
const assetSearch = ref('')
const downloading = ref(false)
const previewLoadingAssetId = ref(null)
const selectedRootGroupId = ref(null)
const selectedBranchGroupId = ref(null)

const equipmentTypeMap = computed(() => {
  const entries = (catalogStore.equipmentTypes || []).map((type) => [type.id, type])
  return new Map(entries)
})

function equipmentTypeLabel(asset) {
  const type = equipmentTypeMap.value.get(asset?.equipment_type_id)
  if (!type) {
    return '미지정'
  }
  return type.code ? `${type.code} · ${type.name}` : type.name
}

function groupLabel(asset) {
  return asset?.group_full_path || asset?.group_name || '-'
}

function isGroupCompatible(template, asset) {
  const assignedGroups = template.groups || []
  if (!assignedGroups.length) {
    return true
  }
  const assetGroupPath = asset?.group_full_path || ''
  if (!assetGroupPath) {
    return false
  }
  return assignedGroups.some((group) =>
    assetGroupPath === group.full_path || assetGroupPath.startsWith(`${group.full_path} >`),
  )
}

function isTemplateCompatible(template, asset) {
  return isGroupCompatible(template, asset)
}

const rootGroupOptions = computed(() =>
  groupStore.list
    .filter((group) => group.depth === 1)
    .map((group) => ({
      label: group.name,
      value: group.id,
    })),
)

const branchGroupOptions = computed(() =>
  groupStore.list
    .filter((group) => group.parent_id === selectedRootGroupId.value)
    .map((group) => ({
      label: group.name,
      value: group.id,
    })),
)

const selectedReportGroupId = computed(() => {
  if (branchGroupOptions.value.length > 0) {
    return selectedBranchGroupId.value || null
  }
  return selectedRootGroupId.value || null
})

const selectedReportGroup = computed(() =>
  groupStore.list.find((group) => group.id === selectedReportGroupId.value) || null,
)

const selectedReportGroupLabel = computed(() =>
  selectedReportGroup.value?.full_path || '그룹을 먼저 선택하세요'
)

function isAssetInSelectedGroup(asset) {
  const group = selectedReportGroup.value
  if (!group) {
    return false
  }
  const assetGroupPath = asset?.group_full_path || ''
  if (!assetGroupPath) {
    return false
  }
  return assetGroupPath === group.full_path || assetGroupPath.startsWith(`${group.full_path} >`)
}

const filteredAssetList = computed(() => {
  const scopedAssets = selectedReportGroup.value
    ? assetStore.list.filter((asset) => isAssetInSelectedGroup(asset))
    : []

  const query = assetSearch.value.trim().toLowerCase()
  if (!query) {
    return scopedAssets
  }

  return scopedAssets.filter((asset) => {
    const haystack = [
      asset.asset_code,
      asset.asset_name,
      asset.status,
      groupLabel(asset),
      equipmentTypeLabel(asset),
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
    return haystack.includes(query)
  })
})

const templateOptions = computed(() => {
  return store.templates
    .filter((template) => template.is_active)
    .filter((template) => {
      if (!selectedReportGroup.value) {
        return false
      }
      const assignedGroups = template.groups || []
      if (!assignedGroups.length) {
        return true
      }
      return assignedGroups.some((group) =>
        group.full_path === selectedReportGroup.value.full_path
        || group.full_path.startsWith(`${selectedReportGroup.value.full_path} >`)
        || selectedReportGroup.value.full_path.startsWith(`${group.full_path} >`),
      )
    })
    .map((template) => {
      return {
        label: template.name,
        value: template.id,
      }
    })
})

const canDownload = computed(() => !!selectedReportGroupId.value && !!selectedTemplate.value && selectedAssetIds.value.length > 0)
const isPreviewLoading = computed(() => previewLoadingAssetId.value !== null)

function rowClassName(row) {
  return selectedAssetIds.value.includes(row.id) ? 'asset-row-selected' : ''
}

function shouldIgnoreRowToggle(event) {
  const target = event?.target
  if (!(target instanceof Element)) {
    return false
  }
  return Boolean(
    target.closest('.n-checkbox')
    || target.closest('.n-button')
    || target.closest('.n-data-table-th--selection')
    || target.closest('.n-data-table-td--selection'),
  )
}

function rowProps(row) {
  return {
    style: 'cursor:pointer',
    onClick: (event) => {
      if (shouldIgnoreRowToggle(event)) {
        return
      }
      const nextKeys = selectedAssetIds.value.includes(row.id)
        ? selectedAssetIds.value.filter((id) => id !== row.id)
        : [...selectedAssetIds.value, row.id]
      selectedAssetIds.value = nextKeys
    },
  }
}

function getCurrentTemplate() {
  return store.templates.find((template) => template.id === selectedTemplate.value) || null
}

function isAssetCompatibleWithSelectedTemplate(assetId) {
  const template = getCurrentTemplate()
  const asset = assetStore.list.find((item) => item.id === assetId)
  if (!template || !asset) {
    return false
  }
  return isTemplateCompatible(template, asset)
}

function handleCheckedRowKeys(keys) {
  selectedAssetIds.value = keys
}

watch(selectedRootGroupId, (value) => {
  const isBranchValid = groupStore.list.some(
    (group) => group.id === selectedBranchGroupId.value && group.parent_id === value,
  )
  if (!isBranchValid) {
    selectedBranchGroupId.value = null
  }
})

watch([selectedReportGroupId, templateOptions], ([groupId, options]) => {
  if (!groupId) {
    selectedTemplate.value = null
    selectedAssetIds.value = []
    return
  }
  if (!options.some((option) => option.value === selectedTemplate.value)) {
    selectedTemplate.value = null
  }
  selectedAssetIds.value = selectedAssetIds.value.filter((assetId) => {
    const asset = assetStore.list.find((item) => item.id === assetId)
    return asset ? isAssetInSelectedGroup(asset) : false
  })
})

const tableColumns = computed(() => [
  {
    type: 'selection',
    width: 48,
  },
  {
    key: 'asset_code',
    title: '자산번호',
    width: 150,
    sorter: (a, b) => String(a.asset_code || '').localeCompare(String(b.asset_code || '')),
  },
  {
    key: 'asset_name',
    title: '자산명',
    minWidth: 220,
    ellipsis: false,
  },
  {
    key: 'group',
    title: '그룹',
    minWidth: 220,
    ellipsis: false,
    render: (row) => groupLabel(row),
  },
  {
    key: 'equipment_type',
    title: '장비종류',
    width: 150,
    render: (row) => equipmentTypeLabel(row),
  },
  {
    key: 'status',
    title: '상태',
    width: 110,
    render: (row) => h(
      NTag,
      { size: 'small', bordered: false, type: selectedAssetIds.value.includes(row.id) ? 'info' : 'default' },
      { default: () => row.status || '-' },
    ),
  },
  {
    key: 'preview_action',
    title: '미리보기',
    width: 110,
    render: (row) => h(
      NButton,
      {
        size: 'small',
        type: 'primary',
        ghost: true,
        loading: previewLoadingAssetId.value === row.id,
        disabled: !selectedTemplate.value || isPreviewLoading.value,
        onClick: (event) => {
          event.stopPropagation()
          handlePreview(row.id)
        },
      },
      { default: () => '보기' },
    ),
  },
])

async function handlePreview(assetId) {
  const asset = assetStore.list.find((item) => item.id === assetId)
  const template = getCurrentTemplate()
  if (!template) {
    message.warning('먼저 그룹과 양식을 선택하세요.')
    return
  }
  if (!asset) {
    message.warning('미리보기 자산을 찾지 못했습니다.')
    return
  }
  if (!isTemplateCompatible(template, asset)) {
    message.warning('선택한 자산과 현재 양식이 호환되지 않습니다.')
    return
  }

  if (isPreviewLoading.value) {
    return
  }

  previewLoadingAssetId.value = assetId
  try {
    store.clearRenderedPreview()
    emit('preview-open')
    await store.fetchPreview(selectedTemplate.value, assetId)
  } catch (e) {
    message.error('미리보기 실패: ' + (e.message || ''))
  } finally {
    previewLoadingAssetId.value = null
  }
}

async function handleBulkDownload() {
  if (!canDownload.value) {
    return
  }

  downloading.value = true
  try {
    const compatibleAssetIds = selectedAssetIds.value.filter((assetId) =>
      isAssetCompatibleWithSelectedTemplate(assetId),
    )
    const skippedCount = selectedAssetIds.value.length - compatibleAssetIds.length

    if (!compatibleAssetIds.length) {
      message.warning('선택한 자산 중 현재 양식과 호환되는 항목이 없습니다.')
      return
    }

    for (const assetId of compatibleAssetIds) {
      await store.downloadReport(selectedTemplate.value, assetId)
    }
    if (skippedCount > 0) {
      message.warning(`호환되지 않는 ${skippedCount}건을 제외하고 ${compatibleAssetIds.length}건 다운로드를 요청했습니다.`)
    } else {
      message.success(`선택한 ${compatibleAssetIds.length}건 다운로드를 요청했습니다.`)
    }
  } catch (e) {
    message.error('다운로드 실패: ' + (e.message || ''))
  } finally {
    downloading.value = false
  }
}

onMounted(async () => {
  await Promise.all([
    store.fetchList({ is_active: true }),
    assetStore.fetchDetailList(),
    catalogStore.fetchEquipmentTypes(),
    groupStore.fetchList(),
  ])
})
</script>

<style scoped>
.generator-layout {
  display: grid;
  grid-template-columns: minmax(248px, 300px) minmax(0, 1fr);
  gap: 18px;
  align-items: start;
}

.control-panel {
  display: grid;
  gap: 16px;
  padding: 18px;
  border: 1px solid #dbe3f0;
  border-radius: 16px;
  background: linear-gradient(180deg, #f8fbff 0%, #ffffff 100%);
  position: sticky;
  top: 20px;
  align-self: start;
  width: 100%;
  min-width: 0;
  max-width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

.field-block {
  display: grid;
  gap: 8px;
  min-width: 0;
}

.group-select-row {
  display: grid;
  gap: 8px;
  min-width: 0;
}

.field-label,
.summary-label {
  font-size: 13px;
  font-weight: 600;
  color: #334155;
}

.selection-summary {
  display: grid;
  gap: 8px;
  min-width: 0;
}

.summary-card,
.summary-empty {
  padding: 14px;
  border-radius: 12px;
  background: #fff;
}

.summary-card {
  display: grid;
  gap: 6px;
  border: 1px solid #dbe3f0;
}

.summary-empty {
  border: 1px dashed #cbd5e1;
  color: #64748b;
  font-size: 13px;
  min-width: 0;
  white-space: normal;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.summary-title {
  font-size: 15px;
  font-weight: 700;
  color: #0f172a;
}

.summary-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  font-size: 12px;
  color: #64748b;
}

.action-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  min-width: 0;
}

.asset-panel {
  display: grid;
  gap: 12px;
  min-width: 0;
  overflow: hidden;
}

.asset-toolbar {
  max-width: 420px;
  min-width: 0;
}

.control-panel :deep(.n-base-selection),
.control-panel :deep(.n-input) {
  width: 100%;
  min-width: 0;
}

.control-panel :deep(.n-base-selection-label),
.control-panel :deep(.n-base-selection-input) {
  min-width: 0;
}

.asset-table {
  min-width: 0;
}

.asset-table :deep(.n-data-table-wrapper) {
  overflow-x: auto;
}

.asset-table :deep(.n-data-table-th) {
  white-space: nowrap;
}

.asset-table :deep(.n-data-table-td) {
  white-space: normal;
  word-break: break-word;
}

.asset-table :deep(.asset-row-selected td) {
  background: #eff6ff;
}

@media (max-width: 900px) {
  .generator-layout {
    grid-template-columns: 1fr;
  }

  .control-panel {
    position: static;
    top: auto;
  }
}
</style>
