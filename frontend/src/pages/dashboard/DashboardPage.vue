<template>
  <n-layout style="height: 100vh">
    <n-layout-header bordered style="padding: 16px">
      <n-h2 style="margin: 0">신인천빛드림본부 설비관리 시스템</n-h2>
    </n-layout-header>
    <n-layout-content style="padding: 24px">
      <n-card title="시스템 상태">
        <n-space vertical>
          <n-tag :type="apiStatus === 'ok' ? 'success' : 'error'">
            API 서버: {{ apiStatus === 'ok' ? '정상' : apiStatus === 'loading' ? '확인 중...' : '오류' }}
          </n-tag>
          <n-text depth="3">Phase 0 배포 확인 완료 시 Phase 1(DB 구축)으로 진행합니다.</n-text>
        </n-space>
      </n-card>
    </n-layout-content>
  </n-layout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { NLayout, NLayoutHeader, NLayoutContent, NCard, NSpace, NTag, NText, NH2 } from 'naive-ui'
import axios from 'axios'

const apiStatus = ref('loading')

onMounted(async () => {
  try {
    const res = await axios.get('/api/health')
    apiStatus.value = res.data.status
  } catch {
    apiStatus.value = 'error'
  }
})
</script>
