<template>
  <section class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Dashboard</h1>
        <p class="page-subtitle">客服业务、售后处理和 Agent 运行状态概览。</p>
      </div>
      <n-button secondary @click="loadDashboard">刷新</n-button>
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
        <n-card title="意图分布" size="small">
          <div ref="intentChartRef" class="chart"></div>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card title="工单状态" size="small">
          <div ref="ticketChartRef" class="chart"></div>
        </n-card>
      </n-grid-item>
    </n-grid>

    <n-card title="最近 Agent 运行记录" size="small">
      <n-data-table :columns="columns" :data="runs" :pagination="{ pageSize: 6 }" />
    </n-card>
  </section>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'
import * as echarts from 'echarts'
import type { DataTableColumns } from 'naive-ui'
import { NButton, NCard, NDataTable, NGrid, NGridItem, NStatistic, useMessage } from 'naive-ui'

import { api, type AgentRun, type StatItem } from '@/api/client'

const message = useMessage()
const summary = ref<Record<string, number>>({})
const intentStats = ref<StatItem[]>([])
const ticketStats = ref<StatItem[]>([])
const runs = ref<AgentRun[]>([])
const intentChartRef = ref<HTMLDivElement | null>(null)
const ticketChartRef = ref<HTMLDivElement | null>(null)

const metrics = computed(() => [
  { label: '会话数', value: summary.value.session_count ?? 0 },
  { label: '商品数', value: summary.value.product_count ?? 0 },
  { label: '订单数', value: summary.value.order_count ?? 0 },
  { label: '待审核', value: summary.value.pending_review_count ?? 0 },
  { label: '待处理工单', value: summary.value.open_ticket_count ?? 0 },
  { label: 'Agent Runs', value: summary.value.agent_run_count ?? 0 },
  { label: '成功率', value: `${Math.round((summary.value.agent_success_rate ?? 0) * 100)}%` },
  { label: '节点数', value: 9 }
])

const columns: DataTableColumns<AgentRun> = [
  { title: 'Run ID', key: 'id', width: 80 },
  { title: '意图', key: 'intent' },
  { title: '状态', key: 'status' },
  { title: '摘要', key: 'summary' },
  { title: '创建时间', key: 'created_at' }
]

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
  message.success('Dashboard 已刷新')
}

function renderCharts() {
  if (intentChartRef.value) {
    echarts.init(intentChartRef.value).setOption({
      tooltip: {},
      xAxis: { type: 'category', data: intentStats.value.map((item) => item.name) },
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
          data: ticketStats.value.map((item) => ({ name: item.name, value: item.value }))
        }
      ]
    })
  }
}

onMounted(loadDashboard)
</script>

<style scoped>
.chart {
  height: 280px;
}
</style>

