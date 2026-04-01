<template>
  <PageShell title="자산 등록">
    <!-- 등록된 자산 간소 목록 -->
    <n-card title="등록된 자산 목록" style="margin-bottom:16px;">
      <ListHeader title="등록된 자산 목록" :count="assetStore.list.length">
        <template #extra>
          <n-button type="primary" @click="openRegisterModal">
            설비 등록
          </n-button>
        </template>
      </ListHeader>
      <div style="max-height:220px; overflow-y:auto; border:1px solid var(--n-border-color, #e0e0e6); border-radius:3px;">
        <n-data-table
          :columns="listColumns"
          :data="assetStore.list"
          :loading="assetStore.loading"
          size="small"
          striped
        />
      </div>
    </n-card>

    <n-modal
      v-model:show="showRegisterModal"
      preset="card"
      title="설비 등록"
      :mask-closable="false"
      style="width:min(860px, calc(100vw - 32px));"
    >
      <n-tabs v-model:value="activeTab" type="line" animated>
        <!-- ─── 단일 등록 ─── -->
        <n-tab-pane name="single" tab="단일 등록">
          <n-form
            ref="formRef"
            :model="form"
            :rules="rules"
            label-placement="left"
            label-width="100px"
            style="max-width:680px; margin-top:12px;"
          >
            <n-form-item label="자산명" path="asset_name">
              <n-input v-model:value="form.asset_name" placeholder="자산명 입력" />
            </n-form-item>

            <n-form-item label="&#xADF8;&#xB8F9; &#xACBD;&#xB85C;">
              <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap; width:100%;">
                <n-select
                  v-model:value="selectedGroupLevel1"
                  :options="topLevelGroupOptions"
                  placeholder="1&#xCC28; &#xADF8;&#xB8F9;"
                  clearable
                  style="flex:1 1 160px; min-width:160px;"
                />
                <span style="color:#999;">&gt;</span>
                <n-select
                  v-model:value="selectedGroupLevel2"
                  :options="secondLevelGroupOptions"
                  placeholder="2&#xCC28; &#xADF8;&#xB8F9;"
                  clearable
                  :disabled="!selectedGroupLevel1"
                  style="flex:1 1 160px; min-width:160px;"
                />
                <template v-if="thirdLevelGroupOptions.length">
                  <span style="color:#999;">&gt;</span>
                  <n-select
                    v-model:value="selectedGroupLevel3"
                    :options="thirdLevelGroupOptions"
                    placeholder="3&#xCC28; &#xADF8;&#xB8F9;"
                    clearable
                    :disabled="!selectedGroupLevel2"
                    style="flex:0 1 120px; min-width:120px;"
                  />
                </template>
                <template v-if="fourthLevelGroupOptions.length">
                  <span style="color:#999;">&gt;</span>
                  <n-select
                    v-model:value="selectedGroupLevel4"
                    :options="fourthLevelGroupOptions"
                    placeholder="4&#xCC28; &#xADF8;&#xB8F9;"
                    clearable
                    :disabled="!selectedGroupLevel3"
                    style="flex:0 1 120px; min-width:120px;"
                  />
                </template>
              </div>
            </n-form-item>

            <n-form-item label="&#xCD5C;&#xC885; &#xADF8;&#xB8F9;" path="group_id">
              <n-select
                v-model:value="form.group_id"
                :options="codeableGroupOptions"
                placeholder="&#xCD5C;&#xC885; &#xADF8;&#xB8F9; &#xC120;&#xD0DD;"
                :disabled="!activeGroupBranch"
                filterable
              />
            </n-form-item>

            <n-form-item label="&#xC120;&#xD0DD; &#xACB0;&#xACFC;">
              <div style="width:100%; min-height:34px; display:flex; align-items:center; padding:0 12px; border:1px solid var(--n-border-color, #e0e0e6); border-radius:3px; background:var(--n-color-embedded, #fafafc); color:var(--n-text-color, #111827);">
                {{ selectedGroupSummary }}
              </div>
            </n-form-item>

            <n-form-item label="장비종류" path="equipment_type_id">
              <n-select
                v-model:value="form.equipment_type_id"
                :options="typeOptions"
                placeholder="장비종류 선택"
                filterable
              />
            </n-form-item>

            <n-form-item label="자산코드 미리보기">
              <AssetCodePreview :group-id="form.group_id" :type-id="form.equipment_type_id" />
            </n-form-item>

            <n-form-item label="위치">
              <n-select
                v-model:value="form.location_id"
                :options="locationOptions"
                placeholder="위치 선택 (선택사항)"
                clearable
                filterable
              />
            </n-form-item>

            <n-form-item label="중요도" path="importance">
              <n-radio-group v-model:value="form.importance">
                <n-radio value="상">상</n-radio>
                <n-radio value="중">중</n-radio>
                <n-radio value="하">하</n-radio>
              </n-radio-group>
            </n-form-item>

            <n-form-item label="설치일">
              <n-date-picker
                v-model:value="installDateMs"
                type="date"
                clearable
                style="width:100%;"
              />
            </n-form-item>

            <n-form-item>
              <n-button type="primary" :loading="saving" @click="handleCreate">
                등록
              </n-button>
            </n-form-item>
          </n-form>
        </n-tab-pane>

        <!-- ─── 대량 등록 ─── -->
        <n-tab-pane name="bulk" tab="대량 등록">
          <div style="margin-top:12px;">
            <n-space vertical>
              <n-button @click="downloadTemplate">
                📥 템플릿 다운로드 (.xlsx)
              </n-button>

              <n-upload
                ref="uploadRef"
                :max="1"
                accept=".xlsx"
                :default-upload="false"
                @change="onFileChange"
              >
                <n-upload-dragger>
                  <n-text>엑셀 파일을 여기에 드래그하거나 클릭하여 업로드</n-text>
                  <n-text depth="3" style="display:block; font-size:12px;">
                    (.xlsx, 템플릿 양식 사용)
                  </n-text>
                </n-upload-dragger>
              </n-upload>

              <div v-if="bulkResult">
                <n-alert
                  :type="bulkResult.errors.length ? 'warning' : 'success'"
                  :title="`등록 완료: ${bulkResult.success}건 성공`"
                >
                  <div v-if="bulkResult.errors.length">
                    <div v-for="e in bulkResult.errors" :key="e.row" style="font-size:12px;">
                      행 {{ e.row }}: {{ e.error }}
                    </div>
                  </div>
                </n-alert>
              </div>

              <n-button
                v-if="bulkFile"
                type="primary"
                :loading="bulkSaving"
                @click="handleBulkRegister"
              >
                대량 등록 실행
              </n-button>
            </n-space>
          </div>
        </n-tab-pane>
      </n-tabs>
    </n-modal>
  </PageShell>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useMessage } from 'naive-ui'
import PageShell from '@/components/common/PageShell.vue'
import ListHeader from '@/components/common/ListHeader.vue'
import AssetCodePreview from '@/components/assets/AssetCodePreview.vue'
import { useAssetStore } from '@/stores/assetStore'
import { useGroupStore } from '@/stores/groupStore'
import { useCatalogStore } from '@/stores/catalogStore'
import { useLocationStore } from '@/stores/locationStore'
import { assetsApi } from '@/api/assetsApi'

const message  = useMessage()
const assetStore   = useAssetStore()
const groupStore   = useGroupStore()
const catalogStore = useCatalogStore()
const locationStore = useLocationStore()

const showRegisterModal = ref(false)
const activeTab = ref('single')
const formRef   = ref(null)
const saving    = ref(false)
const bulkSaving = ref(false)
const bulkFile   = ref(null)
const bulkResult = ref(null)
const uploadRef  = ref(null)
const installDateMs = ref(null)
const selectedGroupLevel1 = ref(null)
const selectedGroupLevel2 = ref(null)
const selectedGroupLevel3 = ref(null)
const selectedGroupLevel4 = ref(null)

const form = ref({
  asset_name: '',
  group_id: null,
  equipment_type_id: null,
  location_id: null,
  importance: '중',
})

const rules = {
  asset_name:        { required: true, message: '자산명을 입력해주세요' },
  group_id:          { required: true, type: 'number', message: '그룹을 선택해주세요' },
  equipment_type_id: { required: true, type: 'number', message: '장비종류를 선택해주세요' },
}

const listColumns = [
  { title: '자산코드', key: 'asset_code', width: 160 },
  { title: '자산명',   key: 'asset_name', width: 200 },
  { title: '중요도',   key: 'importance', width: 70 },
  { title: '상태',     key: 'status', width: 90 },
  { title: '설치일',   key: 'install_date', width: 100 },
]

const topLevelGroupOptions = computed(() =>
  groupStore.list
    .filter((group) => group.parent_id == null)
    .map((group) => ({ label: group.name, value: group.id }))
)

const secondLevelGroupOptions = computed(() =>
  groupStore.list
    .filter((group) => group.parent_id === selectedGroupLevel1.value)
    .map((group) => ({ label: group.name, value: group.id }))
)

const thirdLevelGroupOptions = computed(() =>
  groupStore.list
    .filter((group) => group.parent_id === selectedGroupLevel2.value)
    .map((group) => ({ label: group.name, value: group.id }))
)

const fourthLevelGroupOptions = computed(() =>
  groupStore.list
    .filter((group) => group.parent_id === selectedGroupLevel3.value)
    .map((group) => ({ label: group.name, value: group.id }))
)

const activeGroupBranch = computed(() => {
  return selectedGroupLevel4.value || selectedGroupLevel3.value || selectedGroupLevel2.value || selectedGroupLevel1.value || null
})

const codeableGroupOptions = computed(() => {
  const branch = groupStore.list.find((group) => group.id === activeGroupBranch.value)
  if (!branch?.full_path) {
    return []
  }
  return groupStore.list
    .filter((group) => {
      if (!group.code) {
        return false
      }
      return group.full_path === branch.full_path || group.full_path.startsWith(`${branch.full_path} >`)
    })
    .map((group) => ({ label: `${group.full_path} (${group.display_code || group.code})`, value: group.id }))
})

const selectedGroupSummary = computed(() => {
  const selectedGroup = groupStore.list.find((group) => group.id === form.value.group_id)
  if (!selectedGroup) {
    const branch = groupStore.list.find((group) => group.id === activeGroupBranch.value)
    return branch?.full_path || '그룹을 순차적으로 선택해주세요'
  }
  return `${selectedGroup.full_path} (${selectedGroup.display_code || selectedGroup.code})`
})

const typeOptions = computed(() =>
  catalogStore.equipmentTypes.map(t => ({ label: `${t.name} (${t.code})`, value: t.id }))
)

const leafLocationNodes = computed(() => {
  const parentIds = new Set(locationStore.list.map(l => l.parent_id).filter(id => id != null))
  return locationStore.list
    .filter(l => !parentIds.has(l.id))
})

const locationFilterTokens = computed(() => {
  const selectedNodeId = form.value.group_id || activeGroupBranch.value
  const selectedGroup = groupStore.list.find((group) => group.id === selectedNodeId)
  if (!selectedGroup) {
    return []
  }

  const chainNames = []
  let current = selectedGroup
  while (current) {
    chainNames.unshift(current.name)
    current = groupStore.list.find((group) => group.id === current.parent_id) || null
  }

  return chainNames.filter((name) =>
    leafLocationNodes.value.some((location) => (location.full_path || '').includes(name))
  )
})

const locationOptions = computed(() => {
  const filteredNodes = locationFilterTokens.value.length
    ? leafLocationNodes.value.filter((location) =>
        locationFilterTokens.value.every((token) => (location.full_path || '').includes(token))
      )
    : leafLocationNodes.value

  return filteredNodes.map((location) => ({ label: location.full_path || location.name, value: location.id }))
})

watch(selectedGroupLevel1, (value) => {
  const parentMatches = groupStore.list.some((group) => group.id === selectedGroupLevel2.value && group.parent_id === value)
  if (!parentMatches) {
    selectedGroupLevel2.value = null
  }
})

watch(selectedGroupLevel2, (value) => {
  const parentMatches = groupStore.list.some((group) => group.id === selectedGroupLevel3.value && group.parent_id === value)
  if (!parentMatches) {
    selectedGroupLevel3.value = null
  }
})

watch(selectedGroupLevel3, (value) => {
  const parentMatches = groupStore.list.some((group) => group.id === selectedGroupLevel4.value && group.parent_id === value)
  if (!parentMatches) {
    selectedGroupLevel4.value = null
  }
})

watch(codeableGroupOptions, (options) => {
  if (!options.some((option) => option.value === form.value.group_id)) {
    form.value.group_id = null
  }
})

watch(locationOptions, (options) => {
  if (!options.some((option) => option.value === form.value.location_id)) {
    form.value.location_id = null
  }
})

watch(() => form.value.group_id, (groupId) => {
  const selectedGroup = groupStore.list.find((group) => group.id === groupId)
  if (!selectedGroup) {
    return
  }
  const chain = []
  let current = selectedGroup
  while (current) {
    chain.unshift(current)
    current = groupStore.list.find((group) => group.id === current.parent_id) || null
  }

  selectedGroupLevel1.value = chain[0]?.id || null
  selectedGroupLevel2.value = chain[1]?.id || null
  selectedGroupLevel3.value = chain[2]?.id || null
  selectedGroupLevel4.value = chain[3]?.id || null
})

function openRegisterModal() {
  activeTab.value = 'single'
  showRegisterModal.value = true
}

async function handleCreate() {
  try {
    await formRef.value.validate()
  } catch { return }

  saving.value = true
  try {
    const body = {
      ...form.value,
      install_date: installDateMs.value
        ? (() => { const d = new Date(installDateMs.value); return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}` })()
        : null,
    }
    await assetStore.create(body)
    message.success('자산이 등록되었습니다')
    form.value = { asset_name: '', group_id: null, equipment_type_id: null, location_id: null, importance: '중' }
    selectedGroupLevel1.value = null
    selectedGroupLevel2.value = null
    selectedGroupLevel3.value = null
    selectedGroupLevel4.value = null
    installDateMs.value = null
    showRegisterModal.value = false
    await assetStore.fetchList()
  } catch (e) {
    message.error(e.message || '등록 실패')
  } finally {
    saving.value = false
  }
}

function onFileChange({ file }) {
  bulkFile.value = file?.file ?? null
  bulkResult.value = null
}

async function downloadTemplate() {
  try {
    const res = await assetsApi.bulkTemplate()
    const url = URL.createObjectURL(new Blob([res.data]))
    const a = document.createElement('a')
    a.href = url
    a.download = '자산_대량등록_템플릿.xlsx'
    a.click()
    URL.revokeObjectURL(url)
  } catch {
    message.error('템플릿 다운로드 실패')
  }
}

async function handleBulkRegister() {
  if (!bulkFile.value) return
  bulkSaving.value = true
  try {
    bulkResult.value = await assetStore.bulkCreate(bulkFile.value)
    message.success(`${bulkResult.value.success}건 등록 완료`)
    await assetStore.fetchList()
  } catch (e) {
    message.error(e.message || '대량 등록 실패')
  } finally {
    bulkSaving.value = false
  }
}

onMounted(async () => {
  await Promise.all([
    assetStore.fetchList(),
    groupStore.fetchList(),
    catalogStore.fetchEquipmentTypes(),
    locationStore.fetchList(),
  ])
})
</script>
