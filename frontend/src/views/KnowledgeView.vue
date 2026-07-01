<template>
  <section class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">{{ t('knowledge.title') }}</h1>
        <p class="page-subtitle">{{ t('knowledge.subtitle') }}</p>
      </div>
      <n-space>
        <n-button v-if="canWriteKnowledge" type="primary" @click="openCreate">{{ t('knowledge.newDocument') }}</n-button>
        <n-button secondary @click="loadDocuments">{{ t('common.refresh') }}</n-button>
      </n-space>
    </div>

    <n-grid :cols="2" :x-gap="16" responsive="screen">
      <n-grid-item>
        <n-card :title="t('knowledge.documents')" size="small">
          <n-data-table :columns="columns" :data="documents" :pagination="{ pageSize: 8 }" />
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card :title="t('knowledge.search')" size="small">
          <n-space vertical>
            <n-input v-model:value="query" :placeholder="t('knowledge.searchPlaceholder')" />
            <n-button type="primary" @click="search">{{ t('common.search') }}</n-button>
            <n-empty v-if="searched && !chunks.length" :description="t('knowledge.noChunks')" />
            <n-list v-else bordered>
              <n-list-item v-for="chunk in chunks" :key="chunk.id">
                <n-thing :title="knowledgeTitle(chunk)" :description="knowledgeChunk(chunk)" />
              </n-list-item>
            </n-list>
          </n-space>
        </n-card>
      </n-grid-item>
    </n-grid>

    <n-drawer v-model:show="showDrawer" :width="620">
      <n-drawer-content :title="editing ? t('knowledge.editDocument') : t('knowledge.documentDetail')">
        <n-space v-if="selected" vertical>
          <template v-if="editing">
            <n-input v-model:value="form.title" :placeholder="t('common.title')" />
            <n-input v-model:value="form.document_type" :placeholder="t('knowledge.documentType')" />
            <n-input v-model:value="form.status" :placeholder="t('common.status')" />
            <n-input v-model:value="form.content" type="textarea" :rows="8" :placeholder="t('common.content')" />
            <n-button type="primary" @click="saveDocument">{{ t('common.save') }}</n-button>
          </template>
          <template v-else>
            <n-alert type="info" :title="knowledgeTitle(selected)">{{ knowledgeContent(selected) }}</n-alert>
            <n-card v-for="chunk in selected.chunks" :key="chunk.id" size="small">
              {{ knowledgeChunk(chunk) }}
            </n-card>
          </template>
        </n-space>
      </n-drawer-content>
    </n-drawer>
  </section>
</template>

<script setup lang="ts">
import { computed, h, onMounted, ref } from 'vue'
import type { DataTableColumns } from 'naive-ui'
import { NAlert, NButton, NCard, NDataTable, NDrawer, NDrawerContent, NEmpty, NGrid, NGridItem, NInput, NList, NListItem, NSpace, NTag, NThing, useMessage } from 'naive-ui'
import { useI18n } from 'vue-i18n'

import { api, type KnowledgeChunk, type KnowledgeDocument } from '@/api/client'
import { role } from '@/auth/session'
import { useDisplayText } from '@/i18n/display'

const message = useMessage()
const { t } = useI18n()
const { knowledgeTitle, knowledgeType, knowledgeContent, knowledgeChunk, statusLabel } = useDisplayText()
const documents = ref<KnowledgeDocument[]>([])
const selected = ref<KnowledgeDocument | null>(null)
const chunks = ref<KnowledgeChunk[]>([])
const query = ref('')
const showDrawer = ref(false)
const searched = ref(false)
const editing = ref(false)
const form = ref({ title: '', document_type: 'policy', content: '', status: 'active' })
const canWriteKnowledge = computed(() => role.value === 'admin')

const columns = computed<DataTableColumns<KnowledgeDocument>>(() => [
  { title: t('common.title'), key: 'title', render: (row) => knowledgeTitle(row) },
  { title: t('common.type'), key: 'document_type', render: (row) => knowledgeType(row) },
  {
    title: t('common.status'),
    key: 'status',
    render: (row) => h(NTag, { size: 'small', type: row.status === 'active' ? 'success' : 'warning' }, { default: () => statusLabel(row.status) })
  },
  {
    title: t('common.actions'),
    key: 'actions',
    render: (row) =>
      h(NSpace, null, {
        default: () => [
          h(NButton, { size: 'small', onClick: () => openDetail(row.id) }, { default: () => t('common.detail') }),
          canWriteKnowledge.value
            ? h(NButton, { size: 'small', secondary: true, onClick: () => openEdit(row.id) }, { default: () => t('common.edit') })
            : null
        ]
      })
  }
])

async function loadDocuments() {
  documents.value = await api.getDocuments()
}

async function openDetail(id: number) {
  selected.value = await api.getDocument(id)
  editing.value = false
  showDrawer.value = true
}

function openCreate() {
  selected.value = { id: 0, title: '', document_type: 'policy', content: '', status: 'active', chunks: [] }
  form.value = { title: '', document_type: 'policy', content: '', status: 'active' }
  editing.value = true
  showDrawer.value = true
}

async function openEdit(id: number) {
  selected.value = await api.getDocument(id)
  form.value = {
    title: selected.value.title,
    document_type: selected.value.document_type,
    content: selected.value.content,
    status: selected.value.status
  }
  editing.value = true
  showDrawer.value = true
}

async function saveDocument() {
  if (!selected.value) return
  if (selected.value.id === 0) {
    selected.value = await api.createDocument(form.value)
  } else {
    selected.value = await api.updateDocument(selected.value.id, form.value)
  }
  await loadDocuments()
  editing.value = false
  message.success(t('knowledge.saved'))
}

async function search() {
  chunks.value = await api.searchKnowledge(query.value || 'return refund after-sales')
  searched.value = true
}

onMounted(async () => {
  await loadDocuments()
  await search()
})
</script>
