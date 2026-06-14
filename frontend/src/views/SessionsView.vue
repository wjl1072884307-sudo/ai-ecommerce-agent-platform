<template>
  <section class="sessions-page">
    <n-card class="session-list" size="small">
      <template #header>会话列表</template>
      <n-list clickable>
        <n-list-item v-for="item in sessions" :key="item.id" @click="selectSession(item.id)">
          <n-thing :title="item.title" :description="`用户 ${item.user_id} · ${item.status}`" />
        </n-list-item>
      </n-list>
    </n-card>

    <n-card class="chat-panel" size="small">
      <template #header>客服会话</template>
      <div class="messages">
        <div v-for="item in messages" :key="item.id" class="message" :class="item.sender_type">
          <strong>{{ item.sender_type }}</strong>
          <span>{{ item.content }}</span>
        </div>
      </div>
      <div class="composer">
        <n-input v-model:value="draft" type="textarea" :rows="2" placeholder="输入用户消息" />
        <n-button type="primary" :loading="running" @click="sendAndRun">发送并触发 Agent</n-button>
      </div>
    </n-card>

    <n-card class="result-panel" size="small">
      <template #header>Agent 结果</template>
      <n-empty v-if="!agentResult" description="尚未触发 Agent" />
      <n-space v-else vertical>
        <n-alert title="回复建议" type="success">
          {{ agentResult.reply_suggestion?.content }}
        </n-alert>
        <n-descriptions bordered :column="1" size="small">
          <n-descriptions-item label="意图">{{ agentResult.run.intent }}</n-descriptions-item>
          <n-descriptions-item label="运行状态">{{ agentResult.run.status }}</n-descriptions-item>
          <n-descriptions-item label="审核任务">{{ agentResult.review_task?.status || '-' }}</n-descriptions-item>
          <n-descriptions-item label="工单">{{ agentResult.ticket?.ticket_no || '-' }}</n-descriptions-item>
          <n-descriptions-item label="工单类型">{{ agentResult.ticket?.ticket_type || '-' }}</n-descriptions-item>
        </n-descriptions>
      </n-space>
    </n-card>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { NAlert, NButton, NCard, NDescriptions, NDescriptionsItem, NEmpty, NInput, NList, NListItem, NSpace, NThing, useMessage } from 'naive-ui'

import { api, type AgentRunResult, type MessageItem, type SessionItem } from '@/api/client'

const message = useMessage()
const sessions = ref<SessionItem[]>([])
const messages = ref<MessageItem[]>([])
const selectedSessionId = ref<number | null>(null)
const draft = ref('我买的耳机有杂音，可以退货吗？')
const running = ref(false)
const agentResult = ref<AgentRunResult | null>(null)

async function loadSessions() {
  sessions.value = await api.getSessions()
  if (!selectedSessionId.value && sessions.value.length) {
    await selectSession(sessions.value[0].id)
  }
}

async function selectSession(id: number) {
  selectedSessionId.value = id
  messages.value = await api.getMessages(id)
}

async function sendAndRun() {
  if (!selectedSessionId.value || !draft.value.trim()) return
  running.value = true
  try {
    const created = await api.sendMessage(selectedSessionId.value, draft.value.trim())
    messages.value.push(created)
    agentResult.value = await api.runAgent(selectedSessionId.value, created.id)
    message.success('Agent 已完成处理')
  } finally {
    running.value = false
  }
}

onMounted(loadSessions)
</script>

<style scoped>
.sessions-page {
  display: grid;
  grid-template-columns: 260px minmax(0, 1fr) 360px;
  gap: 16px;
  min-height: calc(100vh - 112px);
}

.messages {
  display: flex;
  min-height: 420px;
  flex-direction: column;
  gap: 10px;
  padding: 8px;
  overflow: auto;
}

.message {
  display: flex;
  max-width: 78%;
  flex-direction: column;
  gap: 4px;
  padding: 10px 12px;
  border-radius: 8px;
  background: #eef2f6;
}

.message.customer {
  align-self: flex-end;
  background: #dff7e8;
}

.composer {
  display: flex;
  gap: 10px;
  align-items: flex-end;
}
</style>

