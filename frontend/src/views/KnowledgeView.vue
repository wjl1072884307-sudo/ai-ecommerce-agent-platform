<template>
  <section class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">知识库管理</h1>
        <p class="page-subtitle">查看售后政策文档、chunk，并测试检索效果。</p>
      </div>
      <n-button secondary @click="loadDocuments">刷新</n-button>
    </div>

    <n-grid :cols="2" :x-gap="16" responsive="screen">
      <n-grid-item>
        <n-card title="文档列表" size="small">
          <n-data-table :columns="columns" :data="documents" :pagination="{ pageSize: 8 }" />
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card title="检索测试" size="small">
          <n-space vertical>
            <n-input v-model:value="query" placeholder="输入退货相关问题" />
            <n-button type="primary" @click="search">检索</n-button>
            <n-empty v-if="searched && !chunks.length" description="暂无匹配的知识库 chunk" />
            <n-list v-else bordered>
              <n-list-item v-for="chunk in chunks" :key="chunk.id">
                <n-thing :title="chunk.document_title" :description="chunk.content" />
              </n-list-item>
            </n-list>
          </n-space>
        </n-card>
      </n-grid-item>
    </n-grid>

    <n-drawer v-model:show="showDrawer" :width="560">
      <n-drawer-content title="知识文档详情">
        <n-space v-if="selected" vertical>
          <n-alert type="info" :title="selected.title">{{ selected.content }}</n-alert>
          <n-card v-for="chunk in selected.chunks" :key="chunk.id" size="small">
            {{ chunk.content }}
          </n-card>
        </n-space>
      </n-drawer-content>
    </n-drawer>
  </section>
</template>

<script setup lang="ts">
import { h, onMounted, ref } from 'vue'
import type { DataTableColumns } from 'naive-ui'
import { NAlert, NButton, NCard, NDataTable, NDrawer, NDrawerContent, NEmpty, NGrid, NGridItem, NInput, NList, NListItem, NSpace, NThing } from 'naive-ui'

import { api, type KnowledgeChunk, type KnowledgeDocument } from '@/api/client'

const documents = ref<KnowledgeDocument[]>([])
const selected = ref<KnowledgeDocument | null>(null)
const chunks = ref<KnowledgeChunk[]>([])
const query = ref('耳机有杂音，可以退货吗？')
const showDrawer = ref(false)
const searched = ref(false)

const columns: DataTableColumns<KnowledgeDocument> = [
  { title: '标题', key: 'title' },
  { title: '类型', key: 'document_type' },
  { title: '状态', key: 'status' },
  { title: '操作', key: 'actions', render: (row) => h(NButton, { size: 'small', onClick: () => openDetail(row.id) }, { default: () => '详情' }) }
]

async function loadDocuments() {
  documents.value = await api.getDocuments()
}

async function openDetail(id: number) {
  selected.value = await api.getDocument(id)
  showDrawer.value = true
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
