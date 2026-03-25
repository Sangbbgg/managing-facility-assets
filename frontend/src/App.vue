<template>
  <n-config-provider :locale="koKR" :date-locale="dateKoKR">
    <n-dialog-provider>
    <n-message-provider>
      <n-layout style="height:100vh">
        <n-layout-header bordered style="height:56px;padding:0 16px;display:flex;align-items:center">
          <span style="font-weight:600;font-size:16px">신인천빛드림본부 설비관리 시스템</span>
        </n-layout-header>
        <n-layout has-sider style="height:calc(100vh - 56px)">
          <AppSidebar />
          <n-layout-content content-style="padding:24px;overflow:auto">
            <router-view />
          </n-layout-content>
        </n-layout>
      </n-layout>
    </n-message-provider>
    </n-dialog-provider>
  </n-config-provider>
</template>

<script setup>
import { koKR, dateKoKR } from 'naive-ui'
import AppSidebar from '@/components/layout/AppSidebar.vue'
</script>
