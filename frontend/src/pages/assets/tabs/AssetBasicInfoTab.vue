<template>
  <div>
    <n-form
      :model="form"
      label-placement="left"
      label-width="120px"
      style="max-width: 680px; margin-top: 8px"
    >
      <n-form-item label="자산명">
        <n-input v-model:value="form.asset_name" />
      </n-form-item>

      <n-form-item label="용도">
        <n-input v-model:value="form.purpose" />
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
          style="width: 100%"
        />
      </n-form-item>

      <n-divider style="margin: 8px 0 16px">대표 네트워크 선택</n-divider>

      <n-form-item label="대표 NIC">
        <n-select
          v-model:value="form.representative_nic_id"
          :options="nicOptions"
          clearable
          placeholder="수집된 NIC 중 선택"
        />
      </n-form-item>

      <n-form-item label="미사용 NIC">
        <n-select
          v-model:value="form.unused_nic_ids"
          :options="unusedNicOptions"
          multiple
          clearable
          placeholder="미사용 NIC 선택"
        />
      </n-form-item>

      <n-form-item label="대표 IP">
        <n-input :value="selectedNicIp" readonly />
      </n-form-item>

      <n-form-item label="대표 MAC">
        <n-input :value="selectedNicMac" readonly />
      </n-form-item>

      <n-divider style="margin: 8px 0 16px">대표 계정 선택</n-divider>

      <n-form-item label="대표 계정">
        <n-select
          v-model:value="form.representative_account_id"
          :options="accountOptions"
          clearable
          placeholder="수집된 계정 중 선택"
        />
      </n-form-item>

      <n-form-item label="미사용 계정">
        <n-select
          v-model:value="form.disabled_account_ids"
          :options="disabledAccountOptions"
          multiple
          clearable
          placeholder="미사용 계정 선택"
        />
      </n-form-item>

      <n-form-item label="대표 계정 상태">
        <n-input :value="selectedAccountEnabledLabel" readonly />
      </n-form-item>

      <n-form-item label="대표 계정 주석">
        <n-input :value="selectedAccountComment" readonly />
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

import { hardwareApi } from '@/api/hardwareApi'
import { softwareApi } from '@/api/softwareApi'
import { useAssetStore } from '@/stores/assetStore'
import { usePersonStore } from '@/stores/personStore'

const props = defineProps({
  asset: { type: Object, required: true },
  nics: { type: Array, default: () => [] },
  accounts: { type: Array, default: () => [] },
})

const emit = defineEmits(['updated'])

const message = useMessage()
const assetStore = useAssetStore()
const personStore = usePersonStore()

const saving = ref(false)
const installDateMs = ref(null)

const form = ref({
  asset_name: '',
  purpose: '',
  status: 'OPERATING',
  manager_id: null,
  importance: '중',
  representative_nic_id: null,
  unused_nic_ids: [],
  representative_account_id: null,
  disabled_account_ids: [],
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
      (person.group_roles || []).some((role) => role.group_id === props.asset.group_id)
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

const nicOptions = computed(() =>
  (props.nics || []).map((nic) => ({
    label: formatNicLabel(nic),
    value: nic.id,
  }))
)

const unusedNicOptions = computed(() =>
  (props.nics || [])
    .filter((nic) => nic.id !== form.value.representative_nic_id)
    .map((nic) => ({
      label: formatNicLabel(nic),
      value: nic.id,
    }))
)

const selectedNic = computed(() =>
  (props.nics || []).find((nic) => nic.id === form.value.representative_nic_id) || null
)

const selectedNicIp = computed(() => selectedNic.value?.ipv4_address || '')
const selectedNicMac = computed(() => selectedNic.value?.mac_address || '')

const accountOptions = computed(() =>
  (props.accounts || []).map((account) => ({
    label: formatAccountLabel(account),
    value: account.id,
  }))
)

const disabledAccountOptions = computed(() =>
  (props.accounts || [])
    .filter((account) => account.id !== form.value.representative_account_id)
    .map((account) => ({
      label: formatAccountLabel(account),
      value: account.id,
    }))
)

const selectedAccount = computed(() =>
  (props.accounts || []).find((account) => account.id === form.value.representative_account_id) || null
)

const selectedAccountEnabledLabel = computed(() => {
  if (!selectedAccount.value) return ''
  return selectedAccount.value.enabled ? '활성' : '미사용'
})

const selectedAccountComment = computed(() => selectedAccount.value?.comment || '')

watch(
  () => props.asset,
  (asset) => {
    if (!asset) return
    form.value = {
      asset_name: asset.asset_name || '',
      purpose: asset.purpose || '',
      status: asset.status || 'OPERATING',
      manager_id: asset.manager_id ?? asset.resolved_manager_id ?? null,
      importance: asset.importance || '중',
      representative_nic_id: asset.representative_nic_id || null,
      unused_nic_ids: (props.nics || []).filter((nic) => nic.is_unused).map((nic) => nic.id),
      representative_account_id: asset.representative_account_id || null,
      disabled_account_ids: (props.accounts || [])
        .filter((account) => account.enabled === false)
        .map((account) => account.id),
    }
    installDateMs.value = asset.install_date ? new Date(asset.install_date).getTime() : null
  },
  { immediate: true }
)

watch(
  () => props.nics,
  (nics) => {
    form.value.unused_nic_ids = (nics || [])
      .filter((nic) => nic.is_unused && nic.id !== form.value.representative_nic_id)
      .map((nic) => nic.id)
  },
  { immediate: true, deep: true }
)

watch(
  () => props.accounts,
  (accounts) => {
    form.value.disabled_account_ids = (accounts || [])
      .filter((account) => account.enabled === false && account.id !== form.value.representative_account_id)
      .map((account) => account.id)
  },
  { immediate: true, deep: true }
)

watch(
  () => form.value.representative_nic_id,
  (nicId) => {
    if (!nicId) return
    form.value.unused_nic_ids = form.value.unused_nic_ids.filter((id) => id !== nicId)
  }
)

watch(
  () => form.value.representative_account_id,
  (accountId) => {
    if (!accountId) return
    form.value.disabled_account_ids = form.value.disabled_account_ids.filter((id) => id !== accountId)
  }
)

async function save() {
  saving.value = true
  try {
    const body = {
      asset_name: form.value.asset_name,
      purpose: form.value.purpose,
      status: form.value.status,
      manager_id: form.value.manager_id,
      importance: form.value.importance,
      representative_nic_id: form.value.representative_nic_id,
      representative_account_id: form.value.representative_account_id,
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
    await hardwareApi.updateUnusedNics(props.asset.id, form.value.unused_nic_ids)
    await softwareApi.updateAccountStatus(props.asset.id, form.value.disabled_account_ids)
    message.success('저장되었습니다')
    emit('updated')
  } catch (error) {
    message.error(error.message || '저장에 실패했습니다')
  } finally {
    saving.value = false
  }
}

function formatNicLabel(nic) {
  return [
    nic.connection_name || nic.adapter_name || `NIC ${nic.id}`,
    nic.mac_address ? `(${nic.mac_address})` : '',
    nic.ipv4_address ? `- ${nic.ipv4_address}` : '',
  ]
    .filter(Boolean)
    .join(' ')
}

function formatAccountLabel(account) {
  return [
    account.account_name || `계정 ${account.id}`,
    account.enabled === false ? '(미사용)' : '(활성)',
    account.comment ? `- ${account.comment}` : '',
  ]
    .filter(Boolean)
    .join(' ')
}
</script>
