<template>
  <div>
    <n-space vertical>
      <ListHeader title="사용자 메모 목록" :count="fields.length" />
      <!-- 기존 메모 목록 -->
      <div v-for="field in fields" :key="field.id" style="display:flex; gap:8px; align-items:center;">
        <n-input
          :value="field.field_key"
          style="width:140px;"
          placeholder="키"
          @update:value="v => field.field_key = v"
          @blur="updateField(field)"
        />
        <n-input
          :value="field.field_value"
          style="flex:1;"
          placeholder="값"
          @update:value="v => field.field_value = v"
          @blur="updateField(field)"
        />
        <n-button size="small" type="error" @click="removeField(field.id)">삭제</n-button>
      </div>

      <!-- 새 메모 추가 행 -->
      <div v-if="adding" style="display:flex; gap:8px; align-items:center;">
        <n-input v-model:value="newKey" style="width:140px;" placeholder="키 입력" />
        <n-input v-model:value="newVal" style="flex:1;" placeholder="값 입력" />
        <n-button size="small" type="primary" @click="addField">추가</n-button>
        <n-button size="small" @click="adding=false">취소</n-button>
      </div>

      <n-button v-if="!adding" size="small" @click="adding=true">+ 메모 추가</n-button>
    </n-space>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useMessage } from 'naive-ui'
import { customFieldsApi } from '@/api/customFieldsApi'
import ListHeader from '@/components/common/ListHeader.vue'

const props = defineProps({ assetId: { type: Number, required: true } })
const message = useMessage()

const fields = ref([])
const adding = ref(false)
const newKey = ref('')
const newVal = ref('')

async function load() {
  try { fields.value = await customFieldsApi.list(props.assetId) }
  catch { fields.value = [] }
}

async function addField() {
  if (!newKey.value.trim()) return
  try {
    const item = await customFieldsApi.create(props.assetId, {
      field_key: newKey.value.trim(),
      field_value: newVal.value,
      sort_order: fields.value.length,
    })
    fields.value.push(item)
    newKey.value = ''
    newVal.value = ''
    adding.value = false
  } catch (e) { message.error(e.message || '추가 실패') }
}

async function updateField(field) {
  try {
    await customFieldsApi.update(props.assetId, field.id, {
      field_key: field.field_key,
      field_value: field.field_value,
    })
  } catch (e) { message.error(e.message || '수정 실패') }
}

async function removeField(fid) {
  try {
    await customFieldsApi.remove(props.assetId, fid)
    fields.value = fields.value.filter(f => f.id !== fid)
  } catch (e) { message.error(e.message || '삭제 실패') }
}

watch(() => props.assetId, load, { immediate: true })
</script>
