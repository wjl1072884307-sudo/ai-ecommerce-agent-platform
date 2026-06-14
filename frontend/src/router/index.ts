import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

import AdminLayout from '@/layouts/AdminLayout.vue'
import AgentLogsView from '@/views/AgentLogsView.vue'
import DashboardView from '@/views/DashboardView.vue'
import KnowledgeView from '@/views/KnowledgeView.vue'
import OrdersView from '@/views/OrdersView.vue'
import ProductsView from '@/views/ProductsView.vue'
import ReviewTasksView from '@/views/ReviewTasksView.vue'
import SessionsView from '@/views/SessionsView.vue'
import TicketsView from '@/views/TicketsView.vue'

export const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: AdminLayout,
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', name: 'dashboard', component: DashboardView, meta: { title: 'Dashboard' } },
      { path: 'products', name: 'products', component: ProductsView, meta: { title: '商品管理' } },
      { path: 'orders', name: 'orders', component: OrdersView, meta: { title: '订单管理' } },
      { path: 'sessions', name: 'sessions', component: SessionsView, meta: { title: '客服会话' } },
      { path: 'knowledge', name: 'knowledge', component: KnowledgeView, meta: { title: '知识库管理' } },
      { path: 'review-tasks', name: 'review-tasks', component: ReviewTasksView, meta: { title: '人工审核' } },
      { path: 'tickets', name: 'tickets', component: TicketsView, meta: { title: '售后工单' } },
      { path: 'agent-logs', name: 'agent-logs', component: AgentLogsView, meta: { title: 'Agent 运行日志' } }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

