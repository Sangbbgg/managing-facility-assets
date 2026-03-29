<template>
  <div>
    <n-spin :show="swStore.loading">
      <n-tabs type="line" size="small">
        <n-tab-pane name="products" tab="설치 프로그램">
          <ListHeader title="설치 프로그램 목록" :count="products.length" />
          <n-data-table
            :columns="productColumns"
            :data="products"
            size="small"
            :max-height="380"
            :pagination="{ pageSize: 20 }"
          />
        </n-tab-pane>

        <n-tab-pane name="hotfixes" tab="Windows 업데이트">
          <ListHeader title="Hotfix 목록" :count="hotfixes.length" />
          <n-data-table
            :columns="hotfixColumns"
            :data="hotfixes"
            size="small"
            :max-height="380"
            :pagination="{ pageSize: 20 }"
          />
        </n-tab-pane>

        <n-tab-pane name="processes" tab="실행 프로세스">
          <ListHeader title="프로세스 목록" :count="processes.length" />
          <n-data-table
            :columns="processColumns"
            :data="processes"
            size="small"
            :max-height="380"
            :pagination="{ pageSize: 20 }"
          />
        </n-tab-pane>

        <n-tab-pane name="accounts" tab="로컬 계정">
          <ListHeader title="로컬 계정 목록" :count="accounts.length" />
          <n-data-table
            :columns="accountColumns"
            :data="accounts"
            size="small"
            :max-height="380"
            :pagination="{ pageSize: 20 }"
          />
        </n-tab-pane>

        <n-tab-pane name="connections" tab="네트워크 연결">
          <ListHeader title="netstat 연결 목록" :count="connections.length" />
          <n-data-table
            :columns="connectionColumns"
            :data="connections"
            size="small"
            :max-height="380"
            :pagination="{ pageSize: 20 }"
          />
        </n-tab-pane>
      </n-tabs>

      <n-empty
        v-if="!hasData"
        description="수집 업로드된 데이터가 없습니다."
        style="margin-top: 32px"
      />
    </n-spin>
  </div>
</template>

<script setup>
import { computed, h, watch } from 'vue'
import { NTag } from 'naive-ui'

import { useAssetSwStore } from '@/stores/assetSwStore'
import ListHeader from '@/components/common/ListHeader.vue'

const props = defineProps({
  assetId: { type: Number, required: true },
})

const swStore = useAssetSwStore()

const products = computed(() => swStore.all.products || [])
const hotfixes = computed(() => swStore.all.hotfixes || [])
const processes = computed(() => swStore.all.processes || [])
const accounts = computed(() => swStore.all.accounts || [])
const connections = computed(() => swStore.all.connections || [])

const hasData = computed(() =>
  [products.value, hotfixes.value, processes.value, accounts.value, connections.value].some(
    (items) => Array.isArray(items) && items.length > 0
  )
)

const productColumns = [
  { title: '프로그램명', key: 'name', width: 280 },
  { title: '버전', key: 'version', width: 140 },
  { title: '제조사', key: 'vendor', width: 180 },
  { title: '설치일', key: 'install_date', width: 120, render: (row) => formatDate(row.install_date) },
]

const hotfixColumns = [
  { title: 'KB번호', key: 'hotfix_id', width: 140 },
  { title: '설명', key: 'description', width: 220 },
  { title: '설치일', key: 'installed_on', width: 120, render: (row) => formatDate(row.installed_on) },
  { title: '설치자', key: 'installed_by', width: 160 },
]

const processColumns = [
  { title: '프로세스명', key: 'process_name', width: 240 },
  { title: 'PID', key: 'pid', width: 90 },
  { title: '세션', key: 'session_name', width: 100 },
  { title: '메모리(KB)', key: 'memory_kb', width: 120 },
]

const accountColumns = [
  { title: '계정명', key: 'account_name', width: 200 },
  {
    title: '활성 상태',
    key: 'enabled',
    width: 100,
    render: (row) =>
      h(
        NTag,
        { type: row.enabled === false ? 'warning' : 'success', size: 'small' },
        { default: () => (row.enabled === false ? '미사용' : '활성') }
      ),
  },
  { title: '주석', key: 'comment', width: 320, render: (row) => row.comment || '-' },
]

const connectionColumns = [
  { title: '프로토콜', key: 'protocol', width: 100 },
  { title: '로컬 주소', key: 'local_address', width: 220 },
  { title: '원격 주소', key: 'remote_address', width: 220 },
  { title: '상태', key: 'state', width: 120, render: (row) => row.state || '-' },
  { title: '프로세스명', key: 'process_name', width: 180, render: (row) => row.process_name || '-' },
]

function formatDate(value) {
  if (!value) return '-'
  return String(value).slice(0, 10)
}

watch(
  () => props.assetId,
  (assetId) => {
    if (assetId) swStore.fetchAll(assetId)
  },
  { immediate: true }
)
</script>
