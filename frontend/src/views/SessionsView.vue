<template>
  <section class="sessions-page">
    <n-card class="session-list" size="small">
      <template #header>Sessions</template>
      <n-list clickable>
        <n-list-item v-for="item in sessions" :key="item.id" @click="selectSession(item.id)">
          <n-thing :title="item.title" :description="`User ${item.user_id} / ${item.status}`" />
        </n-list-item>
      </n-list>
    </n-card>

    <n-card class="chat-panel" size="small">
      <template #header>Conversation</template>
      <div class="messages">
        <div v-for="item in messages" :key="item.id" class="message" :class="item.sender_type">
          <strong>{{ item.sender_type }}</strong>
          <span>{{ item.content }}</span>
        </div>
      </div>
      <div class="composer">
        <n-input v-model:value="draft" type="textarea" :rows="2" placeholder="Enter customer message" />
        <n-button v-if="canRunAgent" type="primary" :loading="running" @click="sendAndRun">Send and Run Agent</n-button>
      </div>
    </n-card>

    <n-card class="result-panel" size="small">
      <template #header>Agent Result</template>
      <n-empty v-if="!agentResult" description="No Agent run yet" />
      <n-space v-else vertical>
        <n-alert title="Reply suggestion" type="success">
          {{ agentResult.reply_suggestion?.content }}
        </n-alert>
        <n-descriptions bordered :column="1" size="small">
          <n-descriptions-item label="Intent">{{ agentResult.run.intent }}</n-descriptions-item>
          <n-descriptions-item label="Status">{{ agentResult.run.status }}</n-descriptions-item>
          <n-descriptions-item label="Review">{{ agentResult.review_task?.status || '-' }}</n-descriptions-item>
          <n-descriptions-item label="Ticket">{{ agentResult.ticket?.ticket_no || '-' }}</n-descriptions-item>
          <n-descriptions-item label="Ticket type">{{ agentResult.ticket?.ticket_type || '-' }}</n-descriptions-item>
        </n-descriptions>
      </n-space>
    </n-card>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { NAlert, NButton, NCard, NDescriptions, NDescriptionsItem, NEmpty, NInput, NList, NListItem, NSpace, NThing, useMessage } from 'naive-ui'

import { api, type AgentRunResult, type MessageItem, type SessionItem } from '@/api/client'
import { role } from '@/auth/session'

const message = useMessage()
const sessions = ref<SessionItem[]>([])
const messages = ref<MessageItem[]>([])
const selectedSessionId = ref<number | null>(null)
const draft = ref('The headset I bought has noise. Can I return it?')
const running = ref(false)
const agentResult = ref<AgentRunResult | null>(null)
const canRunAgent = computed(() => role.value === 'admin' || role.value === 'agent')

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
    message.success('Agent run completed')
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
