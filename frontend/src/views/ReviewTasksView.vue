<template>
  <section class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">{{ t('reviews.title') }}</h1>
        <p class="page-subtitle">{{ t('reviews.subtitle') }}</p>
      </div>
      <n-button secondary @click="loadTasks">{{ t('common.refresh') }}</n-button>
    </div>

    <n-card size="small">
      <n-data-table :columns="columns" :data="tasks" :pagination="{ pageSize: 8 }" />
    </n-card>

    <n-drawer v-model:show="showDrawer" :width="480">
      <n-drawer-content :title="t('reviews.detail')">
        <n-space v-if="selected" vertical>
          <n-descriptions bordered :column="1" size="small">
            <n-descriptions-item :label="t('common.title')">{{ selected.title }}</n-descriptions-item>
            <n-descriptions-item :label="t('reviews.risk')">{{ statusLabel(selected.risk_level) }}</n-descriptions-item>
            <n-descriptions-item :label="t('reviews.reason')">{{ selected.risk_reason || '-' }}</n-descriptions-item>
            <n-descriptions-item :label="t('common.status')">{{ statusLabel(selected.status) }}</n-descriptions-item>
          </n-descriptions>
          <template v-if="canReview">
            <n-input v-model:value="comment" type="textarea" :placeholder="t('reviews.commentPlaceholder')" />
            <n-space>
              <n-button type="primary" @click="approve">{{ t('reviews.approve') }}</n-button>
              <n-button type="error" secondary @click="reject">{{ t('reviews.reject') }}</n-button>
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
import { useI18n } from 'vue-i18n'

import { api, type ReviewTask } from '@/api/client'
import { role } from '@/auth/session'
import { useDisplayText } from '@/i18n/display'

const message = useMessage()
const { t } = useI18n()
const { statusLabel } = useDisplayText()
const tasks = ref<ReviewTask[]>([])
const selected = ref<ReviewTask | null>(null)
const showDrawer = ref(false)
const comment = ref('Approved after manual review.')
const canReview = computed(() => role.value === 'admin' || role.value === 'reviewer')

const columns = computed<DataTableColumns<ReviewTask>>(() => [
  { title: t('common.id'), key: 'id', width: 70 },
  { title: t('common.title'), key: 'title' },
  { title: t('reviews.risk'), key: 'risk_level', render: (row) => h(NTag, { type: row.risk_level === 'high' ? 'error' : 'warning', size: 'small' }, { default: () => statusLabel(row.risk_level) }) },
  { title: t('common.status'), key: 'status', render: (row) => statusLabel(row.status) },
  { title: t('reviews.reason'), key: 'risk_reason' },
  { title: t('common.actions'), key: 'actions', render: (row) => h(NButton, { size: 'small', onClick: () => openDetail(row) }, { default: () => canReview.value ? t('reviews.review') : t('common.view') }) }
])

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
  message.success(t('reviews.approved'))
}

async function reject() {
  if (!selected.value) return
  selected.value = await api.rejectReviewTask(selected.value.id, comment.value)
  await loadTasks()
  message.success(t('reviews.rejected'))
}

onMounted(loadTasks)
</script>
