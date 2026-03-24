<template>
  <div>
    <n-grid :cols="2" :x-gap="16">
      <!-- 좌: xlsx 셀 구조 -->
      <n-grid-item>
        <n-card title="xlsx 셀 구조" size="small">
          <n-spin :show="analyzing">
            <n-scrollbar style="max-height: 400px">
              <n-list v-if="labelCells.length">
                <n-list-item v-for="lc in labelCells" :key="lc.cell" style="padding: 4px 0">
                  <div style="display:flex;align-items:center;justify-content:space-between">
                    <span>
                      <n-tag size="small" type="info" style="margin-right:6px">{{ lc.cell }}</n-tag>
                      {{ lc.value }}
                    </span>
                    <n-button size="tiny" @click="openAddModal(lc.cell)">+ 매핑</n-button>
                  </div>
                </n-list-item>
              </n-list>
              <n-empty v-else description="셀 정보 없음" />
            </n-scrollbar>
          </n-spin>
        </n-card>
      </n-grid-item>

      <!-- 우: 매핑 목록 -->
      <n-grid-item>
        <n-card size="small">
          <template #header>
            <div style="display:flex;align-items:center;justify-content:space-between">
              <span>매핑 목록 ({{ localMappings.length }})</span>
              <n-button size="small" @click="openAddModal(null)">+ 추가</n-button>
            </div>
          </template>
          <n-scrollbar style="max-height: 400px">
            <n-list v-if="localMappings.length">
              <n-list-item v-for="(m, idx) in localMappings" :key="idx" style="padding: 4px 0">
                <div style="display:flex;align-items:center;justify-content:space-between">
                  <span style="font-size:13px">
                    <n-tag size="small" style="margin-right:4px">{{ m.cell }}</n-tag>
                    ← {{ m.data_source }}.{{ m.field }}
                    <span v-if="m.repeat_direction" style="color:#888;font-size:11px"> (반복)</span>
                  </span>
                  <n-button size="tiny" type="error" @click="removeMapping(idx)">삭제</n-button>
                </div>
              </n-list-item>
            </n-list>
            <n-empty v-else description="매핑 없음" />
          </n-scrollbar>
          <div style="margin-top:12px;text-align:right">
            <n-button type="primary" :loading="saving" @click="saveAll">전체 저장</n-button>
          </div>
        </n-card>
      </n-grid-item>
    </n-grid>

    <!-- 매핑 추가 모달 -->
    <n-modal v-model:show="showModal" preset="card" title="매핑 추가" style="width:480px">
      <n-form label-placement="left" label-width="100">
        <n-form-item label="셀 주소">
          <n-input v-model:value="form.cell" placeholder="예: B3" />
        </n-form-item>
        <n-form-item label="데이터 소스">
          <n-select
            v-model:value="form.data_source"
            :options="sourceOptions"
            @update:value="form.field = null"
          />
        </n-form-item>
        <n-form-item label="필드">
          <n-select
            v-model:value="form.field"
            :options="filteredFieldOptions"
            filterable
          />
        </n-form-item>
        <n-form-item label="포맷 (선택)">
          <n-input v-model:value="form.format" placeholder="예: YYYY년 MM월 DD일" />
        </n-form-item>
        <n-form-item label="반복 데이터">
          <n-switch v-model:value="form.is_repeat" />
        </n-form-item>
        <template v-if="form.is_repeat">
          <n-form-item label="최대 행 수">
            <n-input-number v-model:value="form.repeat_max_rows" :min="1" :max="100" />
          </n-form-item>
        </template>
      </n-form>
      <template #footer>
        <div style="text-align:right;gap:8px;display:flex;justify-content:flex-end">
          <n-button @click="showModal = false">취소</n-button>
          <n-button type="primary" :disabled="!canAdd" @click="addMapping">추가</n-button>
        </div>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { useFormTemplateStore } from '@/stores/formTemplateStore'
import formTemplatesApi from '@/api/formTemplatesApi'

const props = defineProps({ templateId: Number })
const message = useMessage()
const store = useFormTemplateStore()

const analyzing = ref(false)
const saving = ref(false)
const showModal = ref(false)
const labelCells = ref([])
const localMappings = ref([])

const form = ref({
  cell: '',
  data_source: null,
  field: null,
  format: '',
  is_repeat: false,
  repeat_max_rows: 10,
})

const sourceOptions = computed(() => {
  const sources = [...new Set(store.fieldCatalog.map(f => f.data_source))]
  return sources.map(s => ({ label: s, value: s }))
})

const filteredFieldOptions = computed(() => {
  if (!form.value.data_source) return []
  return store.fieldCatalog
    .filter(f => f.data_source === form.value.data_source)
    .map(f => ({ label: `${f.field}  (${f.label})`, value: f.field }))
})

const canAdd = computed(() => form.value.cell && form.value.data_source && form.value.field)

watch(() => props.templateId, async (id) => {
  if (!id) return
  await loadData(id)
}, { immediate: true })

async function loadData(id) {
  analyzing.value = true
  try {
    await store.fetchFieldCatalog()
    const [analyzeRes, mappingsRes] = await Promise.all([
      formTemplatesApi.analyze(id),
      formTemplatesApi.listMappings(id),
    ])
    labelCells.value = analyzeRes.data.label_cells || []
    localMappings.value = mappingsRes.data.map(m => ({ ...m }))
  } finally {
    analyzing.value = false
  }
}

function openAddModal(cell) {
  form.value = { cell: cell || '', data_source: null, field: null, format: '', is_repeat: false, repeat_max_rows: 10 }
  showModal.value = true
}

function addMapping() {
  localMappings.value.push({
    cell: form.value.cell,
    data_source: form.value.data_source,
    field: form.value.field,
    display_label: '',
    format: form.value.format || null,
    repeat_direction: form.value.is_repeat ? 'down' : null,
    repeat_max_rows: form.value.is_repeat ? form.value.repeat_max_rows : null,
    sort_order: localMappings.value.length,
  })
  showModal.value = false
}

function removeMapping(idx) {
  localMappings.value.splice(idx, 1)
}

async function saveAll() {
  saving.value = true
  try {
    await store.bulkSaveMappings(props.templateId, localMappings.value)
    message.success('저장되었습니다')
  } catch (e) {
    message.error('저장 실패: ' + (e.message || ''))
  } finally {
    saving.value = false
  }
}
</script>
