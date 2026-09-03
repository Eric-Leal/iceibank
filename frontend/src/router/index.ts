import { createRouter, createWebHistory } from 'vue-router'

import { useAuthStore } from '@/stores/auth'
import ContaView from '@/views/ContaView.vue'
import LoginView from '@/views/LoginView.vue'
import TransferenciaView from '@/views/TransferenciaView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/conta' },
    { path: '/login', name: 'login', component: LoginView },
    { path: '/conta', name: 'conta', component: ContaView, meta: { exigeLogin: true } },
    {
      path: '/transferencia',
      name: 'transferencia',
      component: TransferenciaView,
      meta: { exigeLogin: true },
    },
  ],
})

// Impede acesso as telas internas sem token.
router.beforeEach((para) => {
  if (para.meta.exigeLogin && !useAuthStore().autenticado) {
    return { name: 'login' }
  }
})

export default router
