<template>
  <PageShell title="&#xB2F4;&#xB2F9;&#xC790; &#xAD00;&#xB9AC;">
    <n-card style="margin-bottom: 16px">
      <n-form label-placement="left" label-width="90px">
        <n-grid :cols="2" :x-gap="12">
          <n-gi>
            <n-form-item label="&#xC774;&#xB984;">
              <n-input v-model:value="form.name" placeholder="&#xB2F4;&#xB2F9;&#xC790; &#xC774;&#xB984;" />
            </n-form-item>
          </n-gi>
          <n-gi>
            <n-form-item label="&#xC9C1;&#xAE09;">
              <n-input v-model:value="form.title" placeholder="&#xC9C1;&#xAE09;" />
            </n-form-item>
          </n-gi>
          <n-gi>
            <n-form-item label="&#xBD80;&#xC11C;">
              <n-select
                v-model:value="form.dept_id"
                :options="departmentOptions"
                clearable
                placeholder="&#xBD80;&#xC11C;&#xB97C; &#xC120;&#xD0DD;&#xD558;&#xC138;&#xC694;"
              />
            </n-form-item>
          </n-gi>
          <n-gi :span="2">
            <n-form-item label="&#xC5F0;&#xB77D;&#xCC98;">
              <n-input v-model:value="form.contact" placeholder="&#xC804;&#xD654; / &#xC774;&#xBA54;&#xC77C;" />
            </n-form-item>
          </n-gi>
        </n-grid>

        <n-form-item label="&#xB2F4;&#xB2F9; &#xADF8;&#xB8F9;">
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

        <n-button type="primary" :loading="saving" @click="handleAdd">&#xCD94;&#xAC00;</n-button>
      </n-form>
    </n-card>

    <n-card>
      <DataTable title="&#xB2F4;&#xB2F9;&#xC790; &#xBAA9;&#xB85D;" :columns="columns" :data="store.personList" :loading="store.loading" />
    </n-card>

    <n-modal
      v-model:show="editModal"
      preset="dialog"
      title="&#xB2F4;&#xB2F9;&#xC790; &#xC218;&#xC815;"
      style="width: min(980px, calc(100vw - 48px))"
    >
      <n-form label-placement="left" label-width="90px">
        <n-grid :cols="2" :x-gap="12">
          <n-gi>
            <n-form-item label="&#xC774;&#xB984;">
              <n-input v-model:value="editForm.name" />
            </n-form-item>
          </n-gi>
          <n-gi>
            <n-form-item label="&#xC9C1;&#xAE09;">
              <n-input v-model:value="editForm.title" />
            </n-form-item>
          </n-gi>
          <n-gi>
            <n-form-item label="&#xBD80;&#xC11C;">
              <n-select
                v-model:value="editForm.dept_id"
                :options="departmentOptions"
                clearable
                placeholder="&#xBD80;&#xC11C;&#xB97C; &#xC120;&#xD0DD;&#xD558;&#xC138;&#xC694;"
              />
            </n-form-item>
          </n-gi>
          <n-gi :span="2">
            <n-form-item label="&#xC5F0;&#xB77D;&#xCC98;">
              <n-input v-model:value="editForm.contact" />
            </n-form-item>
          </n-gi>
        </n-grid>

        <n-form-item label="&#xB2F4;&#xB2F9; &#xADF8;&#xB8F9;">
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
        <n-button @click="editModal = false">&#xCDE8;&#xC18C;</n-button>
        <n-button type="primary" :loading="saving" @click="handleUpdate">&#xC800;&#xC7A5;</n-button>
      </template>
    </n-modal>

    <ConfirmModal
      v-model:show="deleteModal"
      title="&#xB2F4;&#xB2F9;&#xC790; &#xC0AD;&#xC81C;"
      message="&#xC120;&#xD0DD;&#xD55C; &#xB2F4;&#xB2F9;&#xC790;&#xB97C; &#xC0AD;&#xC81C;&#xD558;&#xC2DC;&#xACA0;&#xC2B5;&#xB2C8;&#xAE4C;?"
      danger
      @confirm="confirmDelete"
    />
  </PageShell>
</template>

<script setup>
import { computed, h, onMounted, ref } from 'vue'
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
  dept_id: null,
  group_ids: [],
})

const form = ref(emptyForm())
const editForm = ref(emptyForm())

const departmentOptions = computed(() =>
  (store.deptList || []).map((dept) => ({
    label: dept.name,
    value: dept.id,
  }))
)

const columns = [
  { title: '\uC774\uB984', key: 'name', width: 140, sorter: 'default' },
  { title: '\uBD80\uC11C', key: 'department_name', width: 140, render: (row) => row.department_name || '-' },
  { title: '\uC9C1\uAE09', key: 'title', width: 120, sorter: 'default' },
  { title: '\uC5F0\uB77D\uCC98', key: 'contact', width: 220 },
  {
    title: '\uB2F4\uB2F9 \uADF8\uB8F9',
    key: 'group_roles_text',
    minWidth: 420,
    render: (row) => renderRoleSummary(row.group_roles),
  },
  {
    title: '\uAD00\uB9AC',
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
            { default: () => '\uC218\uC815' }
          ),
          h(
            NButton,
            {
              size: 'small',
              type: 'error',
              ghost: true,
              onClick: () => openDelete(row.id),
            },
            { default: () => '\uC0AD\uC81C' }
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
    dept_id: row.dept_id ?? null,
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
    message.warning('\uC774\uB984\uC744 \uC785\uB825\uD574 \uC8FC\uC138\uC694.')
    return
  }

  saving.value = true
  try {
    await store.createPerson({
      name: form.value.name.trim(),
      title: form.value.title?.trim() || '',
      contact: form.value.contact?.trim() || '',
      dept_id: form.value.dept_id,
      group_roles: buildGroupRoles(form.value.group_ids),
    })
    form.value = emptyForm()
    message.success('\uB2F4\uB2F9\uC790\uB97C \uCD94\uAC00\uD588\uC2B5\uB2C8\uB2E4.')
  } catch (error) {
    message.error(error.message)
  } finally {
    saving.value = false
  }
}

async function handleUpdate() {
  if (!editForm.value.name.trim()) {
    message.warning('\uC774\uB984\uC744 \uC785\uB825\uD574 \uC8FC\uC138\uC694.')
    return
  }

  saving.value = true
  try {
    await store.updatePerson(editForm.value.id, {
      name: editForm.value.name.trim(),
      title: editForm.value.title?.trim() || '',
      contact: editForm.value.contact?.trim() || '',
      dept_id: editForm.value.dept_id,
      group_roles: buildGroupRoles(editForm.value.group_ids),
    })
    editModal.value = false
    message.success('\uB2F4\uB2F9\uC790\uB97C \uC218\uC815\uD588\uC2B5\uB2C8\uB2E4.')
  } catch (error) {
    message.error(error.message)
  } finally {
    saving.value = false
  }
}

async function confirmDelete() {
  try {
    await store.removePerson(deleteTarget.value)
    message.success('\uB2F4\uB2F9\uC790\uB97C \uC0AD\uC81C\uD588\uC2B5\uB2C8\uB2E4.')
  } catch (error) {
    message.error(error.message)
  } finally {
    deleteModal.value = false
    deleteTarget.value = null
  }
}

onMounted(async () => {
  await Promise.all([store.fetchPersons(), store.fetchDepts(), groupStore.fetchCodeable()])
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
