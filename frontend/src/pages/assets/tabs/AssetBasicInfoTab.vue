<template>
  <div>
    <n-form
      ref="formRef"
      :model="form"
      label-placement="left"
      label-width="110px"
      style="max-width:560px; margin-top:8px;"
    >
      <n-form-item label="자산명">
        <n-input v-model:value="form.asset_name" />
      </n-form-item>
      <n-form-item label="용도">
        <n-input v-model:value="form.purpose" />
      </n-form-item>
      <n-form-item label="모델명">
        <n-input v-model:value="form.model_name" />
      </n-form-item>
      <n-form-item label="시리얼번호">
        <n-input v-model:value="form.serial_number" />
      </n-form-item>
      <n-form-item label="IP주소">
        <n-input v-model:value="form.ip_address" />
      </n-form-item>
      <n-form-item label="상태">
        <n-select v-model:value="form.status" :options="statusOptions" />
      </n-form-item>
      <n-form-item label="OS">
        <n-select v-model:value="form.os_id" :options="osOptions" clearable />
      </n-form-item>
      <n-form-item label="백신">
        <n-select v-model:value="form.av_id" :options="avOptions" clearable />
      </n-form-item>
      <n-form-item label="담당자">
        <n-select v-model:value="form.manager_id" :options="personOptions" clearable />
      </n-form-item>
      <n-form-item label="관리감독자">
        <n-select v-model:value="form.supervisor_id" :options="personOptions" clearable />
      </n-form-item>
      <n-form-item label="중요도">
        <n-radio-group v-model:value="form.importance">
          <n-radio value="상">상</n-radio>
          <n-radio value="중">중</n-radio>
          <n-radio value="하">하</n-radio>
        </n-radio-group>
      </n-form-item>
      <n-form-item label="설치일">
        <n-date-picker v-model:value="installDateMs" type="date" clearable style="width:100%;" />
      </n-form-item>
      <n-form-item>
        <n-button type="primary" :loading="saving" @click="save">저장</n-button>
      </n-form-item>
    </n-form>
  </div>
</template>

<script setup>
import { ref, watch, computed, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { useAssetStore } from '@/stores/assetStore'
import { useCatalogStore } from '@/stores/catalogStore'
import { usePersonStore } from '@/stores/personStore'

const props = defineProps({ asset: { type: Object, required: true } })
const emit  = defineEmits(['updated'])
const message     = useMessage()
const assetStore  = useAssetStore()
const catalogStore = useCatalogStore()
const personStore  = usePersonStore()

const saving = ref(false)
const installDateMs = ref(null)

const form = ref({
  asset_name: '', purpose: '', model_name: '', serial_number: '',
  ip_address: '', status: 'OPERATING', os_id: null, av_id: null,
  manager_id: null, supervisor_id: null, importance: '중',
})

const statusOptions = [
  { label: '운영중', value: 'OPERATING' },
  { label: '점검중', value: 'MAINTENANCE' },
  { label: '장애',   value: 'FAULTY' },
  { label: '폐기',   value: 'DISPOSED' },
]
const osOptions      = computed(() => catalogStore.osList.map(o => ({ label: o.name, value: o.id })))
const avOptions      = computed(() => catalogStore.avList.map(a  => ({ label: a.name, value: a.id })))
const personOptions  = computed(() => personStore.list.map(p => ({ label: p.name, value: p.id })))

watch(() => props.asset, (a) => {
  if (!a) return
  Object.keys(form.value).forEach(k => { form.value[k] = a[k] ?? form.value[k] })
  installDateMs.value = a.install_date ? new Date(a.install_date).getTime() : null
}, { immediate: true })

async function save() {
  saving.value = true
  try {
    const body = {
      ...form.value,
      install_date: installDateMs.value
        ? new Date(installDateMs.value).toISOString().slice(0, 10)
        : null,
    }
    await assetStore.update(props.asset.id, body)
    message.success('저장되었습니다')
    emit('updated')
  } catch (e) {
    message.error(e.message || '저장 실패')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  catalogStore.fetchOs()
  catalogStore.fetchAv()
  personStore.fetchList()
})
</script>
