<template>
  <n-layout style="min-height: 100vh">
    <n-layout-header bordered style="padding: 16px 24px; display: flex; align-items: center; gap: 16px">
      <n-button text @click="router.back()">
        <n-icon size="20"><ArrowBackOutline /></n-icon>
      </n-button>
      <n-h3 style="margin: 0">{{ title }}</n-h3>
    </n-layout-header>
    <n-layout-content style="padding: 24px">
      <slot />
    </n-layout-content>
  </n-layout>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { NLayout, NLayoutHeader, NLayoutContent, NH3, NButton, NIcon } from 'naive-ui'
import { ArrowBackOutline } from '@vicons/ionicons5'

defineProps({ title: String })
const router = useRouter()
</script>
