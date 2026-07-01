<template>
  <section class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">{{ t('products.title') }}</h1>
        <p class="page-subtitle">{{ t('products.subtitle') }}</p>
      </div>
      <div class="toolbar">
        <n-input v-model:value="keyword" :placeholder="t('products.searchPlaceholder')" clearable />
        <n-button secondary @click="loadProducts">{{ t('common.search') }}</n-button>
        <n-button type="primary" @click="openCreate">{{ t('products.newProduct') }}</n-button>
      </div>
    </div>

    <n-card size="small">
      <n-data-table :columns="columns" :data="products" :pagination="{ pageSize: 8 }" />
    </n-card>

    <n-drawer v-model:show="showDetailDrawer" :width="420">
      <n-drawer-content :title="t('products.productDetail')">
        <n-descriptions v-if="selected" bordered :column="1" size="small">
          <n-descriptions-item :label="t('products.productName')">{{ productName(selected) }}</n-descriptions-item>
          <n-descriptions-item label="SKU">{{ selected.sku }}</n-descriptions-item>
          <n-descriptions-item :label="t('common.category')">{{ productCategory(selected) }}</n-descriptions-item>
          <n-descriptions-item :label="t('common.price')">{{ selected.price }}</n-descriptions-item>
          <n-descriptions-item :label="t('common.stock')">{{ selected.stock }}</n-descriptions-item>
          <n-descriptions-item :label="t('common.status')">{{ statusLabel(selected.status) }}</n-descriptions-item>
          <n-descriptions-item :label="t('products.afterSalesPolicy')">{{ productPolicy(selected) }}</n-descriptions-item>
          <n-descriptions-item :label="t('common.description')">{{ productDescription(selected) }}</n-descriptions-item>
        </n-descriptions>
      </n-drawer-content>
    </n-drawer>

    <n-drawer v-model:show="showFormDrawer" :width="520">
      <n-drawer-content :title="editingId ? t('products.editProduct') : t('products.newProduct')">
        <n-form label-placement="top">
          <n-form-item :label="t('products.productName')">
            <n-input v-model:value="form.name" />
          </n-form-item>
          <n-form-item label="SKU">
            <n-input v-model:value="form.sku" />
          </n-form-item>
          <n-form-item :label="t('common.category')">
            <n-input v-model:value="form.category" />
          </n-form-item>
          <n-form-item :label="t('common.price')">
            <n-input-number v-model:value="form.price" :min="0" />
          </n-form-item>
          <n-form-item :label="t('common.stock')">
            <n-input-number v-model:value="form.stock" :min="0" />
          </n-form-item>
          <n-form-item :label="t('common.status')">
            <n-select v-model:value="form.status" :options="statusOptions" />
          </n-form-item>
          <n-form-item :label="t('products.afterSalesPolicy')">
            <n-input v-model:value="form.after_sale_policy" type="textarea" />
          </n-form-item>
          <n-form-item :label="t('common.description')">
            <n-input v-model:value="form.description" type="textarea" />
          </n-form-item>
          <n-space>
            <n-button type="primary" @click="saveProduct">{{ t('common.save') }}</n-button>
            <n-button @click="showFormDrawer = false">{{ t('common.cancel') }}</n-button>
          </n-space>
        </n-form>
      </n-drawer-content>
    </n-drawer>
  </section>
</template>

<script setup lang="ts">
import { computed, h, onMounted, reactive, ref } from 'vue'
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
import { useI18n } from 'vue-i18n'

import { api, type Product, type ProductPayload } from '@/api/client'
import { useDisplayText } from '@/i18n/display'

const message = useMessage()
const { t } = useI18n()
const { productName, productCategory, productDescription, productPolicy, statusLabel } = useDisplayText()
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

const statusOptions = computed(() => [
  { label: statusLabel('active'), value: 'active' },
  { label: statusLabel('inactive'), value: 'inactive' }
])

const columns = computed<DataTableColumns<Product>>(() => [
  { title: t('common.id'), key: 'id', width: 70 },
  { title: t('products.product'), key: 'name', render: (row) => productName(row) },
  { title: 'SKU', key: 'sku' },
  { title: t('common.category'), key: 'category', render: (row) => productCategory(row) },
  { title: t('common.price'), key: 'price' },
  { title: t('common.stock'), key: 'stock' },
  {
    title: t('common.status'),
    key: 'status',
    render: (row) => h(NTag, { type: row.status === 'active' ? 'success' : 'warning', size: 'small' }, { default: () => statusLabel(row.status) })
  },
  {
    title: t('common.actions'),
    key: 'actions',
    width: 220,
    render: (row) =>
      h(NSpace, { size: 8 }, {
        default: () => [
          h(NButton, { size: 'small', onClick: () => openDetail(row.id) }, { default: () => t('common.detail') }),
          h(NButton, { size: 'small', type: 'primary', secondary: true, onClick: () => openEdit(row) }, { default: () => t('common.edit') }),
          h(
            NPopconfirm,
            { onPositiveClick: () => removeProduct(row.id) },
            {
              trigger: () => h(NButton, { size: 'small', type: 'error', secondary: true }, { default: () => t('common.delete') }),
              default: () => t('products.deleteConfirm')
            }
          )
        ]
      })
  }
])

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
    message.success(t('products.updated'))
  } else {
    await api.createProduct(form)
    message.success(t('products.created'))
  }
  showFormDrawer.value = false
  await loadProducts()
}

async function removeProduct(id: number) {
  await api.deleteProduct(id)
  message.success(t('products.deleted'))
  await loadProducts()
}

onMounted(loadProducts)
</script>
