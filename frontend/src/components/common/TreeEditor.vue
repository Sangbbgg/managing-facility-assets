<template>
  <div>
    <div style="display:flex;gap:8px;margin-bottom:12px">
      <n-input v-model:value="newName" :placeholder="`새 ${title} 이름`" style="width:200px" />
      <n-select
        v-model:value="newParentId"
        :options="parentOptions"
        placeholder="상위 노드 (없으면 루트)"
        clearable
        style="width:200px"
      />
      <slot name="extra-fields" :form="extraForm" />
      <n-button type="primary" @click="handleAdd">추가</n-button>
    </div>

    <n-tree
      :data="treeData"
      :node-props="nodeProps"
      block-line
      expand-on-click
    />

    <!-- 수정 모달 -->
    <n-modal v-model:show="editModal" preset="dialog" title="수정">
      <n-form>
        <n-form-item label="이름">
          <n-input v-model:value="editForm.name" />
        </n-form-item>
        <slot name="edit-extra" :form="editForm" />
      </n-form>
      <template #action>
        <n-button @click="editModal = false">취소</n-button>
        <n-button type="primary" @click="handleUpdate">저장</n-button>
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
import { ref, computed } from 'vue'
import { useMessage } from 'naive-ui'
import ConfirmModal from './ConfirmModal.vue'

const props = defineProps({
  title:    { type: String, required: true },
  nodes:    { type: Array,  default: () => [] },
  onAdd:    { type: Function, required: true },
  onUpdate: { type: Function, required: true },
  onDelete: { type: Function, required: true },
})

const message = useMessage()
const newName     = ref('')
const newParentId = ref(null)
const extraForm   = ref({})
const editModal   = ref(false)
const deleteModal = ref(false)
const editForm    = ref({ id: null, name: '' })
const targetId    = ref(null)

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

function nodeProps({ option }) {
  return {
    onContextmenu(e) { e.preventDefault() },
    // 더블클릭으로 수정
    ondblclick() {
      editForm.value = { ...option._raw }
      editModal.value = true
    },
  }
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

async function handleDelete() {
  try {
    await props.onDelete(targetId.value)
    deleteModal.value = false
    message.success('삭제되었습니다')
  } catch (e) { message.error(e.message) }
}

defineExpose({ openDelete: (id) => { targetId.value = id; deleteModal.value = true } })
</script>
