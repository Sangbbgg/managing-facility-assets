import { createRouter, createWebHistory } from 'vue-router'
import DashboardPage from '../pages/dashboard/DashboardPage.vue'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', component: DashboardPage },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
