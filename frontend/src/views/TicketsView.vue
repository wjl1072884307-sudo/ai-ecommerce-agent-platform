<template>
  <section class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">售后工单</h1>
        <p class="page-subtitle">跟踪退货、退款、投诉等售后事项。</p>
      </div>
      <n-button secondary @click="loadTickets">刷新</n-button>
    </div>

    <n-card size="small">
      <n-data-table :columns="columns" :data="tickets" :pagination="{ pageSize: 8 }" />
    </n-card>

    <n-drawer v-model:show="showDrawer" :width="460">
      <n-drawer-content title="工单详情">
        <n-space v-if="selected" vertical>
          <n-descriptions bordered :column="1" size="small">
            <n-descriptions-item label="工单号">{{ selected.ticket_no }}</n-descriptions-item>
            <n-descriptions-item label="类型">{{ selected.ticket_type }}</n-descriptions-item>
            <n-descriptions-item label="订单">{{ selected.order_id }}</n-descriptions-item>
            <n-descriptions-item label="优先级">{{ selected.priority }}</n-descriptions-item>
            <n-descriptions-item label="状态">{{ selected.status }}</n-descriptions-item>
            <n-descriptions-item label="描述">{{ selected.description }}</n-descriptions-item>
          </n-descriptions>
          <n-select v-model:value="nextStatus" :options="statusOptions" />
          <n-input v-model:value="resolution" type="textarea" placeholder="处理备注" />
          <n-button type="primary" @click="updateStatus">更新状态</n-button>
        </n-space>
      </n-drawer-content>
    </n-drawer>
  </section>
</template>

<script setup lang="ts">
import { h, onMounted, ref } from 'vue'
import type { DataTableColumns } from 'naive-ui'
import { NButton, NCard, NDataTable, NDescriptions, NDescriptionsItem, NDrawer, NDrawerContent, NInput, NSelect, NSpace, NTag, useMessage } from 'naive-ui'

import { api, type Ticket } from '@/api/client'

const message = useMessage()
const tickets = ref<Ticket[]>([])
const selected = ref<Ticket | null>(null)
const showDrawer = ref(false)
const nextStatus = ref('processing')
const resolution = ref('已进入售后处理。')

const statusOptions = [
  { label: 'open', value: 'open' },
  { label: 'processing', value: 'processing' },
  { label: 'resolved', value: 'resolved' },
  { label: 'closed', value: 'closed' }
]

const columns: DataTableColumns<Ticket> = [
  { title: '工单号', key: 'ticket_no' },
  { title: '类型', key: 'ticket_type' },
  { title: '订单', key: 'order_id' },
  { title: '优先级', key: 'priority' },
  { title: '状态', key: 'status', render: (row) => h(NTag, { size: 'small' }, { default: () => row.status }) },
  { title: '操作', key: 'actions', render: (row) => h(NButton, { size: 'small', onClick: () => openDetail(row) }, { default: () => '处理' }) }
]

async function loadTickets() {
  tickets.value = await api.getTickets()
}

function openDetail(row: Ticket) {
  selected.value = row
  nextStatus.value = row.status === 'open' ? 'processing' : row.status
  showDrawer.value = true
}

async function updateStatus() {
  if (!selected.value) return
  selected.value = await api.updateTicketStatus(selected.value.id, nextStatus.value, resolution.value)
  await loadTickets()
  message.success('工单状态已更新')
}

onMounted(loadTickets)
</script>

