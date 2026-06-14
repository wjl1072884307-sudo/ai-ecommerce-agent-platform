<template>
  <section class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">订单管理</h1>
        <p class="page-subtitle">查看订单、物流状态和售后状态。</p>
      </div>
      <n-button secondary @click="loadOrders">刷新</n-button>
    </div>

    <n-card size="small">
      <n-data-table :columns="columns" :data="orders" :pagination="{ pageSize: 8 }" />
    </n-card>

    <n-drawer v-model:show="showDrawer" :width="480">
      <n-drawer-content title="订单详情">
        <n-descriptions v-if="selected" bordered :column="1" size="small">
          <n-descriptions-item label="订单号">{{ selected.order_no }}</n-descriptions-item>
          <n-descriptions-item label="商品">{{ selected.product?.name }}</n-descriptions-item>
          <n-descriptions-item label="金额">{{ selected.total_amount }}</n-descriptions-item>
          <n-descriptions-item label="订单状态">{{ selected.order_status }}</n-descriptions-item>
          <n-descriptions-item label="支付状态">{{ selected.payment_status }}</n-descriptions-item>
          <n-descriptions-item label="物流状态">{{ selected.logistics_status }}</n-descriptions-item>
          <n-descriptions-item label="物流单号">{{ selected.tracking_no }}</n-descriptions-item>
          <n-descriptions-item label="签收时间">{{ selected.delivered_at || '-' }}</n-descriptions-item>
          <n-descriptions-item label="售后状态">{{ selected.after_sale_status }}</n-descriptions-item>
        </n-descriptions>
      </n-drawer-content>
    </n-drawer>
  </section>
</template>

<script setup lang="ts">
import { h, onMounted, ref } from 'vue'
import type { DataTableColumns } from 'naive-ui'
import { NButton, NCard, NDataTable, NDescriptions, NDescriptionsItem, NDrawer, NDrawerContent, NTag } from 'naive-ui'

import { api, type Order } from '@/api/client'

const orders = ref<Order[]>([])
const selected = ref<Order | null>(null)
const showDrawer = ref(false)

const columns: DataTableColumns<Order> = [
  { title: '订单号', key: 'order_no' },
  { title: '金额', key: 'total_amount' },
  { title: '订单状态', key: 'order_status' },
  { title: '物流', key: 'logistics_status', render: (row) => h(NTag, { size: 'small' }, { default: () => row.logistics_status }) },
  { title: '售后', key: 'after_sale_status' },
  { title: '操作', key: 'actions', render: (row) => h(NButton, { size: 'small', onClick: () => openDetail(row.id) }, { default: () => '详情' }) }
]

async function loadOrders() {
  orders.value = await api.getOrders()
}

async function openDetail(id: number) {
  selected.value = await api.getOrder(id)
  showDrawer.value = true
}

onMounted(loadOrders)
</script>

