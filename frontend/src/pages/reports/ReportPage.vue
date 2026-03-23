<template>
  <PageShell title="보고서 생성">
    <n-card style="max-width:560px">
      <n-form label-placement="left" label-width="120">
        <n-form-item label="보고서 종류">
          <n-select v-model:value="reportType" :options="reportOptions" />
        </n-form-item>
        <n-form-item label="시작일">
          <n-date-picker v-model:value="dateFrom" type="date" style="width:100%" />
        </n-form-item>
        <n-form-item label="종료일">
          <n-date-picker v-model:value="dateTo" type="date" style="width:100%" />
        </n-form-item>
      </n-form>
      <n-button
        type="primary"
        :loading="loading"
        :disabled="!reportType || !dateFrom || !dateTo"
        @click="generate"
        style="margin-top:8px"
      >
        보고서 생성
      </n-button>
    </n-card>
  </PageShell>
</template>

<script setup>
import { ref } from 'vue'
import { useMessage } from 'naive-ui'
import PageShell from '@/components/common/PageShell.vue'
import client from '@/api/client'

const message = useMessage()
const reportType = ref(null)
const dateFrom = ref(null)
const dateTo = ref(null)
const loading = ref(false)

const reportOptions = [
  { label: '형상관리대장',    value: '형상관리대장' },
  { label: '설비관리대장',    value: '설비관리대장' },
  { label: '예방점검 월간',   value: '예방점검_월간' },
  { label: '예방점검 분기',   value: '예방점검_분기' },
  { label: '이벤트로그',      value: '이벤트로그' },
  { label: '콘솔접속대장',    value: '콘솔접속대장' },
  { label: '봉인지관리대장',  value: '봉인지관리대장' },
  { label: '비밀번호관리대장', value: '비밀번호관리대장' },
]

function toDateStr(ts) {
  const d = new Date(ts)
  const yyyy = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd}`
}

async function generate() {
  if (!reportType.value || !dateFrom.value || !dateTo.value) return
  loading.value = true
  try {
    const params = new URLSearchParams({
      report_type: reportType.value,
      date_from: toDateStr(dateFrom.value),
      date_to: toDateStr(dateTo.value),
    })
    const res = await client.post(`/api/reports/generate?${params}`, null, {
      responseType: 'blob',
      timeout: 60000,
    })
    const url = URL.createObjectURL(new Blob([res.data]))
    const a = document.createElement('a')
    a.href = url
    a.download = `${reportType.value}_${toDateStr(dateFrom.value)}_${toDateStr(dateTo.value)}.xlsx`
    a.click()
    URL.revokeObjectURL(url)
    message.success('보고서가 다운로드되었습니다')
  } catch (e) {
    message.error(e.message || '보고서 생성 실패')
  } finally {
    loading.value = false
  }
}
</script>
