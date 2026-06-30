<template>
  <section class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Knowledge</h1>
        <p class="page-subtitle">Browse policy documents, chunks, and retrieval results.</p>
      </div>
      <n-space>
        <n-button v-if="canWriteKnowledge" type="primary" @click="openCreate">New Document</n-button>
        <n-button secondary @click="loadDocuments">Refresh</n-button>
      </n-space>
    </div>

    <n-grid :cols="2" :x-gap="16" responsive="screen">
      <n-grid-item>
        <n-card title="Documents" size="small">
          <n-data-table :columns="columns" :data="documents" :pagination="{ pageSize: 8 }" />
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card title="Search" size="small">
          <n-space vertical>
            <n-input v-model:value="query" placeholder="Enter a refund, return, or after-sales question" />
            <n-button type="primary" @click="search">Search</n-button>
            <n-empty v-if="searched && !chunks.length" description="No matching chunks" />
            <n-list v-else bordered>
              <n-list-item v-for="chunk in chunks" :key="chunk.id">
                <n-thing :title="chunk.document_title" :description="chunk.content" />
              </n-list-item>
            </n-list>
          </n-space>
        </n-card>
      </n-grid-item>
    </n-grid>

    <n-drawer v-model:show="showDrawer" :width="620">
      <n-drawer-content :title="editing ? 'Edit document' : 'Document detail'">
        <n-space v-if="selected" vertical>
          <template v-if="editing">
            <n-input v-model:value="form.title" placeholder="Title" />
            <n-input v-model:value="form.document_type" placeholder="Document type" />
            <n-input v-model:value="form.status" placeholder="Status" />
            <n-input v-model:value="form.content" type="textarea" :rows="8" placeholder="Content" />
            <n-button type="primary" @click="saveDocument">Save</n-button>
          </template>
          <template v-else>
            <n-alert type="info" :title="selected.title">{{ selected.content }}</n-alert>
            <n-card v-for="chunk in selected.chunks" :key="chunk.id" size="small">
              {{ chunk.content }}
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
import { NAlert, NButton, NCard, NDataTable, NDrawer, NDrawerContent, NEmpty, NGrid, NGridItem, NInput, NList, NListItem, NSpace, NThing, useMessage } from 'naive-ui'

import { api, type KnowledgeChunk, type KnowledgeDocument } from '@/api/client'
import { role } from '@/auth/session'

const message = useMessage()
const documents = ref<KnowledgeDocument[]>([])
const selected = ref<KnowledgeDocument | null>(null)
const chunks = ref<KnowledgeChunk[]>([])
const query = ref('Can I return a headset with noise?')
const showDrawer = ref(false)
const searched = ref(false)
const editing = ref(false)
const form = ref({ title: '', document_type: 'policy', content: '', status: 'active' })
const canWriteKnowledge = computed(() => role.value === 'admin')

const columns: DataTableColumns<KnowledgeDocument> = [
  { title: 'Title', key: 'title' },
  { title: 'Type', key: 'document_type' },
  { title: 'Status', key: 'status' },
  {
    title: 'Actions',
    key: 'actions',
    render: (row) =>
      h(NSpace, null, {
        default: () => [
          h(NButton, { size: 'small', onClick: () => openDetail(row.id) }, { default: () => 'Detail' }),
          canWriteKnowledge.value ? h(NButton, { size: 'small', secondary: true, onClick: () => openEdit(row.id) }, { default: () => 'Edit' }) : null
        ]
      })
  }
]

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
  message.success('Document saved')
}

async function search() {
  chunks.value = await api.searchKnowledge(query.value)
  searched.value = true
}

onMounted(async () => {
  await loadDocuments()
  await search()
})
</script>
