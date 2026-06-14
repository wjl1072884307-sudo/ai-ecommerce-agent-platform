<template>
  <section class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">人工审核</h1>
        <p class="page-subtitle">处理 Agent 创建的高风险回复和售后审核任务。</p>
      </div>
      <n-button secondary @click="loadTasks">刷新</n-button>
    </div>

    <n-card size="small">
      <n-data-table :columns="columns" :data="tasks" :pagination="{ pageSize: 8 }" />
    </n-card>

    <n-drawer v-model:show="showDrawer" :width="460">
      <n-drawer-content title="审核详情">
        <n-space v-if="selected" vertical>
          <n-descriptions bordered :column="1" size="small">
            <n-descriptions-item label="标题">{{ selected.title }}</n-descriptions-item>
            <n-descriptions-item label="风险等级">{{ selected.risk_level }}</n-descriptions-item>
            <n-descriptions-item label="风险原因">{{ selected.risk_reason }}</n-descriptions-item>
            <n-descriptions-item label="状态">{{ selected.status }}</n-descriptions-item>
          </n-descriptions>
          <n-input v-model:value="comment" type="textarea" placeholder="审核意见" />
          <n-space>
            <n-button type="primary" @click="approve">通过</n-button>
            <n-button type="error" secondary @click="reject">驳回</n-button>
          </n-space>
        </n-space>
      </n-drawer-content>
    </n-drawer>
  </section>
</template>

<script setup lang="ts">
import { h, onMounted, ref } from 'vue'
import type { DataTableColumns } from 'naive-ui'
import { NButton, NCard, NDataTable, NDescriptions, NDescriptionsItem, NDrawer, NDrawerContent, NInput, NSpace, NTag, useMessage } from 'naive-ui'

import { api, type ReviewTask } from '@/api/client'

const message = useMessage()
const tasks = ref<ReviewTask[]>([])
const selected = ref<ReviewTask | null>(null)
const showDrawer = ref(false)
const comment = ref('确认处理方案合理。')

const columns: DataTableColumns<ReviewTask> = [
  { title: 'ID', key: 'id', width: 70 },
  { title: '标题', key: 'title' },
  { title: '风险', key: 'risk_level', render: (row) => h(NTag, { type: row.risk_level === 'high' ? 'error' : 'warning', size: 'small' }, { default: () => row.risk_level }) },
  { title: '状态', key: 'status' },
  { title: '原因', key: 'risk_reason' },
  { title: '操作', key: 'actions', render: (row) => h(NButton, { size: 'small', onClick: () => openDetail(row) }, { default: () => '审核' }) }
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
  message.success('审核已通过')
}

async function reject() {
  if (!selected.value) return
  selected.value = await api.rejectReviewTask(selected.value.id, comment.value)
  await loadTasks()
  message.success('审核已驳回')
}

onMounted(loadTasks)
</script>

