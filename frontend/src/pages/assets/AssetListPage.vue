<template>
  <PageShell title="자산 목록">
    <template #actions>
      <n-button type="primary" @click="$router.push('/assets/new')">
        <template #icon><n-icon><AddOutline /></n-icon></template>
        자산 등록
      </n-button>
    </template>

    <!-- 필터 바 -->
    <n-card style="margin-bottom:16px">
      <n-space wrap>
        <n-input
          v-model:value="filters.keyword"
          placeholder="자산명 / 자산코드 검색"
          clearable
          style="width:220px"
          @keydown.enter="loadList"
        />
        <n-select
          v-model:value="filters.group_id"
          :options="groupOptions"
          placeholder="그룹 선택"
          clearable
          style="width:180px"
        />
        <n-select
          v-model:value="filters.is_deleted"
          :options="[{label:'운용중', value: false},{label:'폐기', value: true}]"
          placeholder="상태"
          clearable
          style="width:120px"
        />
        <n-button @click="loadList">검색</n-button>
        <n-button @click="resetFilters">초기화</n-button>
      </n-space>
    </n-card>

    <n-card>
      <DataTable
        :columns="columns"
        :data="store.list"
        :loading="store.loading"
        :pagination="{ pageSize: 20 }"
      />
    </n-card>

    <ConfirmModal
      v-model:show="deleteModal"
      title="자산 삭제"
      message="선택한 자산을 논리 삭제하시겠습니까?"
      danger
      @confirm="confirmDelete"
    />
  </PageShell>
</template>

<script setup>
import { ref, computed, onMounted, h } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NSpace, NTag, useMessage } from 'naive-ui'
import { AddOutline, CreateOutline, TrashOutline } from '@vicons/ionicons5'
import PageShell   from '@/components/common/PageShell.vue'
import DataTable   from '@/components/common/DataTable.vue'
import ConfirmModal from '@/components/common/ConfirmModal.vue'
import { useAssetStore } from '@/stores/assetStore'
import { useGroupStore }  from '@/stores/groupStore'

const router  = useRouter()
const message = useMessage()
const store   = useAssetStore()
const groupStore = useGroupStore()

const deleteModal = ref(false)
const deleteTarget = ref(null)
const filters = ref({ keyword: '', group_id: null, is_deleted: null })

const groupOptions = computed(() =>
  groupStore.list.map(g => ({ label: g.full_path || g.name, value: g.id }))
)

const columns = [
  { title: '자산코드',  key: 'asset_code', width: 160 },
  { title: '자산명',    key: 'asset_name', width: 180 },
  { title: '모델',      key: 'model_name', width: 150 },
  { title: '용도',      key: 'purpose',    width: 150 },
  { title: '상태',      key: 'is_deleted', width: 80,
    render: row => h(NTag, { type: row.is_deleted ? 'error' : 'success' },
      { default: () => row.is_deleted ? '폐기' : '운용' }) },
  { title: '관리',      key: 'actions',    width: 120,
    render: row => h(NSpace, null, {
      default: () => [
        h(NButton, { size: 'small', onClick: () => router.push(`/assets/${row.id}/edit`) }, { default: () => '수정' }),
        h(NButton, { size: 'small', type: 'error', onClick: () => openDelete(row.id) }, { default: () => '삭제' }),
      ]
    })
  },
]

function openDelete(id) { deleteTarget.value = id; deleteModal.value = true }

async function confirmDelete() {
  try {
    await store.remove(deleteTarget.value)
    message.success('삭제되었습니다')
  } catch (e) { message.error(e.message) }
  deleteModal.value = false
}

function resetFilters() { filters.value = { keyword: '', group_id: null, is_deleted: null }; loadList() }

async function loadList() {
  const p = {}
  if (filters.value.keyword)  p.keyword  = filters.value.keyword
  if (filters.value.group_id) p.group_id = filters.value.group_id
  if (filters.value.is_deleted !== null) p.is_deleted = filters.value.is_deleted
  await store.fetchList(p)
}

onMounted(async () => {
  await groupStore.fetchList()
  await loadList()
})
</script>
