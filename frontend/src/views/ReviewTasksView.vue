<template>
  <section class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Review Tasks</h1>
        <p class="page-subtitle">Handle high-risk Agent replies that require manual approval.</p>
      </div>
      <n-button secondary @click="loadTasks">Refresh</n-button>
    </div>

    <n-card size="small">
      <n-data-table :columns="columns" :data="tasks" :pagination="{ pageSize: 8 }" />
    </n-card>

    <n-drawer v-model:show="showDrawer" :width="480">
      <n-drawer-content title="Review detail">
        <n-space v-if="selected" vertical>
          <n-descriptions bordered :column="1" size="small">
            <n-descriptions-item label="Title">{{ selected.title }}</n-descriptions-item>
            <n-descriptions-item label="Risk">{{ selected.risk_level }}</n-descriptions-item>
            <n-descriptions-item label="Reason">{{ selected.risk_reason || '-' }}</n-descriptions-item>
            <n-descriptions-item label="Status">{{ selected.status }}</n-descriptions-item>
          </n-descriptions>
          <template v-if="canReview">
            <n-input v-model:value="comment" type="textarea" placeholder="Review comment" />
            <n-space>
              <n-button type="primary" @click="approve">Approve</n-button>
              <n-button type="error" secondary @click="reject">Reject</n-button>
            </n-space>
          </template>
        </n-space>
      </n-drawer-content>
    </n-drawer>
  </section>
</template>

<script setup lang="ts">
import { computed, h, onMounted, ref } from 'vue'
import type { DataTableColumns } from 'naive-ui'
import { NButton, NCard, NDataTable, NDescriptions, NDescriptionsItem, NDrawer, NDrawerContent, NInput, NSpace, NTag, useMessage } from 'naive-ui'

import { api, type ReviewTask } from '@/api/client'
import { role } from '@/auth/session'

const message = useMessage()
const tasks = ref<ReviewTask[]>([])
const selected = ref<ReviewTask | null>(null)
const showDrawer = ref(false)
const comment = ref('Approved after manual review.')
const canReview = computed(() => role.value === 'admin' || role.value === 'reviewer')

const columns: DataTableColumns<ReviewTask> = [
  { title: 'ID', key: 'id', width: 70 },
  { title: 'Title', key: 'title' },
  { title: 'Risk', key: 'risk_level', render: (row) => h(NTag, { type: row.risk_level === 'high' ? 'error' : 'warning', size: 'small' }, { default: () => row.risk_level }) },
  { title: 'Status', key: 'status' },
  { title: 'Reason', key: 'risk_reason' },
  { title: 'Actions', key: 'actions', render: (row) => h(NButton, { size: 'small', onClick: () => openDetail(row) }, { default: () => canReview.value ? 'Review' : 'View' }) }
]

async function loadTasks() {
  tasks.value = await api.getReviewTasks()
}

function openDetail(row: ReviewTask) {
  selected.value = row
  showDrawer.value = true
}

async function approve() {
  if (!selected.value) return
  selected.value = await api.approveReviewTask(selected.value.id, comment.value)
  await loadTasks()
  message.success('Review approved')
}

async function reject() {
  if (!selected.value) return
  selected.value = await api.rejectReviewTask(selected.value.id, comment.value)
  await loadTasks()
  message.success('Review rejected')
}

onMounted(loadTasks)
</script>
