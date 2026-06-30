import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

import { api } from '@/api/client'
import { canAccess, clearSession, isAuthenticated, setCurrentUser, user, type UserRole } from '@/auth/session'
import AdminLayout from '@/layouts/AdminLayout.vue'
import AgentLogsView from '@/views/AgentLogsView.vue'
import DashboardView from '@/views/DashboardView.vue'
import KnowledgeView from '@/views/KnowledgeView.vue'
import LoginView from '@/views/LoginView.vue'
import OrdersView from '@/views/OrdersView.vue'
import ProductsView from '@/views/ProductsView.vue'
import ReviewTasksView from '@/views/ReviewTasksView.vue'
import SessionsView from '@/views/SessionsView.vue'
import TicketsView from '@/views/TicketsView.vue'

export const routes: RouteRecordRaw[] = [
  { path: '/login', name: 'login', component: LoginView, meta: { public: true, title: 'Login' } },
  {
    path: '/',
    component: AdminLayout,
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', name: 'dashboard', component: DashboardView, meta: { title: 'Dashboard', roles: ['admin', 'reviewer', 'agent', 'viewer'] } },
      { path: 'products', name: 'products', component: ProductsView, meta: { title: 'Products', roles: ['admin', 'reviewer', 'agent', 'viewer'] } },
      { path: 'orders', name: 'orders', component: OrdersView, meta: { title: 'Orders', roles: ['admin', 'reviewer', 'agent', 'viewer'] } },
      { path: 'sessions', name: 'sessions', component: SessionsView, meta: { title: 'Sessions', roles: ['admin', 'agent'] } },
      { path: 'knowledge', name: 'knowledge', component: KnowledgeView, meta: { title: 'Knowledge', roles: ['admin', 'reviewer', 'agent', 'viewer'] } },
      { path: 'review-tasks', name: 'review-tasks', component: ReviewTasksView, meta: { title: 'Review Tasks', roles: ['admin', 'reviewer'] } },
      { path: 'tickets', name: 'tickets', component: TicketsView, meta: { title: 'Tickets', roles: ['admin', 'reviewer', 'agent', 'viewer'] } },
      { path: 'agent-logs', name: 'agent-logs', component: AgentLogsView, meta: { title: 'Agent Logs', roles: ['admin', 'reviewer', 'agent', 'viewer'] } }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to) => {
  if (to.meta.public) {
    if (to.name === 'login' && isAuthenticated.value) return '/dashboard'
    return true
  }

  if (!isAuthenticated.value) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  try {
    if (!user.value) {
      setCurrentUser(await api.getCurrentUser())
    }
  } catch {
    clearSession()
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  const roles = to.meta.roles as UserRole[] | undefined
  if (!canAccess(roles)) return '/dashboard'
  return true
})

export default router
