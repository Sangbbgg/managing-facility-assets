import { createRouter, createWebHistory } from 'vue-router'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/dashboard' },
    { path: '/dashboard',          component: () => import('@/pages/dashboard/DashboardPage.vue') },
    // 자산 관리
    { path: '/assets',             component: () => import('@/pages/assets/AssetListPage.vue') },
    { path: '/assets/register',    component: () => import('@/pages/assets/AssetRegisterPage.vue') },
    { path: '/assets/details',     component: () => import('@/pages/assets/AssetDetailPage.vue') },
    { path: '/assets/new',         component: () => import('@/pages/assets/AssetFormPage.vue') },
    { path: '/assets/:id/edit',    component: () => import('@/pages/assets/AssetFormPage.vue') },
    // 보고서
    { path: '/reports',            component: () => import('@/pages/reports/ReportPage.vue') },
    { path: '/reports/evtx',       component: () => import('@/pages/reports/EvtxUploadPage.vue') },
    { path: '/reports/form-templates', name: 'FormTemplates', component: () => import('@/pages/reports/FormTemplatePage.vue') },
    { path: '/reports/form-report',    name: 'FormReport',    component: () => import('@/pages/reports/FormReportPage.vue') },
    // 기준 정보
    { path: '/settings/locations',      component: () => import('@/pages/settings/LocationTreePage.vue') },
    { path: '/settings/groups',         component: () => import('@/pages/settings/GroupTreePage.vue') },
    { path: '/settings/os',             component: () => import('@/pages/settings/OsCatalogPage.vue') },
    { path: '/settings/av',             component: () => import('@/pages/settings/AvCatalogPage.vue') },
    { path: '/settings/persons',        component: () => import('@/pages/settings/PersonPage.vue') },
    { path: '/settings/departments',    component: () => import('@/pages/settings/DepartmentPage.vue') },
    { path: '/settings/equipment-types', component: () => import('@/pages/settings/EquipmentTypePage.vue') },
    { path: '/settings/db',              component: () => import('@/pages/settings/DbViewerPage.vue') },
  ],
})
