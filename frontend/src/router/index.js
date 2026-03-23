import { createRouter, createWebHistory } from 'vue-router'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/dashboard' },
    { path: '/dashboard', component: () => import('@/pages/dashboard/DashboardPage.vue') },
    { path: '/assets', component: () => import('@/pages/assets/AssetListPage.vue') },
    { path: '/assets/new', component: () => import('@/pages/assets/AssetFormPage.vue') },
    { path: '/assets/:id/edit', component: () => import('@/pages/assets/AssetFormPage.vue') },
    { path: '/reports', component: () => import('@/pages/reports/ReportPage.vue') },
    { path: '/reports/evtx', component: () => import('@/pages/reports/EvtxUploadPage.vue') },
    { path: '/settings/locations', component: () => import('@/pages/settings/LocationTreePage.vue') },
    { path: '/settings/groups', component: () => import('@/pages/settings/GroupTreePage.vue') },
    { path: '/settings/os', component: () => import('@/pages/settings/OsCatalogPage.vue') },
    { path: '/settings/av', component: () => import('@/pages/settings/AvCatalogPage.vue') },
    { path: '/settings/persons', component: () => import('@/pages/settings/PersonPage.vue') },
    { path: '/settings/departments', component: () => import('@/pages/settings/DepartmentPage.vue') },
    { path: '/settings/equipment-types', component: () => import('@/pages/settings/EquipmentTypePage.vue') },
  ],
})
