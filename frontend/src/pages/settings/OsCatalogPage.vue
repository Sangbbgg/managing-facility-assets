<template>
  <PageShell title="OS 카탈로그">
    <n-card style="margin-bottom:16px">
      <n-form inline label-placement="left">
        <n-form-item label="OS명">
          <n-input v-model:value="form.name" placeholder="OS 이름" style="width:200px" />
        </n-form-item>
        <n-form-item label="버전">
          <n-input v-model:value="form.version" placeholder="버전" style="width:120px" />
        </n-form-item>
        <n-form-item label="EOL">
          <n-date-picker v-model:formatted-value="form.eol_date" type="date" clearable value-format="yyyy-MM-dd" style="width:150px" />
        </n-form-item>
        <n-button type="primary" :loading="saving" @click="handleAdd">추가</n-button>
      </n-form>
    </n-card>

    <n-card>
      <DataTable title="OS 목록" :columns="columns" :data="store.osList" :loading="store.loading" />
    </n-card>

    <n-modal v-model:show="editModal" preset="dialog" title="OS 수정">
      <n-form label-placement="left" label-width="80px">
        <n-form-item label="OS명"><n-input v-model:value="editForm.name" /></n-form-item>
        <n-form-item label="버전"><n-input v-model:value="editForm.version" /></n-form-item>
        <n-form-item label="EOL">
          <n-date-picker v-model:formatted-value="editForm.eol_date" type="date" clearable value-format="yyyy-MM-dd" />
        </n-form-item>
      </n-form>
      <template #action>
        <n-button @click="editModal=false">취소</n-button>
        <n-button type="primary" @click="handleUpdate">저장</n-button>
      </template>
    </n-modal>

    <ConfirmModal v-model:show="deleteModal" title="OS 삭제" message="이 OS를 삭제하시겠습니까?" danger @confirm="confirmDelete" />
  </PageShell>
</template>

<script setup>
import { ref, onMounted, h } from 'vue'
import { NButton, NSpace, useMessage } from 'naive-ui'
import PageShell    from '@/components/common/PageShell.vue'
import DataTable    from '@/components/common/DataTable.vue'
import ConfirmModal from '@/components/common/ConfirmModal.vue'
import { useCatalogStore } from '@/stores/catalogStore'

const store   = useCatalogStore()
const message = useMessage()
const saving  = ref(false)
const editModal   = ref(false)
const deleteModal = ref(false)
const deleteTarget = ref(null)

const form     = ref({ name: '', version: '', eol_date: null })
const editForm = ref({})

const columns = [
  { title: 'OS명',  key: 'name',    width: 200 },
  { title: '버전',  key: 'version', width: 120 },
  { title: 'EOL',   key: 'eol_date',width: 120 },
  { title: '관리', key: 'actions', width: 120,
    render: row => h(NSpace, null, { default: () => [
      h(NButton, { size: 'small', onClick: () => { editForm.value = { ...row }; editModal.value = true } }, { default: () => '수정' }),
      h(NButton, { size: 'small', type: 'error', onClick: () => { deleteTarget.value = row.id; deleteModal.value = true } }, { default: () => '삭제' }),
    ]})
  },
]

async function handleAdd() {
  if (!form.value.name.trim()) { message.warning('OS명을 입력하세요'); return }
  saving.value = true
  try { await store.createOs(form.value); form.value = { name: '', version: '', eol_date: null }; message.success('추가되었습니다') }
  catch (e) { message.error(e.message) }
  finally { saving.value = false }
}

async function handleUpdate() {
  try { await store.updateOs(editForm.value.id, editForm.value); editModal.value = false; message.success('수정되었습니다') }
  catch (e) { message.error(e.message) }
}

async function confirmDelete() {
  try { await store.removeOs(deleteTarget.value); message.success('삭제되었습니다') }
  catch (e) { message.error(e.message) }
  deleteModal.value = false
}

onMounted(() => store.fetchOs())
</script>
