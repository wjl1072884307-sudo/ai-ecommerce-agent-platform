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
          <strong>电商客服 Agent</strong>
          <span>After-sales Console</span>
        </div>
      </div>
      <n-menu :value="activeKey" :options="menuOptions" @update:value="handleMenuSelect" />
    </n-layout-sider>

    <n-layout>
      <n-layout-header bordered class="admin-header">
        <div>
          <div class="header-title">{{ currentTitle }}</div>
          <div class="header-meta">Mock 数据环境 · FastAPI + Vue3</div>
        </div>
        <n-tag :type="healthStatus === 'ok' ? 'success' : 'warning'" size="small">
          API {{ healthStatus }}
        </n-tag>
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
import { NLayout, NLayoutContent, NLayoutHeader, NLayoutSider, NMenu, NTag } from 'naive-ui'

import { getHealth } from '@/api/client'

const route = useRoute()
const router = useRouter()
const healthStatus = ref('checking')

const menuOptions: MenuOption[] = [
  { label: () => h(RouterLink, { to: '/dashboard' }, { default: () => 'Dashboard' }), key: 'dashboard' },
  { label: () => h(RouterLink, { to: '/products' }, { default: () => '商品管理' }), key: 'products' },
  { label: () => h(RouterLink, { to: '/orders' }, { default: () => '订单管理' }), key: 'orders' },
  { label: () => h(RouterLink, { to: '/sessions' }, { default: () => '客服会话' }), key: 'sessions' },
  { label: () => h(RouterLink, { to: '/knowledge' }, { default: () => '知识库管理' }), key: 'knowledge' },
  { label: () => h(RouterLink, { to: '/review-tasks' }, { default: () => '人工审核' }), key: 'review-tasks' },
  { label: () => h(RouterLink, { to: '/tickets' }, { default: () => '售后工单' }), key: 'tickets' },
  { label: () => h(RouterLink, { to: '/agent-logs' }, { default: () => 'Agent 运行日志' }), key: 'agent-logs' }
]

const activeKey = computed(() => String(route.name ?? 'dashboard'))
const currentTitle = computed(() => String(route.meta.title ?? 'Dashboard'))

function handleMenuSelect(key: string) {
  router.push({ name: key })
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

.admin-content {
  min-height: calc(100vh - 64px);
  padding: 24px;
  background: #f4f6f8;
}
</style>

