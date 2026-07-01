<template>
  <section class="sessions-page">
    <n-card class="session-list" size="small">
      <template #header>
        <div class="panel-header">
          <span>Sessions</span>
          <n-button v-if="canRunAgent" size="small" type="primary" @click="showCreateSession = true">New</n-button>
        </div>
      </template>
      <n-input v-model:value="sessionKeyword" clearable size="small" placeholder="Search title, status, user" />
      <n-list clickable class="session-items">
        <n-list-item
          v-for="item in filteredSessions"
          :key="item.id"
          :class="{ active: item.id === selectedSessionId }"
          @click="selectSession(item.id)"
        >
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
        <n-input
          v-model:value="draft"
          type="textarea"
          :rows="2"
          placeholder="Enter customer message"
          @keydown.enter.exact.prevent="sendAndRun"
        />
        <n-button v-if="canRunAgent" type="primary" :disabled="!draft.trim()" :loading="running" @click="sendAndRun">
          Send and Run Agent
        </n-button>
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

    <n-modal v-model:show="showCreateSession" preset="card" title="New Session" class="session-modal">
      <n-space vertical>
        <n-input v-model:value="newSessionTitle" placeholder="Session title" />
        <n-input
          v-model:value="newSessionMessage"
          type="textarea"
          :rows="3"
          placeholder="Initial customer message"
          @keydown.enter.exact.prevent="createSession"
        />
        <n-space justify="end">
          <n-button @click="showCreateSession = false">Cancel</n-button>
          <n-button type="primary" :disabled="!canCreateSession" :loading="creatingSession" @click="createSession">
            Create
          </n-button>
        </n-space>
      </n-space>
    </n-modal>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  NAlert,
  NButton,
  NCard,
  NDescriptions,
  NDescriptionsItem,
  NEmpty,
  NInput,
  NList,
  NListItem,
  NModal,
  NSpace,
  NThing,
  useMessage
} from 'naive-ui'

import { api, type AgentRunResult, type MessageItem, type SessionItem } from '@/api/client'
import { role } from '@/auth/session'

const message = useMessage()
const sessions = ref<SessionItem[]>([])
const messages = ref<MessageItem[]>([])
const selectedSessionId = ref<number | null>(null)
const draft = ref('')
const sessionKeyword = ref('')
const running = ref(false)
const creatingSession = ref(false)
const showCreateSession = ref(false)
const newSessionTitle = ref('')
const newSessionMessage = ref('')
const agentResult = ref<AgentRunResult | null>(null)
const canRunAgent = computed(() => role.value === 'admin' || role.value === 'agent')
const canCreateSession = computed(() => Boolean(newSessionTitle.value.trim() && newSessionMessage.value.trim()))

const filteredSessions = computed(() => {
  const keyword = sessionKeyword.value.trim().toLowerCase()
  if (!keyword) return sessions.value
  return sessions.value.filter((item) =>
    [item.title, item.status, `user ${item.user_id}`, String(item.user_id)].some((value) => value.toLowerCase().includes(keyword))
  )
})

async function loadSessions() {
  sessions.value = await api.getSessions()
  if (!selectedSessionId.value && sessions.value.length) {
    await selectSession(sessions.value[0].id)
  }
}

async function selectSession(id: number) {
  selectedSessionId.value = id
  agentResult.value = null
  messages.value = await api.getMessages(id)
}

async function createSession() {
  if (!canCreateSession.value) return
  creatingSession.value = true
  try {
    const created = await api.createSession({
      user_id: 1,
      title: newSessionTitle.value.trim(),
      initial_message: newSessionMessage.value.trim()
    })
    await loadSessions()
    await selectSession(created.id)
    newSessionTitle.value = ''
    newSessionMessage.value = ''
    showCreateSession.value = false
    message.success('Session created')
  } finally {
    creatingSession.value = false
  }
}

async function sendAndRun() {
  if (!selectedSessionId.value || !draft.value.trim() || running.value) return
  running.value = true
  try {
    const content = draft.value.trim()
    draft.value = ''
    const created = await api.sendMessage(selectedSessionId.value, content)
    agentResult.value = await api.runAgent(selectedSessionId.value, created.id)
    messages.value = await api.getMessages(selectedSessionId.value)
    await loadSessions()
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

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.session-items {
  margin-top: 10px;
}

.session-items :deep(.n-list-item) {
  border-radius: 6px;
}

.session-items :deep(.n-list-item.active) {
  background: #e6f7ee;
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

.session-modal {
  width: min(520px, calc(100vw - 32px));
}
</style>
