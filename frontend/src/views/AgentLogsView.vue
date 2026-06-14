<template>
  <section class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Agent 运行日志</h1>
        <p class="page-subtitle">查看 Agent run 和每个节点的输入输出。</p>
      </div>
      <n-button secondary @click="loadRuns">刷新</n-button>
    </div>

    <n-grid :cols="2" :x-gap="16" responsive="screen">
      <n-grid-item>
        <n-card title="运行记录" size="small">
          <n-data-table :columns="columns" :data="runs" :pagination="{ pageSize: 8 }" />
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card title="节点日志" size="small">
          <n-empty v-if="!logs.length" description="选择一条运行记录" />
          <n-timeline v-else>
            <n-timeline-item v-for="log in logs" :key="log.id" :title="`${log.node_name} · ${log.status}`">
              <n-collapse>
                <n-collapse-item title="输入输出 JSON">
                  <pre>{{ formatJson(log.input_json) }}</pre>
                  <pre>{{ formatJson(log.output_json) }}</pre>
                  <n-alert v-if="log.error_message" type="error">{{ log.error_message }}</n-alert>
                </n-collapse-item>
              </n-collapse>
            </n-timeline-item>
          </n-timeline>
        </n-card>
      </n-grid-item>
    </n-grid>
  </section>
</template>

<script setup lang="ts">
import { h, onMounted, ref } from 'vue'
import type { DataTableColumns } from 'naive-ui'
import { NAlert, NButton, NCard, NCollapse, NCollapseItem, NDataTable, NEmpty, NGrid, NGridItem, NTimeline, NTimelineItem } from 'naive-ui'

import { api, type AgentNodeLog, type AgentRun } from '@/api/client'

const runs = ref<AgentRun[]>([])
const logs = ref<AgentNodeLog[]>([])

const columns: DataTableColumns<AgentRun> = [
  { title: 'Run', key: 'id', width: 70 },
  { title: '意图', key: 'intent' },
  { title: '状态', key: 'status' },
  { title: '摘要', key: 'summary' },
  { title: '操作', key: 'actions', render: (row) => h(NButton, { size: 'small', onClick: () => loadLogs(row.id) }, { default: () => '日志' }) }
]

async function loadRuns() {
  runs.value = await api.getAgentRuns()
  if (runs.value.length) await loadLogs(runs.value[0].id)
}

async function loadLogs(runId: number) {
  logs.value = await api.getAgentLogs(runId)
}

function formatJson(value: string | null) {
  if (!value) return '-'
  try {
    return JSON.stringify(JSON.parse(value), null, 2)
  } catch {
    return value
  }
}

onMounted(loadRuns)
</script>

<style scoped>
pre {
  max-height: 220px;
  overflow: auto;
  margin: 8px 0;
  padding: 10px;
  border-radius: 6px;
  background: #f6f8fa;
  font-size: 12px;
  white-space: pre-wrap;
}
</style>

