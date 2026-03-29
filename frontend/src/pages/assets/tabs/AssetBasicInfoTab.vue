<template>
  <div>
    <n-form
      :model="form"
      label-placement="left"
      label-width="110px"
      style="max-width: 560px; margin-top: 8px;"
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
      <n-form-item label="시리얼 번호">
        <n-input v-model:value="form.serial_number" />
      </n-form-item>
      <n-form-item label="상태">
        <n-select v-model:value="form.status" :options="statusOptions" />
      </n-form-item>
      <n-form-item label="담당자">
        <n-select v-model:value="form.manager_id" :options="managerOptions" clearable />
      </n-form-item>
      <n-form-item label="중요도">
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
          style="width: 100%;"
        />
      </n-form-item>
      <n-form-item>
        <n-button type="primary" :loading="saving" @click="save">저장</n-button>
      </n-form-item>
    </n-form>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useMessage } from 'naive-ui'
import { useAssetStore } from '@/stores/assetStore'
import { usePersonStore } from '@/stores/personStore'

const props = defineProps({ asset: { type: Object, required: true } })
const emit = defineEmits(['updated'])

const message = useMessage()
const assetStore = useAssetStore()
const personStore = usePersonStore()

const saving = ref(false)
const installDateMs = ref(null)

const form = ref({
  asset_name: '',
  purpose: '',
  model_name: '',
  serial_number: '',
  status: 'OPERATING',
  manager_id: null,
  importance: '중',
})

const statusOptions = [
  { label: '운영중', value: 'OPERATING' },
  { label: '점검중', value: 'MAINTENANCE' },
  { label: '고장', value: 'FAULTY' },
  { label: '폐기', value: 'DISPOSED' },
]

const managerOptions = computed(() => {
  const options = personStore.list
    .filter((person) =>
      (person.group_roles || []).some(
        (role) => role.group_id === props.asset.group_id && role.role_type === 'PRIMARY'
      )
    )
    .map((person) => ({ label: person.name, value: person.id }))

  const currentManagerId = form.value.manager_id
  if (currentManagerId && !options.some((option) => option.value === currentManagerId)) {
    const currentPerson = personStore.list.find((person) => person.id === currentManagerId)
    if (currentPerson) {
      options.unshift({ label: currentPerson.name, value: currentPerson.id })
    }
  }

  return options
})

watch(
  () => props.asset,
  (asset) => {
    if (!asset) return

    Object.keys(form.value).forEach((key) => {
      if (key === 'manager_id') {
        form.value.manager_id = asset.manager_id ?? asset.resolved_manager_id ?? null
        return
      }
      form.value[key] = asset[key] ?? form.value[key]
    })
    installDateMs.value = asset.install_date ? new Date(asset.install_date).getTime() : null
  },
  { immediate: true }
)

async function save() {
  saving.value = true
  try {
    const body = {
      ...form.value,
      install_date: installDateMs.value
        ? (() => {
            const date = new Date(installDateMs.value)
            return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(
              date.getDate()
            ).padStart(2, '0')}`
          })()
        : null,
    }
    await assetStore.update(props.asset.id, body)
    message.success('저장되었습니다')
    emit('updated')
  } catch (error) {
    message.error(error.message || '저장에 실패했습니다')
  } finally {
    saving.value = false
  }
}
</script>
