<template>
  <PageShell title="자산 세부사항">
    <div style="display:flex; gap:16px; height:calc(100vh - 140px);">
      <!-- 좌측: 자산 목록 패널 -->
      <div style="width:280px; flex-shrink:0; display:flex; flex-direction:column; gap:8px;">
        <n-input
          v-model:value="search"
          placeholder="자산코드 / 자산명 검색"
          clearable
          size="small"
        />
        <n-scrollbar style="flex:1;">
          <div
            v-for="a in filteredList"
            :key="a.id"
            :class="['asset-list-item', { active: selectedId === a.id }]"
            @click="selectAsset(a.id)"
          >
            <n-text strong style="font-size:12px;">{{ a.asset_code }}</n-text>
            <br />
            <n-text style="font-size:13px;">{{ a.asset_name }}</n-text>
          </div>
          <n-empty v-if="!filteredList.length" description="검색 결과 없음" size="small" />
        </n-scrollbar>
      </div>

      <!-- 우측: 상세 패널 -->
      <div style="flex:1; overflow:auto;">
        <div v-if="selectedAsset">
          <!-- 자산 코드 헤더 -->
          <n-space align="center" style="margin-bottom:12px;">
            <n-tag type="info" size="large">{{ selectedAsset.asset_code }}</n-tag>
            <n-text style="font-size:18px; font-weight:600;">{{ selectedAsset.asset_name }}</n-text>
          </n-space>

          <!-- 탭 -->
          <n-tabs v-model:value="activeTab" type="line" animated>
            <n-tab-pane name="basic" tab="기본 정보">
              <AssetBasicInfoTab :asset="selectedAsset" @updated="reloadAsset" />
            </n-tab-pane>

            <n-tab-pane name="hardware" tab="하드웨어">
              <AssetHardwareTab :asset-id="selectedId" />
            </n-tab-pane>

            <n-tab-pane name="software" tab="소프트웨어">
              <AssetSoftwareTab :asset-id="selectedId" />
            </n-tab-pane>

            <n-tab-pane name="custom" tab="사용자 메모">
              <AssetCustomFieldsTab :asset-id="selectedId" />
            </n-tab-pane>

            <n-tab-pane name="collect" tab="수집 업로드">
              <AssetCollectUploadTab :asset-id="selectedId" @collected="onCollected" />
            </n-tab-pane>

            <n-tab-pane name="changelog" tab="변경 이력">
              <AssetChangeLogTab :asset-id="selectedId" />
            </n-tab-pane>
          </n-tabs>
        </div>

        <div v-else style="display:flex; align-items:center; justify-content:center; height:100%;">
          <n-empty description="좌측에서 자산을 선택하세요" />
        </div>
      </div>
    </div>
  </PageShell>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import PageShell from '@/components/common/PageShell.vue'
import AssetBasicInfoTab    from './tabs/AssetBasicInfoTab.vue'
import AssetHardwareTab     from './tabs/AssetHardwareTab.vue'
import AssetSoftwareTab     from './tabs/AssetSoftwareTab.vue'
import AssetCustomFieldsTab from './tabs/AssetCustomFieldsTab.vue'
import AssetCollectUploadTab from './tabs/AssetCollectUploadTab.vue'
import AssetChangeLogTab    from './tabs/AssetChangeLogTab.vue'
import { useAssetStore } from '@/stores/assetStore'
import { useAssetHwStore } from '@/stores/assetHwStore'
import { useAssetSwStore } from '@/stores/assetSwStore'

const route      = useRoute()
const assetStore = useAssetStore()
const hwStore    = useAssetHwStore()
const swStore    = useAssetSwStore()

const search       = ref('')
const selectedId   = ref(null)
const selectedAsset = ref(null)
const activeTab    = ref('basic')

const filteredList = computed(() => {
  const q = search.value.toLowerCase()
  return assetStore.list.filter(a =>
    !q ||
    a.asset_code?.toLowerCase().includes(q) ||
    a.asset_name?.toLowerCase().includes(q)
  )
})

async function selectAsset(id) {
  selectedId.value = id
  activeTab.value = 'basic'
  await reloadAsset()
  hwStore.reset()
  swStore.reset()
}

async function reloadAsset() {
  if (!selectedId.value) return
  await assetStore.fetchOne(selectedId.value)
  selectedAsset.value = assetStore.current
}

async function onCollected() {
  // 수집 완료 후 HW/SW 탭 새로고침
  if (selectedId.value) {
    await hwStore.fetchAll(selectedId.value)
    await swStore.fetchAll(selectedId.value)
  }
}

onMounted(async () => {
  await assetStore.fetchList()
  // query param ?id=xxx 처리
  const qid = route.query.id ? Number(route.query.id) : null
  if (qid) { await selectAsset(qid) }
})
</script>

<style scoped>
.asset-list-item {
  padding: 8px 10px;
  border-radius: 6px;
  cursor: pointer;
  border: 1px solid transparent;
  margin-bottom: 4px;
  transition: background 0.15s;
}
.asset-list-item:hover {
  background: rgba(99, 162, 255, 0.1);
}
.asset-list-item.active {
  background: rgba(99, 162, 255, 0.18);
  border-color: #63a2ff;
}
</style>
