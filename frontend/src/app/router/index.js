import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'studio',
    component: () => import('../../pages/StudioPage.vue')
  },
  {
    path: '/history',
    name: 'history',
    component: () => import('../../pages/HistoryPage.vue')
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('../../pages/SettingsPage.vue')
  }
]

export const router = createRouter({
  history: createWebHistory(),
  routes
})
