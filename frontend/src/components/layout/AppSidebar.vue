<template>
  <n-layout-sider
    bordered
    collapse-mode="width"
    :collapsed-width="64"
    :width="220"
    :collapsed="collapsed"
    show-trigger
    @collapse="collapsed = true"
    @expand="collapsed = false"
  >
    <n-menu
      :collapsed="collapsed"
      :collapsed-width="64"
      :collapsed-icon-size="22"
      :options="menuOptions"
      :value="activeKey"
      @update:value="handleSelect"
    />
  </n-layout-sider>
</template>

<script setup>
import { ref, computed, h } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { NIcon } from 'naive-ui'
import {
  HomeOutline,
  ServerOutline,
  AddCircleOutline,
  ListOutline,
  DocumentTextOutline,
  CloudUploadOutline,
  LocationOutline,
  GitNetworkOutline,
  DesktopOutline,
  ShieldCheckmarkOutline,
  PeopleOutline,
  BusinessOutline,
  HardwareChipOutline,
  GridOutline,
} from '@vicons/ionicons5'

const router = useRouter()
const route = useRoute()
const collapsed = ref(false)

const activeKey = computed(() => route.path)

function icon(component) {
  return () => h(NIcon, null, { default: () => h(component) })
}

const menuOptions = [
  { label: '대시보드', key: '/dashboard', icon: icon(HomeOutline) },
  {
    label: '자산 관리',
    key: 'assets',
    icon: icon(ServerOutline),
    children: [
      { label: '자산 현황',   key: '/assets',          icon: icon(ListOutline) },
      { label: '자산 등록',   key: '/assets/register', icon: icon(AddCircleOutline) },
      { label: '자산 세부사항', key: '/assets/details', icon: icon(ServerOutline) },
    ],
  },
  {
    label: '보고서',
    key: 'reports',
    icon: icon(DocumentTextOutline),
    children: [
      { label: '보고서 생성',  key: '/reports',                 icon: icon(DocumentTextOutline) },
      { label: 'EVTX 업로드', key: '/reports/evtx',             icon: icon(CloudUploadOutline) },
      { label: '양식 관리',   key: '/reports/form-templates',   icon: icon(DocumentTextOutline) },
      { label: '양식 보고서', key: '/reports/form-report',      icon: icon(DocumentTextOutline) },
    ],
  },
  {
    label: '기준 정보',
    key: 'settings',
    icon: icon(BusinessOutline),
    children: [
      { label: '위치 관리', key: '/settings/locations', icon: icon(LocationOutline) },
      { label: '그룹 관리', key: '/settings/groups', icon: icon(GitNetworkOutline) },
      { label: 'OS 카탈로그', key: '/settings/os', icon: icon(DesktopOutline) },
      { label: '백신 카탈로그', key: '/settings/av', icon: icon(ShieldCheckmarkOutline) },
      { label: '장비 종류', key: '/settings/equipment-types', icon: icon(HardwareChipOutline) },
      { label: '담당자', key: '/settings/persons', icon: icon(PeopleOutline) },
      { label: '부서', key: '/settings/departments', icon: icon(BusinessOutline) },
      { label: 'PostgreSQL DB', key: '/settings/db', icon: icon(GridOutline) },
    ],
  },
]

function handleSelect(key) {
  router.push(key)
}
</script>
