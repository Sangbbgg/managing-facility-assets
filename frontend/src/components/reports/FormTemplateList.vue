<template>
  <div class="template-list">
    <ListHeader title="템플릿 목록" :count="store.templates.length">
      <template #extra>
        <div class="header-actions">
          <n-button @click="openCreateFolder">폴더 추가</n-button>
          <n-button type="primary" @click="$emit('create')">새 템플릿 등록</n-button>
        </div>
      </template>
    </ListHeader>

    <n-collapse :expanded-names="expandedNames" @update:expanded-names="expandedNames = $event">
      <n-collapse-item
        v-for="section in sections"
        :key="section.key"
        :name="section.key"
        :title="section.title"
      >
        <template #header-extra>
          <div class="section-extra">
            <span class="section-count">{{ section.items.length }}</span>
            <template v-if="section.folder">
              <n-button
                size="tiny"
                quaternary
                @click.stop="openEditFolder(section.folder)"
              >
                수정
              </n-button>
              <n-button
                size="tiny"
                quaternary
                type="error"
                @click.stop="handleDeleteFolder(section.folder)"
              >
                삭제
              </n-button>
            </template>
          </div>
        </template>

        <div v-if="section.items.length" class="item-list">
          <button
            v-for="template in section.items"
            :key="template.id"
            type="button"
            class="template-item"
            :class="{ selected: template.id === selectedId }"
            @click="$emit('select', template)"
          >
            <div class="item-main">
              <div class="item-title">{{ template.name }}</div>
              <div class="item-subtitle">
                {{ template.file_name }}
              </div>
              <div class="item-meta">
                <span>{{ categoryLabel[template.category] || template.category }}</span>
                <span>매핑 {{ template.mapping_count || 0 }}개</span>
                <span>{{ template.is_active ? '활성' : '비활성' }}</span>
              </div>
              <div class="item-equipment-types">
                {{ formatGroups(template.groups) }}
              </div>
            </div>

            <div class="item-actions">
              <n-button
                size="tiny"
                @click.stop="$emit('edit', template)"
              >
                수정
              </n-button>
              <n-button
                size="tiny"
                type="error"
                @click.stop="handleDeleteTemplate(template)"
              >
                삭제
              </n-button>
            </div>
          </button>
        </div>

        <n-empty
          v-else
          size="small"
          description="템플릿이 없습니다."
          style="padding: 20px 0"
        />
      </n-collapse-item>
    </n-collapse>

    <n-modal
      v-model:show="showFolderModal"
      preset="card"
      :title="editingFolder ? '폴더 수정' : '폴더 추가'"
      style="width: 420px; max-width: 92vw"
      :mask-closable="false"
    >
      <n-form>
        <n-form-item label="폴더명">
          <n-input v-model:value="folderName" placeholder="예: 운영 보고서" />
        </n-form-item>
      </n-form>

      <template #footer>
        <div class="modal-footer">
          <n-button @click="closeFolderModal">취소</n-button>
          <n-button type="primary" @click="submitFolder">저장</n-button>
        </div>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useDialog, useMessage } from 'naive-ui'
import ListHeader from '@/components/common/ListHeader.vue'
import { useFormTemplateStore } from '@/stores/formTemplateStore'

const props = defineProps({
  selectedId: {
    type: Number,
    default: null,
  },
})

defineEmits(['create', 'select', 'edit'])

const store = useFormTemplateStore()
const message = useMessage()
const dialog = useDialog()

const expandedNames = ref([])
const showFolderModal = ref(false)
const editingFolder = ref(null)
const folderName = ref('')

const categoryLabel = {
  general: '일반',
  inspection: '점검',
  security: '보안',
}

function formatGroups(groups = []) {
  if (!groups.length) {
    return '적용 그룹: 전체'
  }
  return `적용 그룹: ${groups.map((group) => group.full_path || group.name).join(', ')}`
}

const sections = computed(() => {
  const grouped = new Map()
  for (const folder of store.folders) {
    grouped.set(folder.id, {
      key: `folder-${folder.id}`,
      title: folder.name,
      folder,
      items: [],
    })
  }

  const uncategorized = {
    key: 'folder-none',
    title: '미분류',
    folder: null,
    items: [],
  }

  for (const template of store.templates) {
    if (template.folder_id && grouped.has(template.folder_id)) {
      grouped.get(template.folder_id).items.push(template)
    } else {
      uncategorized.items.push(template)
    }
  }

  const result = [...grouped.values()]
  if (uncategorized.items.length || result.length === 0) {
    result.push(uncategorized)
  }
  return result
})

watch(
  sections,
  (value) => {
    expandedNames.value = value.map((section) => section.key)
  },
  { immediate: true },
)

function openCreateFolder() {
  editingFolder.value = null
  folderName.value = ''
  showFolderModal.value = true
}

function openEditFolder(folder) {
  editingFolder.value = folder
  folderName.value = folder.name
  showFolderModal.value = true
}

function closeFolderModal() {
  showFolderModal.value = false
  editingFolder.value = null
  folderName.value = ''
}

async function submitFolder() {
  const name = folderName.value.trim()
  if (!name) {
    message.warning('폴더명을 입력하세요.')
    return
  }

  try {
    if (editingFolder.value) {
      await store.updateFolder(editingFolder.value.id, { name })
      message.success('폴더를 수정했습니다.')
    } else {
      await store.createFolder({ name })
      message.success('폴더를 추가했습니다.')
    }
    closeFolderModal()
  } catch (error) {
    message.error(error.response?.data?.detail || '폴더 저장에 실패했습니다.')
  }
}

function handleDeleteFolder(folder) {
  dialog.warning({
    title: '폴더 삭제',
    content: `"${folder.name}" 폴더를 삭제하시겠습니까? 비어 있는 폴더만 삭제할 수 있습니다.`,
    positiveText: '삭제',
    negativeText: '취소',
    onPositiveClick: async () => {
      try {
        await store.removeFolder(folder.id)
        message.success('폴더를 삭제했습니다.')
      } catch (error) {
        message.error(error.response?.data?.detail || '폴더 삭제에 실패했습니다.')
      }
    },
  })
}

function handleDeleteTemplate(template) {
  dialog.warning({
    title: '템플릿 삭제',
    content: `"${template.name}" 템플릿을 삭제하시겠습니까?`,
    positiveText: '삭제',
    negativeText: '취소',
    onPositiveClick: async () => {
      try {
        await store.remove(template.id)
        message.success('템플릿을 삭제했습니다.')
      } catch {
        message.error('템플릿 삭제에 실패했습니다.')
      }
    },
  })
}
</script>

<style scoped>
.header-actions {
  display: flex;
  gap: 8px;
}

.section-extra {
  display: flex;
  align-items: center;
  gap: 6px;
}

.section-count {
  min-width: 18px;
  font-size: 12px;
  color: #64748b;
  text-align: center;
}

.item-list {
  display: grid;
  gap: 8px;
}

.template-item {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  width: 100%;
  padding: 12px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #fff;
  text-align: left;
  cursor: pointer;
  transition: border-color 0.2s ease, background-color 0.2s ease, box-shadow 0.2s ease;
}

.template-item:hover {
  border-color: #bfd4ea;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
}

.template-item.selected {
  border-color: #60a5fa;
  background: #eff6ff;
}

.item-main {
  min-width: 0;
  display: grid;
  gap: 4px;
}

.item-title {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
  word-break: break-word;
}

.item-subtitle {
  font-size: 12px;
  color: #64748b;
  word-break: break-all;
}

.item-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  font-size: 12px;
  color: #64748b;
}

.item-equipment-types {
  font-size: 12px;
  color: #475569;
}

.item-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
