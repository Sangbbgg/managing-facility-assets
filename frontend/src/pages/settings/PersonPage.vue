<template>
  <PageShell title="담당자 관리">
    <n-card style="margin-bottom:16px">
      <n-form inline label-placement="left">
        <n-form-item label="이름">
          <n-input v-model:value="form.name" placeholder="담당자 이름" style="width:140px" />
        </n-form-item>
        <n-form-item label="직책">
          <n-input v-model:value="form.title" placeholder="직책" style="width:120px" />
        </n-form-item>
        <n-form-item label="부서">
          <n-select v-model:value="form.dept_id" :options="deptOptions" placeholder="부서" clearable style="width:160px" />
        </n-form-item>
        <n-form-item label="연락처">
          <n-input v-model:value="form.contact" placeholder="전화/이메일" style="width:180px" />
        </n-form-item>
        <n-button type="primary" :loading="saving" @click="handleAdd">추가</n-button>
      </n-form>
    </n-card>

    <n-card>
      <DataTable :columns="columns" :data="store.personList" :loading="store.loading" />
    </n-card>

    <n-modal v-model:show="editModal" preset="dialog" title="담당자 수정">
      <n-form label-placement="left" label-width="80px">
        <n-form-item label="이름"><n-input v-model:value="editForm.name" /></n-form-item>
        <n-form-item label="직책"><n-input v-model:value="editForm.title" /></n-form-item>
        <n-form-item label="부서">
          <n-select v-model:value="editForm.dept_id" :options="deptOptions" clearable />
        </n-form-item>
        <n-form-item label="연락처"><n-input v-model:value="editForm.contact" /></n-form-item>
      </n-form>
      <template #action>
        <n-button @click="editModal=false">취소</n-button>
        <n-button type="primary" @click="handleUpdate">저장</n-button>
      </template>
    </n-modal>

    <ConfirmModal v-model:show="deleteModal" title="담당자 삭제" message="담당자를 삭제하시겠습니까?" danger @confirm="confirmDelete" />
  </PageShell>
</template>

<script setup>
import { ref, computed, onMounted, h } from 'vue'
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
const form     = ref({ name: '', title: '', dept_id: null, contact: '' })
const editForm = ref({})

const deptOptions = computed(() => store.deptList.map(d => ({ label: d.name, value: d.id })))

const columns = [
  { title: '이름',   key: 'name',    width: 120 },
  { title: '직책',   key: 'title',   width: 100 },
  { title: '연락처', key: 'contact', width: 180 },
  { title: '관리', key: 'actions', width: 120,
    render: row => h(NSpace, null, { default: () => [
      h(NButton, { size: 'small', onClick: () => { editForm.value = { ...row }; editModal.value = true } }, { default: () => '수정' }),
      h(NButton, { size: 'small', type: 'error', onClick: () => { deleteTarget.value = row.id; deleteModal.value = true } }, { default: () => '삭제' }),
    ]})
  },
]

async function handleAdd() {
  if (!form.value.name.trim()) { message.warning('이름을 입력하세요'); return }
  saving.value = true
  try { await store.createPerson(form.value); form.value = { name: '', title: '', dept_id: null, contact: '' }; message.success('추가되었습니다') }
  catch (e) { message.error(e.message) }
  finally { saving.value = false }
}

async function handleUpdate() {
  try { await store.updatePerson(editForm.value.id, editForm.value); editModal.value = false; message.success('수정되었습니다') }
  catch (e) { message.error(e.message) }
}

async function confirmDelete() {
  try { await store.removePerson(deleteTarget.value); message.success('삭제되었습니다') }
  catch (e) { message.error(e.message) }
  deleteModal.value = false
}

onMounted(async () => {
  await store.fetchDepts()
  await store.fetchPersons()
})
</script>
