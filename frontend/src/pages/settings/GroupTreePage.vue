<template>
  <PageShell title="그룹 관리">
    <n-card>
      <TreeEditor
        title="그룹"
        :nodes="store.list"
        :on-add="handleAdd"
        :on-update="handleUpdate"
        :on-delete="store.remove"
        :new-child-row="() => ({ code: '' })"
        :get-label="formatGroupLabel"
        :render-label="renderGroupLabel"
      >
        <!-- 상단 추가 폼: 코드 입력 -->
        <template #extra-fields="{ form }">
          <n-input v-model:value="form.code" placeholder="그룹 코드 (선택)" style="width:140px" />
        </template>
        <!-- 수정 모달: 코드 입력 -->
        <template #edit-extra="{ form }">
          <n-form-item label="그룹 코드">
            <n-input v-model:value="form.code" placeholder="코드 (자산 채번에 사용)" />
          </n-form-item>
        </template>
        <!-- 하위추가 모달: 행마다 코드 입력 -->
        <template #add-child-extra="{ row }">
          <n-input v-model:value="row.code" placeholder="그룹 코드" style="width:130px" />
        </template>
      </TreeEditor>
    </n-card>
  </PageShell>
</template>

<script setup>
import { onMounted, h } from 'vue'
import PageShell  from '@/components/common/PageShell.vue'
import TreeEditor from '@/components/common/TreeEditor.vue'
import { useGroupStore } from '@/stores/groupStore'

const store = useGroupStore()

async function handleAdd(body)         { await store.create(body) }
async function handleUpdate(id, body)  { await store.update(id, body) }

function formatGroupLabel(node) {
  return node.code ? `${node.name} (${node.code})` : node.name
}

function renderGroupLabel({ option }) {
  return option._raw.code
    ? h('span', [
        option._raw.name,
        ' ',
        h('span', { style: 'color:#18a058;font-weight:700;font-size:0.85em' }, `(${option._raw.code})`),
      ])
    : option._raw.name
}

onMounted(() => store.fetchList())
</script>
