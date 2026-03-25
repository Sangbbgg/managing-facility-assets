<template>
  <div>
    <div style="display:flex;gap:8px;margin-bottom:12px">
      <n-input v-model:value="newName" :placeholder="`새 ${title} 이름`" style="width:200px" />
      <n-select
        v-model:value="newParentId"
        :options="parentOptions"
        placeholder="상위 노드 (없으면 루트)"
        clearable
        :consistent-menu-width="false"
        style="min-width:200px;max-width:400px"
      />
      <slot name="extra-fields" :form="extraForm" />
      <n-button type="primary" @click="handleAdd">추가</n-button>
    </div>

    <n-tree
      :data="treeData"
      :node-props="nodeProps"
      :render-suffix="renderSuffix"
      :render-label="renderLabel ?? undefined"
      :default-expanded-keys="allKeys"
      block-line
      expand-on-click
    />

    <!-- 수정 모달 -->
    <n-modal v-model:show="editModal" preset="dialog" title="수정">
      <n-form>
        <n-form-item label="이름">
          <n-input v-model:value="editForm.name" />
        </n-form-item>
        <n-form-item label="상위 노드">
          <n-select
            v-model:value="editForm.parent_id"
            :options="parentOptions.filter(o => o.value !== editForm.id)"
            placeholder="없으면 루트"
            clearable
            :consistent-menu-width="false"
          />
        </n-form-item>
        <slot name="edit-extra" :form="editForm" />
      </n-form>
      <template #action>
        <n-button @click="editModal = false">취소</n-button>
        <n-button type="primary" @click="handleUpdate">저장</n-button>
      </template>
    </n-modal>

    <!-- 하위 노드 일괄 추가 모달 -->
    <n-modal v-model:show="addChildModal" preset="card" title="하위 노드 추가" style="width:520px">
      <n-form>
        <n-form-item label="상위 노드">
          <n-input :value="addChildParentLabel" disabled />
        </n-form-item>
        <n-form-item label="추가할 목록">
          <div style="display:flex;flex-direction:column;gap:6px;width:100%">
            <div
              v-for="(row, idx) in addChildList"
              :key="idx"
              style="display:flex;gap:6px;align-items:center"
            >
              <n-input
                v-model:value="row.name"
                placeholder="이름 입력"
                style="flex:1"
                :ref="el => setInputRef(el, idx)"
                @keyup.enter="onRowEnter(idx)"
              />
              <slot name="add-child-extra" :row="row" />
              <n-button
                size="small"
                quaternary
                type="error"
                :disabled="addChildList.length === 1"
                @click="removeRow(idx)"
              >✕</n-button>
            </div>
            <n-button dashed size="small" @click="addRow" style="margin-top:2px">
              + 행 추가
            </n-button>
          </div>
        </n-form-item>
      </n-form>
      <template #footer>
        <div style="display:flex;justify-content:flex-end;gap:8px">
          <n-button @click="addChildModal = false">취소</n-button>
          <n-button type="primary" :loading="addChildLoading" @click="handleAddChildren">
            일괄 추가 ({{ addChildList.filter(r => r.name.trim()).length }}개)
          </n-button>
        </div>
      </template>
    </n-modal>

    <!-- 삭제 확인 -->
    <ConfirmModal
      v-model:show="deleteModal"
      title="삭제 확인"
      message="이 노드를 삭제하시겠습니까? 하위 노드가 있으면 삭제되지 않습니다."
      danger
      @confirm="handleDelete"
    />
  </div>
</template>

<script setup>
import { ref, computed, h, nextTick } from 'vue'
import { NButton, NSpace, useMessage } from 'naive-ui'
import ConfirmModal from './ConfirmModal.vue'

const props = defineProps({
  title:         { type: String,   required: true },
  nodes:         { type: Array,    default: () => [] },
  onAdd:         { type: Function, required: true },
  onUpdate:      { type: Function, required: true },
  onDelete:      { type: Function, required: true },
  newChildRow:   { type: Function, default: () => () => ({}) },
  getLabel:      { type: Function, default: null }, // 노드 → 표시 라벨 (string)
  renderLabel:   { type: Function, default: null }, // 노드 → 표시 라벨 (VNode, 우선순위 높음)
})

const message = useMessage()
const newName     = ref('')
const newParentId = ref(null)
const extraForm   = ref({})
const editModal   = ref(false)
const deleteModal = ref(false)
const editForm    = ref({ id: null, name: '', parent_id: null })
const targetId    = ref(null)

const addChildModal       = ref(false)
const addChildList        = ref([{ name: '' }])
const addChildParentId    = ref(null)
const addChildParentLabel = ref('')
const addChildLoading     = ref(false)
const inputRefs           = ref([])

function setInputRef(el, idx) {
  if (el) inputRefs.value[idx] = el
}

function addRow() {
  addChildList.value.push({ name: '', ...props.newChildRow() })
  nextTick(() => {
    const last = inputRefs.value[addChildList.value.length - 1]
    if (last?.focus) last.focus()
  })
}

function removeRow(idx) {
  if (addChildList.value.length === 1) return
  addChildList.value.splice(idx, 1)
}

function onRowEnter(idx) {
  if (idx === addChildList.value.length - 1) {
    addRow()
  } else {
    const next = inputRefs.value[idx + 1]
    if (next?.focus) next.focus()
  }
}

const parentOptions = computed(() =>
  props.nodes.map(n => ({ label: n.full_path || n.name, value: n.id }))
)

function buildTree(nodes, parentId = null) {
  return nodes
    .filter(n => (n.parent_id ?? null) === parentId)
    .map(n => ({
      key: n.id,
      label: n.name,
      _raw: n,
      children: buildTree(nodes, n.id),
    }))
}
const treeData = computed(() => buildTree(props.nodes))
const allKeys  = computed(() => props.nodes.map(n => n.id))

function nodeProps({ option }) {
  return { onContextmenu(e) { e.preventDefault() } }
}

function renderSuffix({ option }) {
  return h(NSpace, { size: 4, style: 'margin-right:4px' }, {
    default: () => [
      h(NButton, {
        size: 'tiny', secondary: true, type: 'primary',
        onClick(e) {
          e.stopPropagation()
          addChildList.value = [{ name: '', ...props.newChildRow() }]
          addChildParentId.value = option._raw.id
          addChildParentLabel.value = option._raw.full_path || option._raw.name
          addChildModal.value = true
          nextTick(() => { if (inputRefs.value[0]?.focus) inputRefs.value[0].focus() })
        },
      }, { default: () => '+ 하위추가' }),
      h(NButton, {
        size: 'tiny', secondary: true,
        onClick(e) {
          e.stopPropagation()
          editForm.value = { ...option._raw }
          editModal.value = true
        },
      }, { default: () => '수정' }),
      h(NButton, {
        size: 'tiny', secondary: true, type: 'error',
        onClick(e) {
          e.stopPropagation()
          targetId.value = option._raw.id
          deleteModal.value = true
        },
      }, { default: () => '삭제' }),
    ],
  })
}

async function handleAdd() {
  if (!newName.value.trim()) { message.warning('이름을 입력하세요'); return }
  try {
    await props.onAdd({ name: newName.value.trim(), parent_id: newParentId.value, ...extraForm.value })
    newName.value = ''
    newParentId.value = null
    extraForm.value = {}
    message.success('추가되었습니다')
  } catch (e) { message.error(e.message) }
}

async function handleUpdate() {
  try {
    await props.onUpdate(editForm.value.id, editForm.value)
    editModal.value = false
    message.success('수정되었습니다')
  } catch (e) { message.error(e.message) }
}

async function handleAddChildren() {
  const rows = addChildList.value.filter(r => r.name.trim())
  if (rows.length === 0) { message.warning('이름을 하나 이상 입력하세요'); return }
  addChildLoading.value = true
  let success = 0
  const errors = []
  for (const row of rows) {
    try {
      await props.onAdd({ ...row, name: row.name.trim(), parent_id: addChildParentId.value })
      success++
    } catch (e) {
      errors.push(row.name)
    }
  }
  addChildLoading.value = false
  if (errors.length === 0) {
    message.success(`${success}개 추가되었습니다`)
    addChildModal.value = false
  } else {
    message.warning(`${success}개 추가, ${errors.length}개 실패: ${errors.join(', ')}`)
  }
}

async function handleDelete() {
  try {
    await props.onDelete(targetId.value)
    deleteModal.value = false
    message.success('삭제되었습니다')
  } catch (e) { message.error(e.message) }
}

defineExpose({ openDelete: (id) => { targetId.value = id; deleteModal.value = true } })
</script>
