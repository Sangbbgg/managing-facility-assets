<template>
  <div>
    <n-spin :show="hwStore.loading">
      <n-collapse v-if="hasData" accordion>
        <n-collapse-item title="시스템 정보" name="systems">
          <ListHeader title="시스템 정보" :count="systems.length" />
          <div class="table-scroll-wrap">
            <div class="table-scroll-inner" style="width: 1600px;">
              <n-data-table :columns="systemColumns" :data="systems" size="small" :max-height="260" :scroll-x="1600" />
            </div>
          </div>
        </n-collapse-item>

        <n-collapse-item title="CPU 정보" name="cpus">
          <ListHeader title="CPU 정보" :count="cpus.length" />
          <div class="table-scroll-wrap">
            <div class="table-scroll-inner" style="width: 1300px;">
              <n-data-table :columns="cpuColumns" :data="cpus" size="small" :max-height="260" :scroll-x="1300" />
            </div>
          </div>
        </n-collapse-item>

        <n-collapse-item title="메모리 정보" name="memories">
          <ListHeader title="메모리 정보" :count="memories.length" />
          <div class="table-scroll-wrap">
            <div class="table-scroll-inner" style="width: 1300px;">
              <n-data-table :columns="memoryColumns" :data="memories" size="small" :max-height="300" :scroll-x="1300" />
            </div>
          </div>
        </n-collapse-item>

        <n-collapse-item title="디스크 정보" name="disks">
          <ListHeader title="디스크 정보" :count="disks.length" />
          <div class="table-scroll-wrap">
            <div class="table-scroll-inner" style="width: 1300px;">
              <n-data-table :columns="diskColumns" :data="disks" size="small" :max-height="300" :scroll-x="1300" />
            </div>
          </div>
        </n-collapse-item>

        <n-collapse-item title="광학 드라이브 정보" name="opticals">
          <ListHeader title="광학 드라이브 정보" :count="opticals.length" />
          <div class="table-scroll-wrap">
            <div class="table-scroll-inner" style="width: 1200px;">
              <n-data-table :columns="opticalColumns" :data="opticals" size="small" :max-height="260" :scroll-x="1200" />
            </div>
          </div>
        </n-collapse-item>

        <n-collapse-item title="GPU 정보" name="gpus">
          <ListHeader title="GPU 정보" :count="gpus.length" />
          <div class="table-scroll-wrap">
            <div class="table-scroll-inner" style="width: 1100px;">
              <n-data-table :columns="gpuColumns" :data="gpus" size="small" :max-height="260" :scroll-x="1100" />
            </div>
          </div>
        </n-collapse-item>

        <n-collapse-item title="네트워크 어댑터" name="nics">
          <ListHeader title="네트워크 어댑터" :count="nics.length" />
          <div class="table-scroll-wrap">
            <div class="table-scroll-inner" style="width: 1700px;">
              <n-data-table :columns="nicColumns" :data="nics" size="small" :max-height="320" :scroll-x="1700" />
            </div>
          </div>
        </n-collapse-item>
      </n-collapse>

      <n-empty
        v-else
        description="수집된 하드웨어 데이터가 없습니다."
        style="margin-top: 32px;"
      />
    </n-spin>
  </div>
</template>

<script setup>
import { computed, onMounted, watch } from 'vue'
import { useAssetHwStore } from '@/stores/assetHwStore'
import ListHeader from '@/components/common/ListHeader.vue'

const props = defineProps({
  assetId: { type: Number, required: true },
})

const hwStore = useAssetHwStore()

const systems = computed(() => hwStore.all.systems || [])
const cpus = computed(() => hwStore.all.cpus || [])
const memories = computed(() => hwStore.all.memories || [])
const disks = computed(() => hwStore.all.disks || [])
const opticals = computed(() => hwStore.all.opticals || [])
const gpus = computed(() => hwStore.all.gpus || [])
const nics = computed(() => hwStore.all.nics || [])

const hasData = computed(() =>
  [systems.value, cpus.value, memories.value, disks.value, opticals.value, gpus.value, nics.value].some(
    (items) => Array.isArray(items) && items.length > 0
  )
)

const systemColumns = [
  { title: '수집일시', key: 'collected_at', width: 160, render: (row) => formatDateTime(row.collected_at) },
  { title: '제조사', key: 'manufacturer', width: 140 },
  { title: '모델명', key: 'system_model', width: 220 },
  { title: 'S/N', key: 'system_serial', width: 180 },
  { title: '시스템 종류', key: 'system_type', width: 160 },
  { title: 'OS', key: 'os_name', width: 220 },
  { title: 'OS 버전', key: 'os_version', width: 120 },
  { title: 'OS 아키텍처', key: 'os_arch', width: 140 },
  { title: '호스트명', key: 'hostname', width: 150 },
  { title: '메모리 총량(GB)', key: 'total_memory_mb', width: 130, render: (row) => formatMegabytesAsGb(row.total_memory_mb) },
]

const cpuColumns = [
  { title: '수집일시', key: 'collected_at', width: 160, render: (row) => formatDateTime(row.collected_at) },
  { title: '모델명', key: 'name', width: 260 },
  { title: '제조사', key: 'manufacturer', width: 140 },
  { title: '코어 수', key: 'cores', width: 90 },
  { title: '논리 CPU', key: 'logical_cpus', width: 100 },
  { title: '최대 MHz', key: 'max_clock_mhz', width: 100 },
  { title: '아키텍처', key: 'architecture', width: 100 },
  { title: '소켓', key: 'socket', width: 120 },
]

const memoryColumns = [
  { title: '수집일시', key: 'collected_at', width: 160, render: (row) => formatDateTime(row.collected_at) },
  { title: '슬롯', key: 'locator', width: 120 },
  { title: '용량(GB)', key: 'capacity_bytes', width: 100, render: (row) => formatBytesAsGb(row.capacity_bytes) },
  { title: '속도(MHz)', key: 'speed_mhz', width: 100 },
  { title: '제조사', key: 'manufacturer', width: 140 },
  { title: 'PartNumber', key: 'part_number', width: 180 },
  { title: 'SerialNumber', key: 'serial_number', width: 180 },
  { title: '폼팩터', key: 'form_factor', width: 100 },
]

const diskColumns = [
  { title: '수집일시', key: 'collected_at', width: 160, render: (row) => formatDateTime(row.collected_at) },
  { title: '모델명', key: 'model', width: 260 },
  { title: '크기(GB)', key: 'size_bytes', width: 110, render: (row) => formatBytesAsGb(row.size_bytes) },
  { title: '인터페이스', key: 'interface_type', width: 110 },
  { title: '시리얼 번호', key: 'serial_number', width: 180 },
  { title: '미디어 유형', key: 'media_type', width: 120 },
  { title: '파티션 수', key: 'partitions', width: 100 },
]

const opticalColumns = [
  { title: '수집일시', key: 'collected_at', width: 160, render: (row) => formatDateTime(row.collected_at) },
  { title: '드라이브명', key: 'name', width: 300 },
  { title: '드라이브', key: 'drive', width: 100 },
  { title: '미디어 유형', key: 'media_type', width: 140 },
  { title: '상태', key: 'status', width: 120 },
  { title: '제조사', key: 'manufacturer', width: 160 },
]

const gpuColumns = [
  { title: '수집일시', key: 'collected_at', width: 160, render: (row) => formatDateTime(row.collected_at) },
  { title: '모델명', key: 'name', width: 260 },
  { title: '드라이버 버전', key: 'driver_version', width: 140 },
  { title: 'VRAM(MB)', key: 'video_memory_mb', width: 100 },
  { title: '해상도', key: 'resolution', width: 160 },
]

const nicColumns = [
  { title: '수집일시', key: 'collected_at', width: 160, render: (row) => formatDateTime(row.collected_at) },
  { title: '어댑터명', key: 'adapter_name', width: 240 },
  { title: '연결명', key: 'connection_name', width: 140 },
  { title: 'MAC', key: 'mac_address', width: 170 },
  { title: 'IPv4', key: 'ipv4_address', width: 150 },
  { title: 'Subnet Mask', key: 'subnet_mask', width: 130 },
  { title: 'Default Gateway', key: 'default_gateway', width: 150 },
  { title: 'DNS Servers', key: 'dns_servers', width: 220 },
  { title: 'DHCP', key: 'dhcp_enabled', width: 80, render: (row) => (row.dhcp_enabled ? 'Y' : 'N') },
]

function formatDateTime(value) {
  if (!value) return '-'
  return String(value).replace('T', ' ').slice(0, 16)
}

function formatBytesAsGb(value) {
  if (value == null || value === '') return '-'
  const bytes = Number(value)
  if (Number.isNaN(bytes)) return '-'
  return (bytes / (1024 ** 3)).toFixed(2)
}

function formatMegabytesAsGb(value) {
  if (value == null || value === '') return '-'
  const megabytes = Number(value)
  if (Number.isNaN(megabytes)) return '-'
  return (megabytes / 1024).toFixed(2)
}

watch(
  () => props.assetId,
  (assetId) => {
    if (assetId) hwStore.fetchAll(assetId)
  },
  { immediate: true }
)

onMounted(() => {
  if (props.assetId) hwStore.fetchAll(props.assetId)
})
</script>

<style scoped>
.table-scroll-wrap {
  overflow-x: auto;
  padding-bottom: 4px;
  width: 100%;
}

.table-scroll-inner {
  max-width: none;
}
</style>
