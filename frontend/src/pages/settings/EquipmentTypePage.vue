<template>
  <PageShell title="장비 종류 관리">
    <n-card style="margin-bottom:16px">
      <n-form inline label-placement="left">
        <n-form-item label="장비명">
          <n-input v-model:value="form.name" placeholder="예) 서버" style="width:160px" />
        </n-form-item>
        <n-form-item label="코드">
          <n-input v-model:value="form.code" placeholder="예) SER" style="width:100px" />
        </n-form-item>
        <n-form-item label="설명">
          <n-input v-model:value="form.description" placeholder="설명 (선택)" style="width:200px" />
        </n-form-item>
        <n-button type="primary" :loading="saving" @click="handleAdd">추가</n-button>
      </n-form>
    </n-card>

    <n-card>
      <DataTable :columns="columns" :data="list" :loading="loading" />
    </n-card>

    <n-modal v-model:show="editModal" preset="dialog" title="장비 종류 수정">
      <n-form label-placement="left" label-width="80px">
        <n-form-item label="장비명"><n-input v-model:value="editForm.name" /></n-form-item>
        <n-form-item label="코드">
          <n-input v-model:value="editForm.code" disabled />
          <n-text depth="3" style="font-size:12px;margin-left:8px">코드는 변경 불가 (자산코드 채번에 사용)</n-text>
        </n-form-item>
        <n-form-item label="설명"><n-input v-model:value="editForm.description" /></n-form-item>
      </n-form>
      <template #action>
        <n-button @click="editModal = false">취소</n-button>
        <n-button type="primary" @click="handleUpdate">저장</n-button>
      </template>
    </n-modal>

    <ConfirmModal
      v-model:show="deleteModal"
      title="장비 종류 삭제"
      message="이 장비 종류를 삭제하시겠습니까? 자산에서 사용 중이면 삭제되지 않습니다."
      danger
      @confirm="confirmDelete"
    />
  </PageShell>
</template>

<script setup>
import { ref, onMounted, h } from 'vue'
import { NButton, NSpace, useMessage } from 'naive-ui'
import PageShell    from '@/components/common/PageShell.vue'
import DataTable    from '@/components/common/DataTable.vue'
import ConfirmModal from '@/components/common/ConfirmModal.vue'
import client from '@/api/client'

const message = useMessage()
const list    = ref([])
const loading = ref(false)
const saving  = ref(false)
const editModal    = ref(false)
const deleteModal  = ref(false)
const deleteTarget = ref(null)
const form     = ref({ name: '', code: '', description: '' })
const editForm = ref({})

const columns = [
  { title: '장비명', key: 'name',        width: 150 },
  { title: '코드',   key: 'code',        width: 100 },
  { title: '설명',   key: 'description', width: 250 },
  {
    title: '관리', key: 'actions', width: 130,
    render: row => h(NSpace, null, { default: () => [
      h(NButton, { size: 'small', onClick: () => { editForm.value = { ...row }; editModal.value = true } }, { default: () => '수정' }),
      h(NButton, { size: 'small', type: 'error', onClick: () => { deleteTarget.value = row.id; deleteModal.value = true } }, { default: () => '삭제' }),
    ]}),
  },
]

async function fetchList() {
  loading.value = true
  try { list.value = await client.get('/api/catalogs/equipment-types').then(r => r.data) }
  finally { loading.value = false }
}

async function handleAdd() {
  if (!form.value.name.trim() || !form.value.code.trim()) {
    message.warning('장비명과 코드를 입력하세요'); return
  }
  saving.value = true
  try {
    const item = await client.post('/api/catalogs/equipment-types', form.value).then(r => r.data)
    list.value.push(item)
    form.value = { name: '', code: '', description: '' }
    message.success('추가되었습니다')
  } catch (e) { message.error(e.message) }
  finally { saving.value = false }
}

async function handleUpdate() {
  try {
    const { id, name, description } = editForm.value
    const item = await client.patch(`/api/catalogs/equipment-types/${id}`, { name, description }).then(r => r.data)
    const idx = list.value.findIndex(t => t.id === id)
    if (idx !== -1) list.value[idx] = item
    editModal.value = false
    message.success('수정되었습니다')
  } catch (e) { message.error(e.message) }
}

async function confirmDelete() {
  try {
    await client.delete(`/api/catalogs/equipment-types/${deleteTarget.value}`)
    list.value = list.value.filter(t => t.id !== deleteTarget.value)
    message.success('삭제되었습니다')
  } catch (e) { message.error(e.message) }
  deleteModal.value = false
}

onMounted(fetchList)
</script>
