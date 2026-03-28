<template>
  <PageShell title="부서 관리">
    <n-card style="margin-bottom:16px">
      <n-form inline label-placement="left">
        <n-form-item label="부서명">
          <n-input v-model:value="form.name" placeholder="부서명" style="width:180px" />
        </n-form-item>
        <n-form-item label="코드">
          <n-input v-model:value="form.code" placeholder="부서 코드 (선택)" style="width:140px" />
        </n-form-item>
        <n-button type="primary" :loading="saving" @click="handleAdd">추가</n-button>
      </n-form>
    </n-card>

    <n-card>
      <DataTable title="부서 목록" :columns="columns" :data="store.deptList" :loading="store.loading" />
    </n-card>

    <n-modal v-model:show="editModal" preset="dialog" title="부서 수정">
      <n-form label-placement="left" label-width="80px">
        <n-form-item label="부서명"><n-input v-model:value="editForm.name" /></n-form-item>
        <n-form-item label="코드"><n-input v-model:value="editForm.code" /></n-form-item>
      </n-form>
      <template #action>
        <n-button @click="editModal=false">취소</n-button>
        <n-button type="primary" @click="handleUpdate">저장</n-button>
      </template>
    </n-modal>

    <ConfirmModal v-model:show="deleteModal" title="부서 삭제" message="부서를 삭제하시겠습니까?" danger @confirm="confirmDelete" />
  </PageShell>
</template>

<script setup>
import { ref, onMounted, h } from 'vue'
import { NButton, NSpace, useMessage } from 'naive-ui'
import PageShell    from '@/components/common/PageShell.vue'
import DataTable    from '@/components/common/DataTable.vue'
import ConfirmModal from '@/components/common/ConfirmModal.vue'
import { usePersonStore } from '@/stores/personStore'

const store   = usePersonStore()
const message = useMessage()
const saving  = ref(false)
const editModal    = ref(false)
const deleteModal  = ref(false)
const deleteTarget = ref(null)
const form     = ref({ name: '', code: '' })
const editForm = ref({})

const columns = [
  { title: '부서명', key: 'name', width: 180 },
  { title: '코드',   key: 'code', width: 120 },
  { title: '관리', key: 'actions', width: 120,
    render: row => h(NSpace, null, { default: () => [
      h(NButton, { size: 'small', onClick: () => { editForm.value = { ...row }; editModal.value = true } }, { default: () => '수정' }),
      h(NButton, { size: 'small', type: 'error', onClick: () => { deleteTarget.value = row.id; deleteModal.value = true } }, { default: () => '삭제' }),
    ]})
  },
]

async function handleAdd() {
  if (!form.value.name.trim()) { message.warning('부서명을 입력하세요'); return }
  saving.value = true
  try { await store.createDept(form.value); form.value = { name: '', code: '' }; message.success('추가되었습니다') }
  catch (e) { message.error(e.message) }
  finally { saving.value = false }
}

async function handleUpdate() {
  try { await store.updateDept(editForm.value.id, editForm.value); editModal.value = false; message.success('수정되었습니다') }
  catch (e) { message.error(e.message) }
}

async function confirmDelete() {
  try { await store.removeDept(deleteTarget.value); message.success('삭제되었습니다') }
  catch (e) { message.error(e.message) }
  deleteModal.value = false
}

onMounted(() => store.fetchDepts())
</script>
