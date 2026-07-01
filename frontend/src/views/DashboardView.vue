<template>
  <section class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">{{ t('dashboard.title') }}</h1>
        <p class="page-subtitle">{{ t('dashboard.subtitle') }}</p>
      </div>
      <n-button secondary @click="loadDashboard">{{ t('common.refresh') }}</n-button>
    </div>

    <n-grid :cols="4" :x-gap="16" :y-gap="16" responsive="screen">
      <n-grid-item v-for="metric in metrics" :key="metric.label">
        <n-card size="small">
          <n-statistic :label="metric.label" :value="metric.value" />
        </n-card>
      </n-grid-item>
    </n-grid>

    <n-grid :cols="2" :x-gap="16" :y-gap="16" responsive="screen">
      <n-grid-item>
        <n-card :title="t('dashboard.intentDistribution')" size="small">
          <div ref="intentChartRef" class="chart"></div>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card :title="t('dashboard.ticketStatus')" size="small">
          <div ref="ticketChartRef" class="chart"></div>
        </n-card>
      </n-grid-item>
    </n-grid>

    <n-card :title="t('dashboard.recentRuns')" size="small">
      <n-data-table :columns="columns" :data="runs" :pagination="{ pageSize: 6 }" />
    </n-card>
  </section>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts'
import type { DataTableColumns } from 'naive-ui'
import { NButton, NCard, NDataTable, NGrid, NGridItem, NStatistic, useMessage } from 'naive-ui'
import { useI18n } from 'vue-i18n'

import { api, type AgentRun, type StatItem } from '@/api/client'
import { useDisplayText } from '@/i18n/display'

const message = useMessage()
const { t, locale } = useI18n()
const { statusLabel } = useDisplayText()
const summary = ref<Record<string, number>>({})
const intentStats = ref<StatItem[]>([])
const ticketStats = ref<StatItem[]>([])
const runs = ref<AgentRun[]>([])
const intentChartRef = ref<HTMLDivElement | null>(null)
const ticketChartRef = ref<HTMLDivElement | null>(null)

const metrics = computed(() => [
  { label: t('dashboard.sessionCount'), value: summary.value.session_count ?? 0 },
  { label: t('dashboard.productCount'), value: summary.value.product_count ?? 0 },
  { label: t('dashboard.orderCount'), value: summary.value.order_count ?? 0 },
  { label: t('dashboard.pendingReviews'), value: summary.value.pending_review_count ?? 0 },
  { label: t('dashboard.openTickets'), value: summary.value.open_ticket_count ?? 0 },
  { label: t('dashboard.agentRuns'), value: summary.value.agent_run_count ?? 0 },
  { label: t('dashboard.successRate'), value: `${Math.round((summary.value.agent_success_rate ?? 0) * 100)}%` },
  { label: t('dashboard.nodeCount'), value: 9 }
])

const columns = computed<DataTableColumns<AgentRun>>(() => [
  { title: t('dashboard.runId'), key: 'id', width: 80 },
  { title: t('dashboard.intent'), key: 'intent', render: (row) => statusLabel(row.intent) },
  { title: t('common.status'), key: 'status', render: (row) => statusLabel(row.status) },
  { title: t('dashboard.summary'), key: 'summary' },
  { title: t('dashboard.createdAt'), key: 'created_at' }
])

async function loadDashboard() {
  const [summaryData, intents, tickets, runData] = await Promise.all([
    api.getSummary(),
    api.getIntentStats(),
    api.getTicketStats(),
    api.getAgentRuns()
  ])
  summary.value = summaryData
  intentStats.value = intents
  ticketStats.value = tickets
  runs.value = runData
  await nextTick()
  renderCharts()
  message.success(t('dashboard.refreshed'))
}

function renderCharts() {
  if (intentChartRef.value) {
    echarts.init(intentChartRef.value).setOption({
      tooltip: {},
      xAxis: { type: 'category', data: intentStats.value.map((item) => statusLabel(item.name)) },
      yAxis: { type: 'value' },
      series: [{ type: 'bar', data: intentStats.value.map((item) => item.value), itemStyle: { color: '#18a058' } }]
    })
  }
  if (ticketChartRef.value) {
    echarts.init(ticketChartRef.value).setOption({
      tooltip: { trigger: 'item' },
      series: [
        {
          type: 'pie',
          radius: '70%',
          data: ticketStats.value.map((item) => ({ name: statusLabel(item.name), value: item.value }))
        }
      ]
    })
  }
}

watch(locale, async () => {
  await nextTick()
  renderCharts()
})

onMounted(loadDashboard)
</script>

<style scoped>
.chart {
  height: 280px;
}
</style>
