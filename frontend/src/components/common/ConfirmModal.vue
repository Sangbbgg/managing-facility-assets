<template>
  <n-modal
    :show="show"
    preset="dialog"
    :title="title"
    :type="danger ? 'error' : 'warning'"
    :positive-text="'확인'"
    :negative-text="'취소'"
    @positive-click="$emit('confirm')"
    @negative-click="$emit('update:show', false)"
    @update:show="$emit('update:show', $event)"
  >
    {{ message }}
  </n-modal>
</template>

<script setup>
defineProps({
  show:    { type: Boolean, required: true },
  title:   { type: String,  default: '확인' },
  message: { type: String,  default: '계속하시겠습니까?' },
  danger:  { type: Boolean, default: false },
})
defineEmits(['update:show', 'confirm'])
</script>
