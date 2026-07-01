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
          <strong>{{ t('brand.name') }}</strong>
          <span>{{ t('brand.subtitle') }}</span>
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
            {{ t('common.api') }} {{ statusLabel(healthStatus) }}
          </n-tag>
          <n-select v-model:value="selectedLocale" size="small" class="language-select" :options="languageOptions" @update:value="switchLanguage" />
          <n-tag size="small">{{ currentUser?.role || 'unknown' }}</n-tag>
          <n-button size="small" secondary @click="logout">{{ t('common.logout') }}</n-button>
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
import { NButton, NLayout, NLayoutContent, NLayoutHeader, NLayoutSider, NMenu, NSelect, NTag } from 'naive-ui'
import { useI18n } from 'vue-i18n'

import { getHealth } from '@/api/client'
import { clearSession, role, user, type UserRole } from '@/auth/session'
import { useDisplayText } from '@/i18n/display'
import type { Locale } from '@/i18n/messages'

type RoleMenuOption = MenuOption & { roles: UserRole[] }

const route = useRoute()
const router = useRouter()
const { t, locale } = useI18n()
const { statusLabel } = useDisplayText()
const healthStatus = ref('checking')
const selectedLocale = ref(locale.value as Locale)

const menuOptions = computed<RoleMenuOption[]>(() => [
  { label: () => h(RouterLink, { to: '/dashboard' }, { default: () => t('nav.dashboard') }), key: 'dashboard', roles: ['admin', 'reviewer', 'agent', 'viewer'] },
  { label: () => h(RouterLink, { to: '/products' }, { default: () => t('nav.products') }), key: 'products', roles: ['admin', 'reviewer', 'agent', 'viewer'] },
  { label: () => h(RouterLink, { to: '/orders' }, { default: () => t('nav.orders') }), key: 'orders', roles: ['admin', 'reviewer', 'agent', 'viewer'] },
  { label: () => h(RouterLink, { to: '/sessions' }, { default: () => t('nav.sessions') }), key: 'sessions', roles: ['admin', 'agent'] },
  { label: () => h(RouterLink, { to: '/knowledge' }, { default: () => t('nav.knowledge') }), key: 'knowledge', roles: ['admin', 'reviewer', 'agent', 'viewer'] },
  { label: () => h(RouterLink, { to: '/review-tasks' }, { default: () => t('nav.reviews') }), key: 'review-tasks', roles: ['admin', 'reviewer'] },
  { label: () => h(RouterLink, { to: '/tickets' }, { default: () => t('nav.tickets') }), key: 'tickets', roles: ['admin', 'reviewer', 'agent', 'viewer'] },
  { label: () => h(RouterLink, { to: '/agent-logs' }, { default: () => t('nav.agentLogs') }), key: 'agent-logs', roles: ['admin', 'reviewer', 'agent', 'viewer'] }
])

const routeTitleMap: Record<string, string> = {
  dashboard: 'nav.dashboard',
  products: 'nav.products',
  orders: 'nav.orders',
  sessions: 'nav.sessions',
  knowledge: 'nav.knowledge',
  'review-tasks': 'nav.reviews',
  tickets: 'nav.tickets',
  'agent-logs': 'nav.agentLogs'
}

const languageOptions = [
  { label: 'English', value: 'en' },
  { label: '中文', value: 'zh' }
]

const activeKey = computed(() => String(route.name ?? 'dashboard'))
const currentTitle = computed(() => t(routeTitleMap[activeKey.value] ?? 'nav.dashboard'))
const currentUser = computed(() => user.value)
const visibleMenuOptions = computed(() => menuOptions.value.filter((item) => role.value && item.roles.includes(role.value)))

function handleMenuSelect(key: string) {
  router.push({ name: key })
}

function logout() {
  clearSession()
  router.replace('/login')
}

function switchLanguage(value: Locale) {
  locale.value = value
  selectedLocale.value = value
  localStorage.setItem('locale', value)
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

.language-select {
  width: 116px;
}

.admin-content {
  min-height: calc(100vh - 64px);
  padding: 24px;
  background: #f4f6f8;
}
</style>
