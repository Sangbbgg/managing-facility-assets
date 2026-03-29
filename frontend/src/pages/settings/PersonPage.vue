<template>
  <PageShell title="담당자 관리">
    <n-card style="margin-bottom: 16px">
      <n-form label-placement="left" label-width="90px">
        <n-grid :cols="2" :x-gap="12">
          <n-gi>
            <n-form-item label="이름">
              <n-input v-model:value="form.name" placeholder="담당자 이름" />
            </n-form-item>
          </n-gi>
          <n-gi>
            <n-form-item label="직급">
              <n-input v-model:value="form.title" placeholder="직급" />
            </n-form-item>
          </n-gi>
          <n-gi :span="2">
            <n-form-item label="연락처">
              <n-input v-model:value="form.contact" placeholder="전화 / 이메일" />
            </n-form-item>
          </n-gi>
        </n-grid>

        <n-form-item label="담당 그룹">
          <div class="group-box">
            <n-checkbox-group v-model:value="form.group_ids">
              <n-space vertical size="small">
                <n-checkbox
                  v-for="group in groupStore.codeable"
                  :key="`create-group-${group.id}`"
                  :value="group.id"
                  :label="formatGroupOptionLabel(group)"
                />
              </n-space>
            </n-checkbox-group>
          </div>
        </n-form-item>

        <n-button type="primary" :loading="saving" @click="handleAdd">추가</n-button>
      </n-form>
    </n-card>

    <n-card>
      <DataTable title="담당자 목록" :columns="columns" :data="store.personList" :loading="store.loading" />
    </n-card>

    <n-modal
      v-model:show="editModal"
      preset="dialog"
      title="담당자 수정"
      style="width: min(980px, calc(100vw - 48px))"
    >
      <n-form label-placement="left" label-width="90px">
        <n-grid :cols="2" :x-gap="12">
          <n-gi>
            <n-form-item label="이름">
              <n-input v-model:value="editForm.name" />
            </n-form-item>
          </n-gi>
          <n-gi>
            <n-form-item label="직급">
              <n-input v-model:value="editForm.title" />
            </n-form-item>
          </n-gi>
          <n-gi :span="2">
            <n-form-item label="연락처">
              <n-input v-model:value="editForm.contact" />
            </n-form-item>
          </n-gi>
        </n-grid>

        <n-form-item label="담당 그룹">
          <div class="group-box">
            <n-checkbox-group v-model:value="editForm.group_ids">
              <n-space vertical size="small">
                <n-checkbox
                  v-for="group in groupStore.codeable"
                  :key="`edit-group-${group.id}`"
                  :value="group.id"
                  :label="formatGroupOptionLabel(group)"
                />
              </n-space>
            </n-checkbox-group>
          </div>
        </n-form-item>
      </n-form>

      <template #action>
        <n-button @click="editModal = false">취소</n-button>
        <n-button type="primary" :loading="saving" @click="handleUpdate">저장</n-button>
      </template>
    </n-modal>

    <ConfirmModal
      v-model:show="deleteModal"
      title="담당자 삭제"
      message="선택한 담당자를 삭제하시겠습니까?"
      danger
      @confirm="confirmDelete"
    />
  </PageShell>
</template>

<script setup>
import { h, onMounted, ref } from 'vue'
import { NButton, NSpace, useMessage } from 'naive-ui'

import ConfirmModal from '@/components/common/ConfirmModal.vue'
import DataTable from '@/components/common/DataTable.vue'
import PageShell from '@/components/common/PageShell.vue'
import { useGroupStore } from '@/stores/groupStore'
import { usePersonStore } from '@/stores/personStore'

const store = usePersonStore()
const groupStore = useGroupStore()
const message = useMessage()

const saving = ref(false)
const editModal = ref(false)
const deleteModal = ref(false)
const deleteTarget = ref(null)

const emptyForm = () => ({
  id: null,
  name: '',
  title: '',
  contact: '',
  group_ids: [],
})

const form = ref(emptyForm())
const editForm = ref(emptyForm())

const columns = [
  { title: '이름', key: 'name', width: 140, sorter: 'default' },
  { title: '직급', key: 'title', width: 120, sorter: 'default' },
  { title: '연락처', key: 'contact', width: 220 },
  {
    title: '담당 그룹',
    key: 'group_roles_text',
    minWidth: 420,
    render: (row) => renderRoleSummary(row.group_roles),
  },
  {
    title: '관리',
    key: 'actions',
    width: 140,
    render: (row) =>
      h(NSpace, { size: 8 }, {
        default: () => [
          h(
            NButton,
            {
              size: 'small',
              onClick: () => openEdit(row),
            },
            { default: () => '수정' }
          ),
          h(
            NButton,
            {
              size: 'small',
              type: 'error',
              ghost: true,
              onClick: () => openDelete(row.id),
            },
            { default: () => '삭제' }
          ),
        ],
      }),
  },
]

function renderRoleSummary(groupRoles = []) {
  const roles = Array.isArray(groupRoles) ? groupRoles : []
  if (!roles.length) return '-'

  return h(
    'div',
    { class: 'role-summary' },
    roles.map((role) =>
      h('div', { class: 'role-summary__item' }, [
        h('span', { class: 'role-summary__path' }, role.group_full_path || role.group_name || String(role.group_id)),
      ])
    )
  )
}

function formatGroupOptionLabel(group) {
  const path = group.full_path || group.name
  const code = group.display_code || group.code
  return code ? `${path} [${code}]` : path
}

function toEditableForm(row) {
  return {
    id: row.id,
    name: row.name || '',
    title: row.title || '',
    contact: row.contact || '',
    group_ids: (row.group_roles || []).map((role) => role.group_id),
  }
}

function buildGroupRoles(groupIds = []) {
  return groupIds.map((groupId) => ({
    group_id: groupId,
    role_type: 'PRIMARY',
  }))
}

function openEdit(row) {
  editForm.value = toEditableForm(row)
  editModal.value = true
}

function openDelete(id) {
  deleteTarget.value = id
  deleteModal.value = true
}

async function handleAdd() {
  if (!form.value.name.trim()) {
    message.warning('이름을 입력해 주세요.')
    return
  }

  saving.value = true
  try {
    await store.createPerson({
      name: form.value.name.trim(),
      title: form.value.title?.trim() || '',
      contact: form.value.contact?.trim() || '',
      group_roles: buildGroupRoles(form.value.group_ids),
    })
    form.value = emptyForm()
    message.success('담당자를 추가했습니다.')
  } catch (error) {
    message.error(error.message)
  } finally {
    saving.value = false
  }
}

async function handleUpdate() {
  if (!editForm.value.name.trim()) {
    message.warning('이름을 입력해 주세요.')
    return
  }

  saving.value = true
  try {
    await store.updatePerson(editForm.value.id, {
      name: editForm.value.name.trim(),
      title: editForm.value.title?.trim() || '',
      contact: editForm.value.contact?.trim() || '',
      group_roles: buildGroupRoles(editForm.value.group_ids),
    })
    editModal.value = false
    message.success('담당자를 수정했습니다.')
  } catch (error) {
    message.error(error.message)
  } finally {
    saving.value = false
  }
}

async function confirmDelete() {
  try {
    await store.removePerson(deleteTarget.value)
    message.success('담당자를 삭제했습니다.')
  } catch (error) {
    message.error(error.message)
  } finally {
    deleteModal.value = false
    deleteTarget.value = null
  }
}

onMounted(async () => {
  await Promise.all([store.fetchPersons(), groupStore.fetchCodeable()])
})
</script>

<style scoped>
.group-box {
  width: 100%;
  max-height: 320px;
  overflow-y: auto;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 10px 12px;
}

.role-summary {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 6px 0;
}

.role-summary__item {
  display: flex;
  align-items: center;
  min-width: 0;
}

.role-summary__path {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
