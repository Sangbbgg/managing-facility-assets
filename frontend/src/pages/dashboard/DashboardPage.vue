<template>
  <div>
    <n-card title="시스템 상태">
      <n-space vertical>
        <n-tag :type="apiStatus === 'ok' ? 'success' : 'error'">
          API 서버: {{ apiStatus === 'ok' ? '정상' : apiStatus === 'loading' ? '확인 중...' : '오류' }}
        </n-tag>
        <n-text depth="3">설비관리 시스템이 정상 운영 중입니다.</n-text>
      </n-space>
    </n-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import client from '@/api/client'

const apiStatus = ref('loading')

onMounted(async () => {
  try {
    const res = await client.get('/api/health')
    apiStatus.value = res.data.status
  } catch {
    apiStatus.value = 'error'
  }
})
</script>
