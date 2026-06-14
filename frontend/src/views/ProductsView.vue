<template>
  <section class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">商品管理</h1>
        <p class="page-subtitle">查看商品、SKU、库存和售后标签。</p>
      </div>
      <div class="toolbar">
        <n-input v-model:value="keyword" placeholder="搜索商品" clearable />
        <n-button type="primary" @click="loadProducts">搜索</n-button>
      </div>
    </div>

    <n-card size="small">
      <n-data-table :columns="columns" :data="products" :pagination="{ pageSize: 8 }" />
    </n-card>

    <n-drawer v-model:show="showDrawer" :width="420">
      <n-drawer-content title="商品详情">
        <n-descriptions v-if="selected" bordered :column="1" size="small">
          <n-descriptions-item label="名称">{{ selected.name }}</n-descriptions-item>
          <n-descriptions-item label="SKU">{{ selected.sku }}</n-descriptions-item>
          <n-descriptions-item label="类目">{{ selected.category }}</n-descriptions-item>
          <n-descriptions-item label="价格">{{ selected.price }}</n-descriptions-item>
          <n-descriptions-item label="库存">{{ selected.stock }}</n-descriptions-item>
          <n-descriptions-item label="售后">{{ selected.after_sale_policy }}</n-descriptions-item>
          <n-descriptions-item label="描述">{{ selected.description }}</n-descriptions-item>
        </n-descriptions>
      </n-drawer-content>
    </n-drawer>
  </section>
</template>

<script setup lang="ts">
import { h, onMounted, ref } from 'vue'
import type { DataTableColumns } from 'naive-ui'
import { NButton, NCard, NDataTable, NDescriptions, NDescriptionsItem, NDrawer, NDrawerContent, NInput, NTag } from 'naive-ui'

import { api, type Product } from '@/api/client'

const keyword = ref('')
const products = ref<Product[]>([])
const selected = ref<Product | null>(null)
const showDrawer = ref(false)

const columns: DataTableColumns<Product> = [
  { title: 'ID', key: 'id', width: 70 },
  { title: '商品', key: 'name' },
  { title: 'SKU', key: 'sku' },
  { title: '类目', key: 'category' },
  { title: '价格', key: 'price' },
  { title: '库存', key: 'stock' },
  { title: '状态', key: 'status', render: (row) => h(NTag, { type: 'success', size: 'small' }, { default: () => row.status }) },
  { title: '操作', key: 'actions', render: (row) => h(NButton, { size: 'small', onClick: () => openDetail(row.id) }, { default: () => '详情' }) }
]

async function loadProducts() {
  products.value = await api.getProducts(keyword.value)
}

async function openDetail(id: number) {
  selected.value = await api.getProduct(id)
  showDrawer.value = true
}

onMounted(loadProducts)
</script>

