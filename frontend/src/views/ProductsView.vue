<template>
  <section class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">商品管理</h1>
        <p class="page-subtitle">维护商品、SKU、库存和售后标签。</p>
      </div>
      <div class="toolbar">
        <n-input v-model:value="keyword" placeholder="搜索商品" clearable />
        <n-button secondary @click="loadProducts">搜索</n-button>
        <n-button type="primary" @click="openCreate">新增商品</n-button>
      </div>
    </div>

    <n-card size="small">
      <n-data-table :columns="columns" :data="products" :pagination="{ pageSize: 8 }" />
    </n-card>

    <n-drawer v-model:show="showDetailDrawer" :width="420">
      <n-drawer-content title="商品详情">
        <n-descriptions v-if="selected" bordered :column="1" size="small">
          <n-descriptions-item label="名称">{{ selected.name }}</n-descriptions-item>
          <n-descriptions-item label="SKU">{{ selected.sku }}</n-descriptions-item>
          <n-descriptions-item label="类目">{{ selected.category }}</n-descriptions-item>
          <n-descriptions-item label="价格">{{ selected.price }}</n-descriptions-item>
          <n-descriptions-item label="库存">{{ selected.stock }}</n-descriptions-item>
          <n-descriptions-item label="状态">{{ selected.status }}</n-descriptions-item>
          <n-descriptions-item label="售后">{{ selected.after_sale_policy }}</n-descriptions-item>
          <n-descriptions-item label="描述">{{ selected.description }}</n-descriptions-item>
        </n-descriptions>
      </n-drawer-content>
    </n-drawer>

    <n-drawer v-model:show="showFormDrawer" :width="520">
      <n-drawer-content :title="editingId ? '编辑商品' : '新增商品'">
        <n-form label-placement="top">
          <n-form-item label="商品名称">
            <n-input v-model:value="form.name" />
          </n-form-item>
          <n-form-item label="SKU">
            <n-input v-model:value="form.sku" />
          </n-form-item>
          <n-form-item label="类目">
            <n-input v-model:value="form.category" />
          </n-form-item>
          <n-form-item label="价格">
            <n-input-number v-model:value="form.price" :min="0" />
          </n-form-item>
          <n-form-item label="库存">
            <n-input-number v-model:value="form.stock" :min="0" />
          </n-form-item>
          <n-form-item label="状态">
            <n-select v-model:value="form.status" :options="statusOptions" />
          </n-form-item>
          <n-form-item label="售后规则">
            <n-input v-model:value="form.after_sale_policy" type="textarea" />
          </n-form-item>
          <n-form-item label="描述">
            <n-input v-model:value="form.description" type="textarea" />
          </n-form-item>
          <n-space>
            <n-button type="primary" @click="saveProduct">保存</n-button>
            <n-button @click="showFormDrawer = false">取消</n-button>
          </n-space>
        </n-form>
      </n-drawer-content>
    </n-drawer>
  </section>
</template>

<script setup lang="ts">
import { h, onMounted, reactive, ref } from 'vue'
import type { DataTableColumns } from 'naive-ui'
import {
  NButton,
  NCard,
  NDataTable,
  NDescriptions,
  NDescriptionsItem,
  NDrawer,
  NDrawerContent,
  NForm,
  NFormItem,
  NInput,
  NInputNumber,
  NPopconfirm,
  NSelect,
  NSpace,
  NTag,
  useMessage
} from 'naive-ui'

import { api, type Product, type ProductPayload } from '@/api/client'

const message = useMessage()
const keyword = ref('')
const products = ref<Product[]>([])
const selected = ref<Product | null>(null)
const showDetailDrawer = ref(false)
const showFormDrawer = ref(false)
const editingId = ref<number | null>(null)

const form = reactive<ProductPayload>({
  name: '',
  sku: '',
  category: '',
  description: '',
  price: 0,
  stock: 0,
  after_sale_policy: '',
  status: 'active'
})

const statusOptions = [
  { label: 'active', value: 'active' },
  { label: 'inactive', value: 'inactive' }
]

const columns: DataTableColumns<Product> = [
  { title: 'ID', key: 'id', width: 70 },
  { title: '商品', key: 'name' },
  { title: 'SKU', key: 'sku' },
  { title: '类目', key: 'category' },
  { title: '价格', key: 'price' },
  { title: '库存', key: 'stock' },
  { title: '状态', key: 'status', render: (row) => h(NTag, { type: row.status === 'active' ? 'success' : 'warning', size: 'small' }, { default: () => row.status }) },
  {
    title: '操作',
    key: 'actions',
    width: 210,
    render: (row) =>
      h(NSpace, { size: 8 }, {
        default: () => [
          h(NButton, { size: 'small', onClick: () => openDetail(row.id) }, { default: () => '详情' }),
          h(NButton, { size: 'small', type: 'primary', secondary: true, onClick: () => openEdit(row) }, { default: () => '编辑' }),
          h(
            NPopconfirm,
            { onPositiveClick: () => removeProduct(row.id) },
            {
              trigger: () => h(NButton, { size: 'small', type: 'error', secondary: true }, { default: () => '删除' }),
              default: () => '确认删除该商品？'
            }
          )
        ]
      })
  }
]

async function loadProducts() {
  products.value = await api.getProducts(keyword.value)
}

async function openDetail(id: number) {
  selected.value = await api.getProduct(id)
  showDetailDrawer.value = true
}

function openCreate() {
  editingId.value = null
  Object.assign(form, {
    name: '',
    sku: '',
    category: '',
    description: '',
    price: 0,
    stock: 0,
    after_sale_policy: '',
    status: 'active'
  })
  showFormDrawer.value = true
}

function openEdit(row: Product) {
  editingId.value = row.id
  Object.assign(form, {
    name: row.name,
    sku: row.sku,
    category: row.category,
    description: row.description || '',
    price: row.price,
    stock: row.stock,
    after_sale_policy: row.after_sale_policy || '',
    status: row.status
  })
  showFormDrawer.value = true
}

async function saveProduct() {
  if (editingId.value) {
    await api.updateProduct(editingId.value, form)
    message.success('商品已更新')
  } else {
    await api.createProduct(form)
    message.success('商品已新增')
  }
  showFormDrawer.value = false
  await loadProducts()
}

async function removeProduct(id: number) {
  await api.deleteProduct(id)
  message.success('商品已删除')
  await loadProducts()
}

onMounted(loadProducts)
</script>

