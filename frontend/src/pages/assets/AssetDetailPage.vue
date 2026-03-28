<template>
  <PageShell title="자산 상세 검토">
    <div style="height:calc(100vh - 140px);">
      <div style="display:flex; flex-direction:column; gap:8px;">
        <n-input
          v-model:value="search"
          placeholder="자산번호 / 자산명 검색"
          clearable
          size="small"
          style="max-width:360px;"
        />
        <ListHeader title="장비 종류별 자산 목록" :count="filteredList.length" />
        <n-alert type="info" :show-icon="false" style="font-size:12px;">
          장비 종류 탭을 선택한 뒤 자산 목록에서 공통 항목을 바로 수정하거나 상세 버튼으로 세부 화면을 엽니다.
        </n-alert>

        <n-tabs v-model:value="activeEquipmentTypeKey" type="line" animated size="small">
          <n-tab-pane
            v-for="group in equipmentTabs"
            :key="group.key"
            :name="group.key"
            :tab="`${group.title} (${group.items.length})`"
          >
            <n-data-table
              :columns="listColumns"
              :data="group.items"
              :pagination="false"
              :bordered="false"
              :single-line="false"
              :row-key="row => row.id"
              :scroll-x="1680"
              size="small"
            />
          </n-tab-pane>
        </n-tabs>

        <n-empty
          v-if="!equipmentTabs.length"
          description="표시할 자산이 없습니다."
          size="small"
          style="margin-top:16px;"
        />
      </div>
    </div>

    <n-modal
      v-model:show="detailModalVisible"
      preset="card"
      style="width:min(1280px, calc(100vw - 48px));"
      content-style="padding: 0;"
      :mask-closable="true"
      :bordered="false"
      size="huge"
    >
      <template #header>
        <n-text strong style="font-size:18px;">자산 상세 검토</n-text>
      </template>

      <div v-if="displayAsset" style="height:75vh; overflow-y:scroll; padding:16px;">
        <n-card size="small" style="margin-bottom:12px;">
          <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:16px; flex-wrap:wrap;">
            <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap;">
              <n-tag type="info" size="large">{{ displayAsset.asset_code }}</n-tag>
              <n-text style="font-size:18px; font-weight:600;">{{ displayAsset.asset_name }}</n-text>
              <n-tag size="small" :type="statusTagType(displayAsset.status)">
                {{ statusLabel(displayAsset.status) }}
              </n-tag>
            </div>
            <n-text depth="3" style="font-size:12px;">
              자동 수집 데이터를 확인한 뒤 필요한 항목만 보완합니다.
            </n-text>
          </div>

          <n-grid :cols="4" :x-gap="12" :y-gap="10" style="margin-top:14px;">
            <n-gi>
              <n-text depth="3" style="font-size:12px; display:block;">장비 유형</n-text>
              <n-text>{{ displayAsset.equipment_type_name || '-' }}</n-text>
            </n-gi>
            <n-gi>
              <n-text depth="3" style="font-size:12px; display:block;">위치</n-text>
              <div v-if="locationPath.hasValue">
                <n-text depth="3" style="font-size:12px; line-height:1.5;">
                  {{ locationPath.parentText }}
                </n-text>
                <n-text strong style="display:block; font-size:15px; line-height:1.5;">
                  {{ locationPath.leaf }}
                </n-text>
              </div>
              <n-text v-else>-</n-text>
            </n-gi>
            <n-gi>
              <n-text depth="3" style="font-size:12px; display:block;">그룹</n-text>
              <div v-if="groupPath.hasValue">
                <n-text depth="3" style="font-size:12px; line-height:1.5;">
                  {{ groupPath.parentText }}
                </n-text>
                <n-text strong style="display:block; font-size:15px; line-height:1.5;">
                  {{ groupPath.leaf }}
                </n-text>
              </div>
              <n-text v-else>-</n-text>
            </n-gi>
            <n-gi>
              <n-text depth="3" style="font-size:12px; display:block;">마지막 수집</n-text>
              <n-text>{{ formatDateTime(displayAsset.last_collected_at) }}</n-text>
            </n-gi>
          </n-grid>
        </n-card>

        <n-alert type="warning" :show-icon="false" style="margin-bottom:12px; font-size:12px;">
          이 팝업은 자산 1건의 운영 상태를 검토하고 예외 정보만 수정하는 작업 공간입니다.
        </n-alert>

        <n-tabs v-model:value="activeTab" type="line" animated>
          <n-tab-pane name="basic" tab="공통 정보">
            <AssetBasicInfoTab :asset="displayAsset" @updated="reloadAsset" />
          </n-tab-pane>

          <n-tab-pane name="hardware" tab="수집 하드웨어">
            <AssetHardwareTab :asset-id="selectedId" />
          </n-tab-pane>

          <n-tab-pane name="software" tab="수집 소프트웨어">
            <AssetSoftwareTab :asset-id="selectedId" />
          </n-tab-pane>

          <n-tab-pane name="custom" tab="보완 메모">
            <AssetCustomFieldsTab :asset-id="selectedId" />
          </n-tab-pane>

          <n-tab-pane name="collect" tab="수집 업로드">
            <AssetCollectUploadTab :asset-id="selectedId" @collected="onCollected" />
          </n-tab-pane>

          <n-tab-pane name="changelog" tab="변경 이력">
            <AssetChangeLogTab :asset-id="selectedId" />
          </n-tab-pane>
        </n-tabs>
      </div>

      <n-empty v-else description="자산을 불러오지 못했습니다." />
    </n-modal>
  </PageShell>
</template>

<script setup>
import { computed, h, onMounted, ref, watch } from 'vue'
import { NButton, NDatePicker, NInput, NSelect, useMessage } from 'naive-ui'
import { useRoute } from 'vue-router'
import PageShell from '@/components/common/PageShell.vue'
import ListHeader from '@/components/common/ListHeader.vue'
import AssetBasicInfoTab from './tabs/AssetBasicInfoTab.vue'
import AssetHardwareTab from './tabs/AssetHardwareTab.vue'
import AssetSoftwareTab from './tabs/AssetSoftwareTab.vue'
import AssetCustomFieldsTab from './tabs/AssetCustomFieldsTab.vue'
import AssetCollectUploadTab from './tabs/AssetCollectUploadTab.vue'
import AssetChangeLogTab from './tabs/AssetChangeLogTab.vue'
import { useAssetStore } from '@/stores/assetStore'
import { useAssetHwStore } from '@/stores/assetHwStore'
import { useAssetSwStore } from '@/stores/assetSwStore'
import { useCatalogStore } from '@/stores/catalogStore'
import { usePersonStore } from '@/stores/personStore'
import client from '@/api/client'

const route = useRoute()
const message = useMessage()
const assetStore = useAssetStore()
const hwStore = useAssetHwStore()
const swStore = useAssetSwStore()
const catalogStore = useCatalogStore()
const personStore = usePersonStore()

const search = ref('')
const assets = ref([])
const selectedId = ref(null)
const selectedAsset = ref(null)
const selectedAssetSummary = ref(null)
const activeTab = ref('basic')
const detailModalVisible = ref(false)
const activeEquipmentTypeKey = ref(null)
const rowDrafts = ref({})

const STATUS_LABELS = {
  OPERATING: '운영중',
  MAINTENANCE: '점검중',
  FAULTY: '고장',
  DISPOSED: '폐기',
}

const STATUS_TYPES = {
  OPERATING: 'success',
  MAINTENANCE: 'warning',
  FAULTY: 'error',
  DISPOSED: 'default',
}

const STATUS_OPTIONS = [
  { label: '운영중', value: 'OPERATING' },
  { label: '점검중', value: 'MAINTENANCE' },
  { label: '고장', value: 'FAULTY' },
  { label: '폐기', value: 'DISPOSED' },
]

const IMPORTANCE_OPTIONS = [
  { label: '상', value: '상' },
  { label: '중', value: '중' },
  { label: '하', value: '하' },
]

const personOptions = computed(() =>
  personStore.list.map((person) => ({ label: person.name, value: person.id }))
)

const mergedAssets = computed(() => {
  const baseById = new Map(assetStore.list.map((asset) => [asset.id, asset]))
  return assets.value.map((asset) => ({
    ...(baseById.get(asset.id) || {}),
    ...asset,
  }))
})

const filteredList = computed(() => {
  const q = search.value.trim().toLowerCase()
  return mergedAssets.value.filter((asset) => {
    if (!q) return true
    return (
      String(asset.asset_code || '').toLowerCase().includes(q) ||
      String(asset.asset_name || '').toLowerCase().includes(q)
    )
  })
})

const displayAsset = computed(() => ({
  ...(selectedAssetSummary.value || {}),
  ...(selectedAsset.value || {}),
}))

const locationPath = computed(() =>
  splitPath(displayAsset.value.location_full_path || displayAsset.value.location_name)
)

const groupPath = computed(() =>
  splitPath(displayAsset.value.group_full_path || displayAsset.value.group_name)
)

const equipmentTabs = computed(() => {
  const tabs = [
    {
      key: 'type-all',
      title: '전체',
      items: filteredList.value,
    },
    ...(catalogStore.equipmentTypes || []).map((type) => ({
    key: `type-${type.id}`,
    title: type.name || type.code || `장비 종류 ${type.id}`,
    items: filteredList.value.filter((asset) => {
      if (asset.equipment_type_code) {
        return asset.equipment_type_code === type.code
      }
      return asset.equipment_type_id === type.id
    }),
    })),
  ]

  const unassignedItems = filteredList.value.filter((asset) => {
    const hasTypeId = asset.equipment_type_id != null
    const hasTypeCode = Boolean(asset.equipment_type_code)
    return !hasTypeId && !hasTypeCode
  })

  if (unassignedItems.length) {
    tabs.push({
      key: 'type-unassigned',
      title: '미지정',
      items: unassignedItems,
    })
  }

  return tabs
})

const listColumns = computed(() => [
  {
    key: 'asset_code',
    title: '자산번호',
    width: 150,
    sorter: (a, b) => compareValues(a.asset_code, b.asset_code),
    render: (row) => row.asset_code || '-',
  },
  {
    key: 'asset_name',
    title: '자산명',
    width: 180,
    sorter: (a, b) => compareValues(getRowValue(a, 'asset_name'), getRowValue(b, 'asset_name')),
    render: (row) =>
      h(NInput, {
        value: getRowValue(row, 'asset_name') || '',
        size: 'small',
        'onUpdate:value': (value) => setRowDraft(row.id, 'asset_name', value),
        onBlur: () => saveRowField(row, 'asset_name'),
      }),
  },
  {
    key: 'purpose',
    title: '용도',
    width: 160,
    sorter: (a, b) => compareValues(getRowValue(a, 'purpose'), getRowValue(b, 'purpose')),
    render: (row) =>
      h(NInput, {
        value: getRowValue(row, 'purpose') || '',
        size: 'small',
        'onUpdate:value': (value) => setRowDraft(row.id, 'purpose', value),
        onBlur: () => saveRowField(row, 'purpose'),
      }),
  },
  {
    key: 'model_name',
    title: '모델명',
    width: 160,
    sorter: (a, b) => compareValues(getRowValue(a, 'model_name'), getRowValue(b, 'model_name')),
    render: (row) =>
      h(NInput, {
        value: getRowValue(row, 'model_name') || '',
        size: 'small',
        'onUpdate:value': (value) => setRowDraft(row.id, 'model_name', value),
        onBlur: () => saveRowField(row, 'model_name'),
      }),
  },
  {
    key: 'serial_number',
    title: '시리얼 번호',
    width: 160,
    sorter: (a, b) => compareValues(getRowValue(a, 'serial_number'), getRowValue(b, 'serial_number')),
    render: (row) =>
      h(NInput, {
        value: getRowValue(row, 'serial_number') || '',
        size: 'small',
        'onUpdate:value': (value) => setRowDraft(row.id, 'serial_number', value),
        onBlur: () => saveRowField(row, 'serial_number'),
      }),
  },
  {
    key: 'status',
    title: '상태',
    width: 130,
    sorter: (a, b) => compareValues(statusLabel(getRowValue(a, 'status')), statusLabel(getRowValue(b, 'status'))),
    render: (row) =>
      h(NSelect, {
        value: getRowValue(row, 'status'),
        options: STATUS_OPTIONS,
        size: 'small',
        consistentMenuWidth: false,
        'onUpdate:value': (value) => saveRowField(row, 'status', value),
      }),
  },
  {
    key: 'manager_id',
    title: '담당자(정)',
    width: 150,
    sorter: (a, b) => compareValues(findPersonName(getRowValue(a, 'manager_id')), findPersonName(getRowValue(b, 'manager_id'))),
    render: (row) =>
      h(NSelect, {
        value: getRowValue(row, 'manager_id'),
        options: personOptions.value,
        clearable: true,
        size: 'small',
        consistentMenuWidth: false,
        'onUpdate:value': (value) => saveRowField(row, 'manager_id', value ?? null),
      }),
  },
  {
    key: 'supervisor_id',
    title: '담당자(부)',
    width: 150,
    sorter: (a, b) => compareValues(findPersonName(getRowValue(a, 'supervisor_id')), findPersonName(getRowValue(b, 'supervisor_id'))),
    render: (row) =>
      h(NSelect, {
        value: getRowValue(row, 'supervisor_id'),
        options: personOptions.value,
        clearable: true,
        size: 'small',
        consistentMenuWidth: false,
        'onUpdate:value': (value) => saveRowField(row, 'supervisor_id', value ?? null),
      }),
  },
  {
    key: 'importance',
    title: '중요도',
    width: 110,
    sorter: (a, b) => compareValues(getRowValue(a, 'importance'), getRowValue(b, 'importance')),
    render: (row) =>
      h(NSelect, {
        value: getRowValue(row, 'importance'),
        options: IMPORTANCE_OPTIONS,
        size: 'small',
        'onUpdate:value': (value) => saveRowField(row, 'importance', value),
      }),
  },
  {
    key: 'install_date',
    title: '설치일',
    width: 160,
    sorter: (a, b) => compareValues(getRowValue(a, 'install_date'), getRowValue(b, 'install_date')),
    render: (row) =>
      h(NDatePicker, {
        value: toDatePickerValue(getRowValue(row, 'install_date')),
        type: 'date',
        clearable: true,
        size: 'small',
        style: 'width: 100%;',
        'onUpdate:value': (value) => saveRowField(row, 'install_date', formatDateValue(value)),
      }),
  },
  {
    key: 'actions',
    title: '상세',
    width: 80,
    render: (row) =>
      h(
        NButton,
        {
          size: 'tiny',
          type: 'primary',
          secondary: true,
          onClick: () => openDetail(row.id),
        },
        { default: () => '상세' }
      ),
  },
])

async function openDetail(id) {
  selectedId.value = id
  activeTab.value = 'basic'
  detailModalVisible.value = true
  selectedAssetSummary.value = mergedAssets.value.find((asset) => asset.id === id) || null
  await reloadAsset()
  hwStore.reset()
  swStore.reset()
}

async function reloadAsset() {
  if (!selectedId.value) return
  await assetStore.fetchOne(selectedId.value)
  selectedAsset.value = assetStore.current
}

async function onCollected() {
  if (!selectedId.value) return
  await hwStore.fetchAll(selectedId.value)
  await swStore.fetchAll(selectedId.value)
}

function statusLabel(status) {
  return STATUS_LABELS[status] || status || '-'
}

function statusTagType(status) {
  return STATUS_TYPES[status] || 'default'
}

function formatDateTime(value) {
  if (!value) return '-'
  return String(value).replace('T', ' ').slice(0, 16)
}

function toDatePickerValue(value) {
  if (!value) return null
  return new Date(value).getTime()
}

function formatDateValue(value) {
  if (!value) return null
  const date = new Date(value)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

function compareValues(a, b) {
  const left = String(a ?? '').toLowerCase()
  const right = String(b ?? '').toLowerCase()
  return left.localeCompare(right, 'ko')
}

function splitPath(value) {
  const raw = String(value || '').trim()
  if (!raw) {
    return { hasValue: false, parentText: '', leaf: '' }
  }

  const parts = raw
    .split('>')
    .map((part) => part.trim())
    .filter(Boolean)

  if (!parts.length) {
    return { hasValue: false, parentText: '', leaf: '' }
  }

  if (parts.length === 1) {
    return { hasValue: true, parentText: '', leaf: parts[0] }
  }

  return {
    hasValue: true,
    parentText: `${parts.slice(0, -1).join(' > ')} >`,
    leaf: parts[parts.length - 1],
  }
}

function getRowValue(row, key) {
  const draft = rowDrafts.value[row.id]
  if (draft && Object.prototype.hasOwnProperty.call(draft, key)) {
    return draft[key]
  }
  return row[key]
}

function setRowDraft(rowId, key, value) {
  rowDrafts.value = {
    ...rowDrafts.value,
    [rowId]: {
      ...(rowDrafts.value[rowId] || {}),
      [key]: value,
    },
  }
}

async function saveRowField(row, key, immediateValue) {
  const nextValue = immediateValue !== undefined ? immediateValue : getRowValue(row, key)
  const currentValue = row[key] ?? null
  if ((nextValue ?? null) === currentValue) return

  try {
    const updated = await assetStore.update(row.id, { [key]: nextValue })
    applyAssetUpdate(row.id, key, nextValue, updated)
    clearRowDraft(row.id, key)
  } catch (error) {
    message.error(error.message || '자산 정보를 저장하지 못했습니다.')
  }
}

function clearRowDraft(rowId, key) {
  if (!rowDrafts.value[rowId]) return
  const nextDraft = { ...(rowDrafts.value[rowId] || {}) }
  delete nextDraft[key]
  rowDrafts.value = {
    ...rowDrafts.value,
    [rowId]: nextDraft,
  }
}

function applyAssetUpdate(id, key, value, updatedAsset) {
  const nextList = assetStore.list.map((asset) =>
    asset.id === id ? { ...asset, ...updatedAsset } : asset
  )
  assetStore.list = nextList

  assets.value = assets.value.map((asset) => {
    if (asset.id !== id) return asset
    const nextAsset = { ...asset, ...updatedAsset, [key]: value }
    if (key === 'manager_id') nextAsset.manager_name = findPersonName(value)
    if (key === 'supervisor_id') nextAsset.supervisor_name = findPersonName(value)
    return nextAsset
  })

  if (selectedAsset.value?.id === id) {
    selectedAsset.value = { ...selectedAsset.value, ...updatedAsset }
  }
  if (selectedAssetSummary.value?.id === id) {
    selectedAssetSummary.value = { ...selectedAssetSummary.value, ...updatedAsset, [key]: value }
  }
}

function findPersonName(personId) {
  if (!personId) return ''
  return personStore.list.find((person) => person.id === personId)?.name || ''
}

watch(
  equipmentTabs,
  (tabs) => {
    if (!tabs.length) {
      activeEquipmentTypeKey.value = null
      return
    }

    const exists = tabs.some((tab) => tab.key === activeEquipmentTypeKey.value)
    if (!exists) {
      activeEquipmentTypeKey.value = tabs[0].key
    }
  },
  { immediate: true }
)

onMounted(async () => {
  await Promise.all([
    loadAssets(),
    assetStore.fetchList(),
    catalogStore.fetchEquipmentTypes(),
    personStore.fetchList(),
  ])

  const qid = route.query.id ? Number(route.query.id) : null
  if (qid) await openDetail(qid)
})

async function loadAssets() {
  const { data } = await client.get('/api/assets/enriched')
  assets.value = data
}
</script>
