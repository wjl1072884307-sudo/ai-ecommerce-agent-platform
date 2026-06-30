<template>
  <section class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Tickets</h1>
        <p class="page-subtitle">Track return, refund, complaint, and after-sales workflows.</p>
      </div>
      <n-button secondary @click="loadTickets">Refresh</n-button>
    </div>

    <n-card size="small">
      <n-data-table :columns="columns" :data="tickets" :pagination="{ pageSize: 8 }" />
    </n-card>

    <n-drawer v-model:show="showDrawer" :width="560">
      <n-drawer-content title="Ticket detail">
        <n-space v-if="selected" vertical>
          <n-descriptions bordered :column="1" size="small">
            <n-descriptions-item label="Ticket No">{{ selected.ticket_no }}</n-descriptions-item>
            <n-descriptions-item label="Type">{{ selected.ticket_type }}</n-descriptions-item>
            <n-descriptions-item label="Order">{{ selected.order_id || '-' }}</n-descriptions-item>
            <n-descriptions-item label="Priority">{{ selected.priority }}</n-descriptions-item>
            <n-descriptions-item label="Status">{{ selected.status }}</n-descriptions-item>
            <n-descriptions-item label="Assignee">{{ selected.assignee_id || '-' }}</n-descriptions-item>
            <n-descriptions-item label="Description">{{ selected.description }}</n-descriptions-item>
          </n-descriptions>

          <template v-if="canHandleTickets">
            <n-space>
              <n-button secondary @click="claimSelected">Claim</n-button>
              <n-select v-model:value="nextStatus" :options="statusOptions" class="status-select" />
            </n-space>
            <n-input v-model:value="reason" placeholder="Status change reason" />
            <n-input v-model:value="resolution" type="textarea" placeholder="Resolution" />
            <n-button type="primary" @click="updateStatus">Update Status</n-button>
          </template>

          <n-card title="Status Timeline" size="small">
            <n-empty v-if="!statusLogs.length" description="No status changes yet" />
            <n-timeline v-else>
              <n-timeline-item
                v-for="item in statusLogs"
                :key="item.id"
                :title="`${item.from_status} -> ${item.to_status}`"
                :content="item.reason"
                :time="formatTime(item.created_at)"
              />
            </n-timeline>
          </n-card>
        </n-space>
      </n-drawer-content>
    </n-drawer>
  </section>
</template>

<script setup lang="ts">
import { computed, h, onMounted, ref } from 'vue'
import type { DataTableColumns } from 'naive-ui'
import { NButton, NCard, NDataTable, NDescriptions, NDescriptionsItem, NDrawer, NDrawerContent, NEmpty, NInput, NSelect, NSpace, NTag, NTimeline, NTimelineItem, useMessage } from 'naive-ui'

import { api, type Ticket, type TicketStatusLog } from '@/api/client'
import { role } from '@/auth/session'

const message = useMessage()
const tickets = ref<Ticket[]>([])
const selected = ref<Ticket | null>(null)
const statusLogs = ref<TicketStatusLog[]>([])
const showDrawer = ref(false)
const nextStatus = ref('processing')
const reason = ref('Start after-sales handling')
const resolution = ref('')
const canHandleTickets = computed(() => role.value === 'admin' || role.value === 'reviewer' || role.value === 'agent')

const statusOptions = [
  { label: 'pending', value: 'pending' },
  { label: 'processing', value: 'processing' },
  { label: 'resolved', value: 'resolved' },
  { label: 'closed', value: 'closed' },
  { label: 'cancelled', value: 'cancelled' }
]

const columns: DataTableColumns<Ticket> = [
  { title: 'Ticket No', key: 'ticket_no' },
  { title: 'Type', key: 'ticket_type' },
  { title: 'Order', key: 'order_id' },
  { title: 'Priority', key: 'priority' },
  { title: 'Status', key: 'status', render: (row) => h(NTag, { size: 'small' }, { default: () => row.status }) },
  { title: 'Actions', key: 'actions', render: (row) => h(NButton, { size: 'small', onClick: () => openDetail(row) }, { default: () => canHandleTickets.value ? 'Handle' : 'View' }) }
]

async function loadTickets() {
  tickets.value = await api.getTickets()
}

async function openDetail(row: Ticket) {
  selected.value = row
  nextStatus.value = row.status === 'pending' ? 'processing' : row.status
  resolution.value = row.resolution || ''
  showDrawer.value = true
  statusLogs.value = await api.getTicketStatusLogs(row.id)
}

async function claimSelected() {
  if (!selected.value) return
  selected.value = await api.claimTicket(selected.value.id)
  statusLogs.value = await api.getTicketStatusLogs(selected.value.id)
  await loadTickets()
  message.success('Ticket claimed')
}

async function updateStatus() {
  if (!selected.value) return
  selected.value = await api.updateTicketStatus(selected.value.id, nextStatus.value, reason.value, resolution.value || undefined)
  statusLogs.value = await api.getTicketStatusLogs(selected.value.id)
  await loadTickets()
  message.success('Ticket status updated')
}

function formatTime(value: string) {
  return new Date(value).toLocaleString()
}

onMounted(loadTickets)
</script>

<style scoped>
.status-select {
  width: 180px;
}
</style>
