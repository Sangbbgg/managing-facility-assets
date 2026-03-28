<template>
  <div>
    <n-spin :show="hwStore.loading">
      <n-collapse v-if="hasData" accordion>
        <!-- 시스템 -->
        <n-collapse-item title="시스템 정보" name="systems">
          <ListHeader title="시스템 정보" :count="(hwStore.all.systems || []).length" />
          <n-data-table :columns="sysCols" :data="hwStore.all.systems || []" size="small" :max-height="220" />
        </n-collapse-item>

        <!-- CPU -->
        <n-collapse-item title="CPU 정보" name="cpus">
          <ListHeader title="CPU 정보" :count="(hwStore.all.cpus || []).length" />
          <n-data-table :columns="cpuCols" :data="hwStore.all.cpus || []" size="small" :max-height="220" />
        </n-collapse-item>

        <!-- 메모리 -->
        <n-collapse-item title="메모리 정보" name="memories">
          <ListHeader title="메모리 정보" :count="(hwStore.all.memories || []).length" />
          <n-data-table :columns="memCols" :data="hwStore.all.memories || []" size="small" :max-height="220" />
        </n-collapse-item>

        <!-- 디스크 -->
        <n-collapse-item title="디스크 정보" name="disks">
          <ListHeader title="디스크 정보" :count="(hwStore.all.disks || []).length" />
          <n-data-table :columns="diskCols" :data="hwStore.all.disks || []" size="small" :max-height="220" />
        </n-collapse-item>

        <!-- GPU -->
        <n-collapse-item title="GPU 정보" name="gpus">
          <ListHeader title="GPU 정보" :count="(hwStore.all.gpus || []).length" />
          <n-data-table :columns="gpuCols" :data="hwStore.all.gpus || []" size="small" :max-height="220" />
        </n-collapse-item>

        <!-- NIC -->
        <n-collapse-item title="네트워크 어댑터" name="nics">
          <ListHeader title="네트워크 어댑터" :count="(hwStore.all.nics || []).length" />
          <n-data-table :columns="nicCols" :data="hwStore.all.nics || []" size="small" :max-height="220" />
        </n-collapse-item>
      </n-collapse>

      <n-empty v-else description="수집된 하드웨어 데이터가 없습니다" style="margin-top:32px;" />
    </n-spin>
  </div>
</template>

<script setup>
import { computed, onMounted, watch } from 'vue'
import { useAssetHwStore } from '@/stores/assetHwStore'
import ListHeader from '@/components/common/ListHeader.vue'

const props  = defineProps({ assetId: { type: Number, required: true } })
const hwStore = useAssetHwStore()

const hasData = computed(() =>
  Object.values(hwStore.all).some(arr => Array.isArray(arr) && arr.length > 0)
)

// 컬럼 정의
const sysCols = [
  { title: '수집일시',  key: 'collected_at', width: 160, render: r => r.collected_at?.slice(0,16) },
  { title: '제조사',    key: 'manufacturer', width: 120 },
  { title: '모델',      key: 'system_model', width: 200 },
  { title: 'OS',        key: 'os_name',      width: 200 },
  { title: 'OS 버전',   key: 'os_version',   width: 100 },
  { title: '호스트명',  key: 'hostname',     width: 120 },
  { title: '메모리(MB)', key: 'total_memory_mb', width: 100 },
]
const cpuCols = [
  { title: '수집일시',  key: 'collected_at', width: 160, render: r => r.collected_at?.slice(0,16) },
  { title: '모델명',    key: 'name',         width: 250 },
  { title: '코어수',    key: 'cores',        width: 70 },
  { title: '논리CPUs',  key: 'logical_cpus', width: 80 },
  { title: 'Max MHz',   key: 'max_clock_mhz',width: 80 },
  { title: '아키텍처',  key: 'architecture', width: 70 },
]
const memCols = [
  { title: '수집일시', key: 'collected_at', width: 160, render: r => r.collected_at?.slice(0,16) },
  { title: '슬롯',     key: 'locator',     width: 100 },
  { title: '용량(B)',  key: 'capacity_bytes', width: 120 },
  { title: '속도(MHz)', key: 'speed_mhz',  width: 80 },
  { title: '제조사',   key: 'manufacturer',width: 120 },
]
const diskCols = [
  { title: '수집일시',  key: 'collected_at', width: 160, render: r => r.collected_at?.slice(0,16) },
  { title: '모델',      key: 'model',        width: 200 },
  { title: '크기(B)',   key: 'size_bytes',   width: 120 },
  { title: '인터페이스', key: 'interface_type', width: 80 },
  { title: '미디어유형', key: 'media_type',  width: 100 },
]
const gpuCols = [
  { title: '수집일시',  key: 'collected_at', width: 160, render: r => r.collected_at?.slice(0,16) },
  { title: '모델명',    key: 'name',         width: 250 },
  { title: '드라이버',  key: 'driver_version', width: 120 },
  { title: 'VRAM(MB)', key: 'video_memory_mb', width: 90 },
]
const nicCols = [
  { title: '수집일시',  key: 'collected_at', width: 160, render: r => r.collected_at?.slice(0,16) },
  { title: '어댑터명',  key: 'adapter_name', width: 200 },
  { title: 'MAC',       key: 'mac_address',  width: 150 },
  { title: 'IPv4',      key: 'ipv4_address', width: 130 },
  { title: 'DHCP',      key: 'dhcp_enabled', width: 70, render: r => r.dhcp_enabled ? 'Y' : 'N' },
]

watch(() => props.assetId, (id) => { if (id) hwStore.fetchAll(id) }, { immediate: true })
onMounted(() => { if (props.assetId) hwStore.fetchAll(props.assetId) })
</script>
