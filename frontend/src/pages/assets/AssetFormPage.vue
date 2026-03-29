<template>
  <PageShell :title="isEdit ? '자산 수정' : '자산 등록'">
    <n-card style="max-width: 700px">
      <n-form
        ref="formRef"
        :model="form"
        label-placement="left"
        label-width="120px"
        require-mark-placement="right-hanging"
      >
        <n-form-item label="자산명" path="asset_name" :rule="required('자산명을 입력하세요')">
          <n-input v-model:value="form.asset_name" placeholder="자산명" />
        </n-form-item>

        <n-form-item label="그룹" path="group_id" :rule="required('그룹을 선택하세요')">
          <n-select
            v-model:value="form.group_id"
            :options="groupOptions"
            placeholder="코드 보유 그룹만 선택 가능"
            filterable
          />
        </n-form-item>

        <n-form-item label="장비 종류" path="equipment_type_id">
          <n-select
            v-model:value="form.equipment_type_id"
            :options="typeOptions"
            placeholder="장비 종류"
            clearable
          />
        </n-form-item>

        <n-form-item label="위치" path="location_id">
          <n-select
            v-model:value="form.location_id"
            :options="locationOptions"
            placeholder="위치"
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

        <n-form-item label="상태" path="status">
          <n-select
            v-model:value="form.status"
            :options="[
              { label: '운영중', value: 'OPERATING' },
              { label: '점검중', value: 'MAINTENANCE' },
              { label: '고장', value: 'FAULTY' },
              { label: '폐기', value: 'DISPOSED' },
            ]"
          />
        </n-form-item>

        <n-form-item label="담당자" path="manager_id">
          <n-select
            v-model:value="form.manager_id"
            :options="personOptions"
            placeholder="담당자"
            clearable
            filterable
          />
        </n-form-item>

        <n-form-item label="용도" path="purpose">
          <n-input v-model:value="form.purpose" placeholder="용도 설명" type="textarea" :rows="2" />
        </n-form-item>

        <n-form-item label="설치일" path="install_date">
          <n-date-picker
            v-model:formatted-value="form.install_date"
            type="date"
            clearable
            value-format="yyyy-MM-dd"
          />
        </n-form-item>

        <div style="display: flex; justify-content: flex-end; gap: 8px; margin-top: 8px">
          <n-button @click="$router.push('/assets')">취소</n-button>
          <n-button type="primary" :loading="saving" @click="handleSubmit">저장</n-button>
        </div>
      </n-form>
    </n-card>
  </PageShell>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'

import client from '@/api/client'
import PageShell from '@/components/common/PageShell.vue'
import { useAssetStore } from '@/stores/assetStore'
import { useCatalogStore } from '@/stores/catalogStore'
import { useGroupStore } from '@/stores/groupStore'
import { useLocationStore } from '@/stores/locationStore'
import { usePersonStore } from '@/stores/personStore'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const assetStore = useAssetStore()
const groupStore = useGroupStore()
const locationStore = useLocationStore()
const catalogStore = useCatalogStore()
const personStore = usePersonStore()

const isEdit = computed(() => !!route.params.id)
const formRef = ref(null)
const saving = ref(false)

const form = ref({
  asset_name: '',
  group_id: null,
  equipment_type_id: null,
  location_id: null,
  importance: '중',
  status: 'OPERATING',
  manager_id: null,
  purpose: '',
  install_date: null,
})

const required = (msg) => ({ required: true, message: msg, trigger: ['blur', 'change'] })

const groupOptions = computed(() =>
  groupStore.codeable.map((g) => ({
    label: `${g.full_path || g.name} [${g.display_code || g.code}]`,
    value: g.id,
  }))
)
const locationOptions = computed(() =>
  locationStore.list.map((l) => ({ label: l.full_path || l.name, value: l.id }))
)
const personOptions = computed(() =>
  personStore.list.map((p) => ({ label: p.name, value: p.id }))
)
const typeOptions = ref([])

async function loadTypes() {
  const data = await client.get('/api/catalogs/equipment-types').then((r) => r.data)
  typeOptions.value = data.map((t) => ({ label: t.name, value: t.id }))
}

async function handleSubmit() {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }

  saving.value = true
  try {
    if (isEdit.value) {
      await assetStore.update(Number(route.params.id), form.value)
      message.success('수정되었습니다')
    } else {
      await assetStore.create(form.value)
      message.success('등록되었습니다')
    }
    router.push('/assets')
  } catch (error) {
    message.error(error.message)
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await Promise.all([
    groupStore.fetchCodeable(),
    locationStore.fetchList(),
    catalogStore.fetchEquipmentTypes?.() || Promise.resolve(),
    personStore.fetchList(),
    loadTypes(),
  ])

  if (isEdit.value) {
    await assetStore.fetchOne(Number(route.params.id))
    Object.assign(form.value, assetStore.current)
  }
})
</script>
