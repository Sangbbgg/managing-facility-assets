<template>
  <PageShell title="자산 등록">
    <!-- 등록된 자산 간소 목록 -->
    <n-card title="등록된 자산 목록" style="margin-bottom:16px;">
      <n-data-table
        :columns="listColumns"
        :data="assetStore.list"
        :loading="assetStore.loading"
        :max-height="220"
        size="small"
        striped
      />
    </n-card>

    <!-- 등록 모드 탭 -->
    <n-card>
      <n-tabs v-model:value="activeTab" type="line">
        <!-- ─── 단일 등록 ─── -->
        <n-tab-pane name="single" tab="단일 등록">
          <n-form
            ref="formRef"
            :model="form"
            :rules="rules"
            label-placement="left"
            label-width="100px"
            style="max-width:600px; margin-top:12px;"
          >
            <n-form-item label="자산명" path="asset_name">
              <n-input v-model:value="form.asset_name" placeholder="자산명 입력" />
            </n-form-item>

            <n-form-item label="그룹" path="group_id">
              <n-select
                v-model:value="form.group_id"
                :options="codeableGroupOptions"
                placeholder="그룹 선택"
                filterable
              />
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

            <n-form-item label="담당자">
              <n-select
                v-model:value="form.manager_id"
                :options="personOptions"
                placeholder="담당자 선택 (선택사항)"
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
    </n-card>
  </PageShell>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import PageShell from '@/components/common/PageShell.vue'
import AssetCodePreview from '@/components/assets/AssetCodePreview.vue'
import { useAssetStore } from '@/stores/assetStore'
import { useGroupStore } from '@/stores/groupStore'
import { useCatalogStore } from '@/stores/catalogStore'
import { useLocationStore } from '@/stores/locationStore'
import { usePersonStore } from '@/stores/personStore'
import { assetsApi } from '@/api/assetsApi'

const message  = useMessage()
const assetStore   = useAssetStore()
const groupStore   = useGroupStore()
const catalogStore = useCatalogStore()
const locationStore = useLocationStore()
const personStore  = usePersonStore()

const activeTab = ref('single')
const formRef   = ref(null)
const saving    = ref(false)
const bulkSaving = ref(false)
const bulkFile   = ref(null)
const bulkResult = ref(null)
const uploadRef  = ref(null)
const installDateMs = ref(null)

const form = ref({
  asset_name: '',
  group_id: null,
  equipment_type_id: null,
  location_id: null,
  manager_id: null,
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

const codeableGroupOptions = computed(() =>
  groupStore.list
    .filter(g => g.code)
    .map(g => ({ label: `${g.name} (${g.code})`, value: g.id }))
)

const typeOptions = computed(() =>
  catalogStore.equipmentTypes.map(t => ({ label: `${t.name} (${t.code})`, value: t.id }))
)

const locationOptions = computed(() =>
  locationStore.list.map(l => ({ label: l.name, value: l.id }))
)

const personOptions = computed(() =>
  personStore.list.map(p => ({ label: p.name, value: p.id }))
)

async function handleCreate() {
  try {
    await formRef.value.validate()
  } catch { return }

  saving.value = true
  try {
    const body = {
      ...form.value,
      install_date: installDateMs.value
        ? new Date(installDateMs.value).toISOString().slice(0, 10)
        : null,
    }
    await assetStore.create(body)
    message.success('자산이 등록되었습니다')
    form.value = { asset_name: '', group_id: null, equipment_type_id: null, location_id: null, manager_id: null, importance: '중' }
    installDateMs.value = null
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
    personStore.fetchList(),
  ])
})
</script>
