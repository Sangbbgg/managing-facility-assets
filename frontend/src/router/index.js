import { createRouter, createWebHistory } from 'vue-router'
import DashboardPage from '../pages/dashboard/DashboardPage.vue'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', component: DashboardPage },
  {
    path: '/reports',
    component: () => import('@/pages/reports/ReportPage.vue'),
  },
  {
    path: '/reports/evtx',
    component: () => import('@/pages/reports/EvtxUploadPage.vue'),
  },
  {
    path: '/reports/form-templates',
    name: 'FormTemplates',
    component: () => import('@/pages/reports/FormTemplatePage.vue'),
  },
  {
    path: '/reports/form-report',
    name: 'FormReport',
    component: () => import('@/pages/reports/FormReportPage.vue'),
  },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
