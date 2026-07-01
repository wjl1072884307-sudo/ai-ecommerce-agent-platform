<template>
  <section class="sessions-page">
    <n-card class="session-list" size="small">
      <template #header>
        <div class="panel-header">
          <span>{{ t('sessions.title') }}</span>
          <n-button v-if="canRunAgent" size="small" type="primary" @click="showCreateSession = true">{{ t('sessions.simulateConversation') }}</n-button>
        </div>
      </template>
      <n-select v-model:value="queueFilter" size="small" :options="queueFilterOptions" />
      <n-input v-model:value="sessionKeyword" clearable size="small" :placeholder="t('sessions.searchPlaceholder')" />
      <n-list clickable class="session-items">
        <n-list-item
          v-for="item in filteredSessions"
          :key="item.id"
          :class="{ active: item.id === selectedSessionId }"
          @click="selectSession(item.id)"
        >
          <n-thing :title="sessionTitle(item)" :description="sessionDescription(item)">
            <template #footer>
              <n-space size="small">
                <n-tag size="small">{{ statusLabel(item.conversation_type) }}</n-tag>
                <n-tag size="small" :type="item.requires_human ? 'warning' : 'success'">
                  {{ item.requires_human ? t('sessions.requiresHuman') : statusLabel(item.status) }}
                </n-tag>
                <n-tag v-if="item.bound_order_id" size="small" type="info">#{{ item.bound_order_id }}</n-tag>
              </n-space>
            </template>
          </n-thing>
        </n-list-item>
      </n-list>
    </n-card>

    <n-card class="chat-panel" size="small">
      <template #header>{{ t('sessions.conversation') }}</template>
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
          :placeholder="t('sessions.inputPlaceholder')"
          @keydown.enter.exact.prevent="sendAndRun"
        />
        <n-button v-if="canRunAgent" type="primary" :disabled="!draft.trim()" :loading="running" @click="sendAndRun">
          {{ t('sessions.sendAndRun') }}
        </n-button>
      </div>
    </n-card>

    <n-card class="result-panel" size="small">
      <template #header>{{ t('sessions.contextPanel') }}</template>
      <n-empty v-if="!agentResult" :description="t('sessions.noAgentRun')" />
      <n-space v-else vertical>
        <n-descriptions bordered :column="1" size="small">
          <n-descriptions-item :label="t('sessions.runId')">{{ agentResult.run.id }}</n-descriptions-item>
          <n-descriptions-item :label="t('sessions.customer')">{{ selectedSession?.customer_id || '-' }}</n-descriptions-item>
          <n-descriptions-item :label="t('sessions.visitor')">{{ selectedSession?.visitor_id || '-' }}</n-descriptions-item>
          <n-descriptions-item :label="t('sessions.language')">{{ agentContext.language || '-' }}</n-descriptions-item>
          <n-descriptions-item :label="t('common.type')">{{ statusLabel(agentContext.conversation_type || selectedSession?.conversation_type) }}</n-descriptions-item>
          <n-descriptions-item :label="t('sessions.intent')">{{ statusLabel(agentResult.run.intent) }}</n-descriptions-item>
          <n-descriptions-item :label="t('common.status')">{{ statusLabel(agentResult.run.status) }}</n-descriptions-item>
          <n-descriptions-item :label="t('common.order')">{{ agentContext.matched_order?.order_no || selectedSession?.bound_order_id || '-' }}</n-descriptions-item>
          <n-descriptions-item :label="t('products.product')">{{ agentContext.matched_product?.name || selectedSession?.bound_product_id || '-' }}</n-descriptions-item>
          <n-descriptions-item :label="t('sessions.requiresHuman')">
            <n-tag :type="agentContext.risk_result?.need_review || agentContext.policy_result?.requires_order_info ? 'warning' : 'success'" size="small">
              {{ agentContext.risk_result?.need_review || agentContext.policy_result?.requires_order_info ? t('common.yes') : t('common.no') }}
            </n-tag>
          </n-descriptions-item>
          <n-descriptions-item :label="t('reviews.risk')">{{ statusLabel(agentContext.risk_result?.risk_level) }}</n-descriptions-item>
          <n-descriptions-item :label="t('sessions.review')">{{ statusLabel(agentResult.review_task?.status) }}</n-descriptions-item>
          <n-descriptions-item :label="t('sessions.ticket')">{{ agentResult.ticket?.ticket_no || '-' }}</n-descriptions-item>
          <n-descriptions-item :label="t('sessions.ticketType')">{{ statusLabel(agentResult.ticket?.ticket_type) }}</n-descriptions-item>
          <n-descriptions-item :label="t('agentLogs.fallback')">
            {{ agentContext.llm_result?.fallback_reason || '-' }}
          </n-descriptions-item>
        </n-descriptions>
        <n-card size="small" :title="t('sessions.policyDecision')" embedded>
          {{ agentContext.policy_result?.reason || '-' }}
        </n-card>
        <n-card size="small" :title="t('agentLogs.sources')" embedded>
          <n-empty v-if="!knowledgeSources.length" size="small" :description="t('knowledge.noChunks')" />
          <n-list v-else>
            <n-list-item v-for="source in knowledgeSources" :key="`${source.document_id}-${source.chunk_id}`">
              <n-thing :title="source.document_title" :description="source.document_type" />
            </n-list-item>
          </n-list>
        </n-card>
      </n-space>
    </n-card>

    <n-modal v-model:show="showCreateSession" preset="card" :title="t('sessions.simulateConversation')" class="session-modal">
      <n-space vertical>
        <n-select v-model:value="testIdentity" :options="testIdentityOptions" />
        <n-select v-model:value="testConversationType" :options="testConversationTypeOptions" />
        <n-input v-if="testIdentity === 'purchased'" v-model:value="testOrderNo" :placeholder="t('orders.orderNo')" />
        <n-input
          v-model:value="newSessionMessage"
          type="textarea"
          :rows="3"
          :placeholder="t('sessions.initialMessage')"
          @keydown.enter.exact.prevent="createSession"
        />
        <n-space justify="end">
          <n-button @click="showCreateSession = false">{{ t('common.cancel') }}</n-button>
          <n-button type="primary" :disabled="!canCreateSession" :loading="creatingSession" @click="createSession">
            {{ t('sessions.createTestConversation') }}
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
  NSelect,
  NSpace,
  NTag,
  NThing,
  useMessage
} from 'naive-ui'
import { useI18n } from 'vue-i18n'

import { api, type AgentRunResult, type MessageItem, type SessionItem } from '@/api/client'
import { role } from '@/auth/session'
import { useDisplayText } from '@/i18n/display'

const message = useMessage()
const { t } = useI18n()
const { sessionTitle, statusLabel } = useDisplayText()
const sessions = ref<SessionItem[]>([])
const messages = ref<MessageItem[]>([])
const selectedSessionId = ref<number | null>(null)
const draft = ref('')
const sessionKeyword = ref('')
const queueFilter = ref('all')
const running = ref(false)
const creatingSession = ref(false)
const showCreateSession = ref(false)
const newSessionMessage = ref('')
const testIdentity = ref<'anonymous' | 'purchased'>('anonymous')
const testConversationType = ref('pre_sales')
const testOrderNo = ref('MOCK202606120001')
const agentResult = ref<AgentRunResult | null>(null)
const canRunAgent = computed(() => role.value === 'admin' || role.value === 'agent')
const canCreateSession = computed(() => Boolean(newSessionMessage.value.trim()))
const selectedSession = computed(() => sessions.value.find((item) => item.id === selectedSessionId.value) || null)
const agentContext = computed(() => agentResult.value?.partial_context || {})
const knowledgeSources = computed(() => agentContext.value.knowledge_sources || [])
const queueFilterOptions = computed(() => [
  { label: t('sessions.filterAll'), value: 'all' },
  { label: t('sessions.filterPreSales'), value: 'pre_sales' },
  { label: t('sessions.filterAfterSales'), value: 'after_sales' },
  { label: t('sessions.filterLogistics'), value: 'logistics' },
  { label: t('sessions.filterComplaint'), value: 'complaint' },
  { label: t('sessions.filterInvoice'), value: 'invoice' },
  { label: t('sessions.filterPendingHuman'), value: 'pending_human' },
  { label: t('sessions.filterClosed'), value: 'closed' }
])
const testIdentityOptions = computed(() => [
  { label: t('sessions.identityAnonymous'), value: 'anonymous' },
  { label: t('sessions.identityPurchased'), value: 'purchased' }
])
const testConversationTypeOptions = computed(() => [
  { label: t('sessions.filterPreSales'), value: 'pre_sales' },
  { label: t('sessions.filterAfterSales'), value: 'after_sales' },
  { label: t('sessions.filterLogistics'), value: 'logistics' },
  { label: t('sessions.filterComplaint'), value: 'complaint' },
  { label: t('sessions.filterInvoice'), value: 'invoice' }
])

const filteredSessions = computed(() => {
  const keyword = sessionKeyword.value.trim().toLowerCase()
  return sessions.value.filter((item) => matchesQueueFilter(item) && matchesSessionKeyword(item, keyword))
})

function matchesQueueFilter(item: SessionItem) {
  if (queueFilter.value === 'all') return true
  if (queueFilter.value === 'pending_human') return item.requires_human
  if (queueFilter.value === 'closed') return item.status === 'closed'
  return item.conversation_type === queueFilter.value
}

function matchesSessionKeyword(item: SessionItem, keyword: string) {
  if (!keyword) return true
  return [
    item.title,
    sessionTitle(item),
    item.status,
    statusLabel(item.status),
    item.conversation_type,
    statusLabel(item.conversation_type),
    item.summary || '',
    `user ${item.user_id}`,
    `customer ${item.customer_id || ''}`,
    item.customer_id ? String(item.customer_id) : '',
    item.visitor_id || '',
    item.bound_order_id ? String(item.bound_order_id) : '',
    item.bound_product_id ? String(item.bound_product_id) : ''
  ].some((value) => value.toLowerCase().includes(keyword))
}

function sessionDescription(item: SessionItem) {
  const identity = item.customer_id ? `${t('sessions.customer')} ${item.customer_id}` : item.visitor_id || `${t('common.user')} ${item.user_id}`
  const order = item.bound_order_id ? `${t('common.order')} #${item.bound_order_id}` : t('sessions.noBoundOrder')
  return `${identity} / ${order}`
}

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
    const response = await api.sendCustomerMessage({
      customer_id: testIdentity.value === 'purchased' ? 1 : null,
      visitor_id: testIdentity.value === 'anonymous' ? `visitor-${Date.now()}` : null,
      content: newSessionMessage.value.trim(),
      channel: 'admin_test',
      conversation_type: testConversationType.value,
      order_no: testIdentity.value === 'purchased' && testOrderNo.value.trim() ? testOrderNo.value.trim() : null,
      run_agent: true
    })
    await loadSessions()
    await selectSession(response.session.id)
    agentResult.value = response.agent_result
    newSessionMessage.value = ''
    showCreateSession.value = false
    message.success(t('sessions.created'))
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
    message.success(t('sessions.agentCompleted'))
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

.session-list :deep(.n-select) {
  margin-bottom: 8px;
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
