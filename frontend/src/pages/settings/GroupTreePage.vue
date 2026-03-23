<template>
  <PageShell title="그룹 관리">
    <n-card>
      <TreeEditor
        title="그룹"
        :nodes="store.list"
        :on-add="handleAdd"
        :on-update="handleUpdate"
        :on-delete="store.remove"
      >
        <!-- 추가 시 코드 입력 -->
        <template #extra-fields="{ form }">
          <n-input v-model:value="form.code" placeholder="그룹 코드 (선택)" style="width:140px" />
        </template>
        <!-- 수정 모달 내 코드 입력 -->
        <template #edit-extra="{ form }">
          <n-form-item label="그룹 코드">
            <n-input v-model:value="form.code" placeholder="코드 (자산 채번에 사용)" />
          </n-form-item>
        </template>
      </TreeEditor>
    </n-card>
  </PageShell>
</template>

<script setup>
import { onMounted } from 'vue'
import PageShell  from '@/components/common/PageShell.vue'
import TreeEditor from '@/components/common/TreeEditor.vue'
import { useGroupStore } from '@/stores/groupStore'

const store = useGroupStore()

async function handleAdd(body)         { await store.create(body) }
async function handleUpdate(id, body)  { await store.update(id, body) }

onMounted(() => store.fetchList())
</script>
