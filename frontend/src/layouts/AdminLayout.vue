<template>
  <n-layout class="admin-shell" has-sider>
    <n-layout-sider
      bordered
      collapse-mode="width"
      :collapsed-width="64"
      :width="236"
      :native-scrollbar="false"
      class="admin-sider"
    >
      <div class="brand">
        <div class="brand-mark">AI</div>
        <div class="brand-text">
          <strong>Ecommerce Agent</strong>
          <span>After-sales Console</span>
        </div>
      </div>
      <n-menu :value="activeKey" :options="visibleMenuOptions" @update:value="handleMenuSelect" />
    </n-layout-sider>

    <n-layout>
      <n-layout-header bordered class="admin-header">
        <div>
          <div class="header-title">{{ currentTitle }}</div>
          <div class="header-meta">{{ currentUser?.display_name || currentUser?.username }}</div>
        </div>
        <div class="header-actions">
          <n-tag :type="healthStatus === 'ok' ? 'success' : 'warning'" size="small">
            API {{ healthStatus }}
          </n-tag>
          <n-tag size="small">{{ currentUser?.role || 'unknown' }}</n-tag>
          <n-button size="small" secondary @click="logout">Logout</n-button>
        </div>
      </n-layout-header>
      <n-layout-content class="admin-content">
        <RouterView />
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>

<script setup lang="ts">
import { computed, h, onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import type { MenuOption } from 'naive-ui'
import { NButton, NLayout, NLayoutContent, NLayoutHeader, NLayoutSider, NMenu, NTag } from 'naive-ui'

import { getHealth } from '@/api/client'
import { clearSession, role, user, type UserRole } from '@/auth/session'

type RoleMenuOption = MenuOption & { roles: UserRole[] }

const route = useRoute()
const router = useRouter()
const healthStatus = ref('checking')

const menuOptions: RoleMenuOption[] = [
  { label: () => h(RouterLink, { to: '/dashboard' }, { default: () => 'Dashboard' }), key: 'dashboard', roles: ['admin', 'reviewer', 'agent', 'viewer'] },
  { label: () => h(RouterLink, { to: '/products' }, { default: () => 'Products' }), key: 'products', roles: ['admin', 'reviewer', 'agent', 'viewer'] },
  { label: () => h(RouterLink, { to: '/orders' }, { default: () => 'Orders' }), key: 'orders', roles: ['admin', 'reviewer', 'agent', 'viewer'] },
  { label: () => h(RouterLink, { to: '/sessions' }, { default: () => 'Sessions' }), key: 'sessions', roles: ['admin', 'agent'] },
  { label: () => h(RouterLink, { to: '/knowledge' }, { default: () => 'Knowledge' }), key: 'knowledge', roles: ['admin', 'reviewer', 'agent', 'viewer'] },
  { label: () => h(RouterLink, { to: '/review-tasks' }, { default: () => 'Reviews' }), key: 'review-tasks', roles: ['admin', 'reviewer'] },
  { label: () => h(RouterLink, { to: '/tickets' }, { default: () => 'Tickets' }), key: 'tickets', roles: ['admin', 'reviewer', 'agent', 'viewer'] },
  { label: () => h(RouterLink, { to: '/agent-logs' }, { default: () => 'Agent Logs' }), key: 'agent-logs', roles: ['admin', 'reviewer', 'agent', 'viewer'] }
]

const activeKey = computed(() => String(route.name ?? 'dashboard'))
const currentTitle = computed(() => String(route.meta.title ?? 'Dashboard'))
const currentUser = computed(() => user.value)
const visibleMenuOptions = computed(() => menuOptions.filter((item) => role.value && item.roles.includes(role.value)))

function handleMenuSelect(key: string) {
  router.push({ name: key })
}

function logout() {
  clearSession()
  router.replace('/login')
}

onMounted(async () => {
  try {
    const health = await getHealth()
    healthStatus.value = health.status
  } catch {
    healthStatus.value = 'error'
  }
})
</script>

<style scoped>
.admin-shell {
  min-height: 100vh;
}

.admin-sider {
  background: #ffffff;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  height: 64px;
  padding: 0 18px;
}

.brand-mark {
  display: grid;
  width: 34px;
  height: 34px;
  place-items: center;
  border-radius: 8px;
  background: #1f2328;
  color: #ffffff;
  font-size: 13px;
  font-weight: 700;
}

.brand-text {
  display: flex;
  min-width: 0;
  flex-direction: column;
  line-height: 1.25;
}

.brand-text strong {
  font-size: 14px;
}

.brand-text span {
  color: #667085;
  font-size: 12px;
}

.admin-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  padding: 0 24px;
  background: #ffffff;
}

.header-title {
  font-size: 17px;
  font-weight: 700;
}

.header-meta {
  margin-top: 3px;
  color: #667085;
  font-size: 12px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.admin-content {
  min-height: calc(100vh - 64px);
  padding: 24px;
  background: #f4f6f8;
}
</style>
