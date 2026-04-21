<template>
  <PageShell title="DB 스냅샷">
    <template #actions>
      <n-button @click="loadSnapshots" :loading="loadingSnapshots">새로고침</n-button>
    </template>

    <n-space vertical size="large">
      <n-card title="현재 DB 저장" size="small">
        <n-space vertical size="medium">
          <n-alert type="info" :show-icon="false">
            스냅샷을 로드하면 현재 DB 전체가 선택한 시점으로 교체됩니다. 로드 직전에 자동으로 취소 지점을 저장하므로 필요하면 마지막 로드를 되돌릴 수 있습니다.
          </n-alert>

          <div class="save-row">
            <n-input
              v-model:value="snapshotName"
              placeholder="스냅샷 이름을 입력하세요"
              maxlength="120"
              clearable
            />
            <n-input
              v-model:value="snapshotDescription"
              type="textarea"
              placeholder="추가 설명을 입력하세요"
              :autosize="{ minRows: 3, maxRows: 5 }"
              maxlength="2000"
              clearable
            />
            <n-button type="primary" :loading="savingSnapshot" @click="handleSaveSnapshot">
              저장
            </n-button>
          </div>

          <n-card
            v-if="rollbackSnapshot"
            size="small"
            embedded
            class="rollback-card"
            title="마지막 로드 취소 가능"
          >
              <div class="rollback-body">
                <div>
                  <div class="rollback-title">{{ rollbackSnapshot.name }}</div>
                  <div v-if="rollbackSnapshot.description" class="rollback-description">
                    {{ rollbackSnapshot.description }}
                  </div>
                  <div class="rollback-meta">
                    생성 시각 {{ formatDateTime(rollbackSnapshot.created_at) }}
                  </div>
              </div>
              <n-button
                type="warning"
                :loading="rollingBack"
                @click="handleRollbackSnapshot"
              >
                취소
              </n-button>
            </div>
          </n-card>
        </n-space>
      </n-card>

      <n-card title="저장된 스냅샷" size="small">
        <n-spin :show="loadingSnapshots">
          <n-empty
            v-if="!manualSnapshots.length"
            description="저장된 수동 스냅샷이 없습니다"
            style="padding: 32px 0"
          />

          <n-space v-else vertical size="medium">
            <n-card
              v-for="snapshot in manualSnapshots"
              :key="snapshot.id"
              size="small"
              embedded
            >
              <div class="snapshot-row">
                <div class="snapshot-main">
                  <div class="snapshot-header">
                    <strong>{{ snapshot.name }}</strong>
                    <n-tag size="small" type="success">수동 저장</n-tag>
                  </div>
                  <div class="snapshot-meta">
                    생성 시각 {{ formatDateTime(snapshot.created_at) }}
                  </div>
                  <div v-if="snapshot.description" class="snapshot-description">
                    {{ snapshot.description }}
                  </div>
                  <div class="snapshot-meta">
                    테이블 {{ formatNumber(snapshot.table_count) }}개 · 행 {{ formatNumber(snapshot.row_count) }}개
                  </div>
                  <div class="snapshot-meta">
                    {{ formatTableSummary(snapshot.table_counts_json) }}
                  </div>
                </div>

                <n-popconfirm @positive-click="() => handleRestoreSnapshot(snapshot)">
                  <template #trigger>
                    <n-button
                      type="primary"
                      :loading="restoringSnapshotId === snapshot.id"
                    >
                      로드
                    </n-button>
                  </template>
                  현재 DB를 이 스냅샷 상태로 교체합니다. 계속할까요?
                </n-popconfirm>
              </div>
            </n-card>
          </n-space>
        </n-spin>
      </n-card>
    </n-space>
  </PageShell>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useMessage } from 'naive-ui'
import PageShell from '@/components/common/PageShell.vue'
import { adminApi } from '@/api/adminApi'

const message = useMessage()

const snapshots = ref([])
const loadingSnapshots = ref(false)
const savingSnapshot = ref(false)
const restoringSnapshotId = ref(null)
const rollingBack = ref(false)
const snapshotName = ref(createDefaultSnapshotName())
const snapshotDescription = ref('')

const manualSnapshots = computed(() =>
  snapshots.value.filter(snapshot => snapshot.snapshot_type !== 'rollback')
)

const rollbackSnapshot = computed(() =>
  snapshots.value.find(snapshot => snapshot.snapshot_type === 'rollback') || null
)

function createDefaultSnapshotName() {
  const now = new Date()
  const pad = (value) => String(value).padStart(2, '0')
  return `DB 스냅샷 ${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`
}

function formatDateTime(value) {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString('ko-KR', { hour12: false })
}

function formatNumber(value) {
  return Number(value || 0).toLocaleString('ko-KR')
}

function formatTableSummary(tableCounts) {
  if (!Array.isArray(tableCounts) || !tableCounts.length) {
    return '저장된 테이블 정보가 없습니다'
  }
  const topTables = [...tableCounts]
    .sort((a, b) => (b.rows || 0) - (a.rows || 0))
    .slice(0, 4)
    .map(item => `${item.name}(${formatNumber(item.rows)})`)
  return `주요 테이블: ${topTables.join(', ')}`
}

async function loadSnapshots() {
  loadingSnapshots.value = true
  try {
    snapshots.value = await adminApi.listSnapshots()
  } catch (error) {
    message.error(error.message)
  } finally {
    loadingSnapshots.value = false
  }
}

async function handleSaveSnapshot() {
  const name = snapshotName.value.trim()
  if (!name) {
    message.warning('스냅샷 이름을 입력해 주세요')
    return
  }

  savingSnapshot.value = true
  try {
    const snapshot = await adminApi.createSnapshot({
      name,
      description: snapshotDescription.value.trim() || null,
    })
    message.success(`'${snapshot.name}' 스냅샷을 저장했습니다`)
    snapshotName.value = createDefaultSnapshotName()
    snapshotDescription.value = ''
    await loadSnapshots()
  } catch (error) {
    message.error(error.message)
  } finally {
    savingSnapshot.value = false
  }
}

async function handleRestoreSnapshot(snapshot) {
  restoringSnapshotId.value = snapshot.id
  try {
    const result = await adminApi.restoreSnapshot(snapshot.id)
    message.success(result.message)
    await loadSnapshots()
  } catch (error) {
    message.error(error.message)
  } finally {
    restoringSnapshotId.value = null
  }
}

async function handleRollbackSnapshot() {
  rollingBack.value = true
  try {
    const result = await adminApi.rollbackSnapshot()
    message.success(result.message)
    await loadSnapshots()
  } catch (error) {
    message.error(error.message)
  } finally {
    rollingBack.value = false
  }
}

onMounted(loadSnapshots)
</script>

<style scoped>
.save-row {
  display: grid;
  gap: 12px;
  grid-template-columns: minmax(0, 1fr);
}

.rollback-card {
  background: #fff8e1;
}

.rollback-body {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.rollback-title {
  font-weight: 600;
}

.rollback-meta {
  color: #666;
  font-size: 13px;
  margin-top: 4px;
}

.rollback-description,
.snapshot-description {
  color: #333;
  font-size: 14px;
  margin-top: 6px;
  white-space: pre-wrap;
  word-break: break-word;
}

.snapshot-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.snapshot-main {
  min-width: 0;
}

.snapshot-header {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.snapshot-meta {
  color: #666;
  font-size: 13px;
  margin-top: 6px;
  word-break: break-word;
}

@media (max-width: 768px) {
  .save-row {
    grid-template-columns: 1fr;
  }

  .rollback-body,
  .snapshot-row {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
