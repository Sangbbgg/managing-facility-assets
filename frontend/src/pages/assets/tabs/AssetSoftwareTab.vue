<template>
  <div>
    <n-spin :show="swStore.loading">
      <n-tabs type="line" size="small">
        <!-- 설치 프로그램 -->
        <n-tab-pane name="products" tab="설치 프로그램">
          <ListHeader title="설치 프로그램 목록" :count="(swStore.all.products || []).length" />
          <n-data-table :columns="productCols" :data="swStore.all.products || []" size="small" :max-height="350"
            :pagination="{ pageSize: 20 }" />
        </n-tab-pane>

        <!-- 핫픽스 -->
        <n-tab-pane name="hotfixes" tab="핫픽스/패치">
          <ListHeader title="핫픽스 목록" :count="(swStore.all.hotfixes || []).length" />
          <n-data-table :columns="hotfixCols" :data="swStore.all.hotfixes || []" size="small" :max-height="350"
            :pagination="{ pageSize: 20 }" />
        </n-tab-pane>

        <!-- 프로세스 스냅샷 -->
        <n-tab-pane name="processes" tab="프로세스 스냅샷">
          <ListHeader title="프로세스 목록" :count="(swStore.all.processes || []).length" />
          <n-data-table :columns="processCols" :data="swStore.all.processes || []" size="small" :max-height="350"
            :pagination="{ pageSize: 20 }" />
        </n-tab-pane>
      </n-tabs>

      <n-empty
        v-if="!hasData"
        description="수집된 소프트웨어 데이터가 없습니다"
        style="margin-top:32px;"
      />
    </n-spin>
  </div>
</template>

<script setup>
import { computed, watch } from 'vue'
import { useAssetSwStore } from '@/stores/assetSwStore'
import ListHeader from '@/components/common/ListHeader.vue'

const props  = defineProps({ assetId: { type: Number, required: true } })
const swStore = useAssetSwStore()

const hasData = computed(() =>
  Object.values(swStore.all).some(arr => Array.isArray(arr) && arr.length > 0)
)

const productCols = [
  { title: '프로그램명', key: 'name',    width: 250, ellipsis: { tooltip: true } },
  { title: '버전',      key: 'version', width: 120 },
  { title: '제조사',    key: 'vendor',  width: 150 },
  { title: '설치일',    key: 'install_date', width: 100 },
]
const hotfixCols = [
  { title: 'KB번호',   key: 'hotfix_id',   width: 120 },
  { title: '설명',     key: 'description', width: 200 },
  { title: '설치일',   key: 'installed_on', width: 100 },
  { title: '설치자',   key: 'installed_by', width: 120 },
]
const processCols = [
  { title: '프로세스명', key: 'process_name', width: 200 },
  { title: 'PID',       key: 'pid',          width: 80 },
  { title: '메모리(KB)', key: 'memory_kb',   width: 100 },
]

watch(() => props.assetId, (id) => { if (id) swStore.fetchAll(id) }, { immediate: true })
</script>
