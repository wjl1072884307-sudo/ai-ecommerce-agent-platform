<template>
  <section class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">{{ t('agentLogs.title') }}</h1>
        <p class="page-subtitle">{{ t('agentLogs.subtitle') }}</p>
      </div>
      <n-button secondary @click="loadRuns">{{ t('common.refresh') }}</n-button>
    </div>

    <n-grid :cols="2" :x-gap="16" responsive="screen">
      <n-grid-item>
        <n-card :title="t('agentLogs.runs')" size="small">
          <n-data-table :columns="columns" :data="runs" :pagination="{ pageSize: 8 }" />
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card :title="t('agentLogs.nodeLogs')" size="small">
          <n-empty v-if="!logs.length" :description="t('agentLogs.selectRun')" />
          <n-timeline v-else>
            <n-timeline-item
              v-for="log in logs"
              :key="log.id"
              :type="timelineType(log.status)"
              :title="log.node_name"
              :time="durationText(log)"
            >
              <n-space vertical>
                <n-space>
                  <n-tag size="small" :type="tagType(log.status)">{{ statusLabel(log.status) }}</n-tag>
                  <n-tag v-if="hasFallback(log)" size="small" type="warning">{{ t('agentLogs.fallback') }}</n-tag>
                  <n-tag v-if="hasSources(log)" size="small" type="info">{{ t('agentLogs.sources') }}</n-tag>
                  <n-tag v-if="isHighRisk(log)" size="small" type="error">{{ t('agentLogs.highRisk') }}</n-tag>
                </n-space>
                <n-alert v-if="log.error_message" type="error">{{ log.error_message }}</n-alert>
                <n-collapse>
                  <n-collapse-item :title="t('agentLogs.inputJson')">
                    <pre>{{ formatJson(log.input_json) }}</pre>
                  </n-collapse-item>
                  <n-collapse-item :title="t('agentLogs.outputJson')">
                    <pre>{{ formatJson(log.output_json) }}</pre>
                  </n-collapse-item>
                </n-collapse>
              </n-space>
            </n-timeline-item>
          </n-timeline>
        </n-card>
      </n-grid-item>
    </n-grid>
  </section>
</template>

<script setup lang="ts">
import { computed, h, onMounted, ref } from 'vue'
import type { DataTableColumns } from 'naive-ui'
import { NAlert, NButton, NCard, NCollapse, NCollapseItem, NDataTable, NEmpty, NGrid, NGridItem, NSpace, NTag, NTimeline, NTimelineItem } from 'naive-ui'
import { useI18n } from 'vue-i18n'

import { api, type AgentNodeLog, type AgentRun } from '@/api/client'
import { useDisplayText } from '@/i18n/display'

const { t } = useI18n()
const { statusLabel } = useDisplayText()
const runs = ref<AgentRun[]>([])
const logs = ref<AgentNodeLog[]>([])

const columns = computed<DataTableColumns<AgentRun>>(() => [
  { title: t('agentLogs.run'), key: 'id', width: 70 },
  { title: t('agentLogs.intent'), key: 'intent', render: (row) => statusLabel(row.intent) },
  { title: t('common.status'), key: 'status', render: (row) => statusLabel(row.status) },
  { title: t('agentLogs.summary'), key: 'summary' },
  { title: t('common.actions'), key: 'actions', render: (row) => h(NButton, { size: 'small', onClick: () => loadLogs(row.id) }, { default: () => t('agentLogs.logs') }) }
])

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

function parsedOutput(log: AgentNodeLog) {
  if (!log.output_json) return null
  try {
    return JSON.parse(log.output_json)
  } catch {
    return null
  }
}

function hasFallback(log: AgentNodeLog) {
  const output = parsedOutput(log)
  return Boolean(output?.fallback || output?.llm_fallback || output?.used_fallback)
}

function hasSources(log: AgentNodeLog) {
  const output = parsedOutput(log)
  return Array.isArray(output?.sources) && output.sources.length > 0
}

function isHighRisk(log: AgentNodeLog) {
  const output = parsedOutput(log)
  return output?.risk_level === 'high' || output?.requires_review === true
}

function durationText(log: AgentNodeLog) {
  return log.duration_ms === null || log.duration_ms === undefined ? undefined : `${log.duration_ms} ms`
}

function tagType(status: string) {
  if (status === 'success' || status === 'completed') return 'success'
  if (status === 'failed' || status === 'error') return 'error'
  return 'default'
}

function timelineType(status: string) {
  if (status === 'failed' || status === 'error') return 'error'
  if (status === 'success' || status === 'completed') return 'success'
  return 'default'
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
