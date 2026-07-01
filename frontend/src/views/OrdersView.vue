<template>
  <section class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">{{ t('orders.title') }}</h1>
        <p class="page-subtitle">{{ t('orders.subtitle') }}</p>
      </div>
      <div class="toolbar">
        <n-button secondary @click="loadOrders">{{ t('common.refresh') }}</n-button>
        <n-button type="primary" @click="openCreate">{{ t('orders.newOrder') }}</n-button>
      </div>
    </div>

    <n-card size="small">
      <n-data-table :columns="columns" :data="orders" :pagination="{ pageSize: 8 }" />
    </n-card>

    <n-drawer v-model:show="showDetailDrawer" :width="480">
      <n-drawer-content :title="t('orders.orderDetail')">
        <n-descriptions v-if="selected" bordered :column="1" size="small">
          <n-descriptions-item :label="t('orders.orderNo')">{{ selected.order_no }}</n-descriptions-item>
          <n-descriptions-item :label="t('orders.userId')">{{ selected.user_id }}</n-descriptions-item>
          <n-descriptions-item :label="t('products.product')">{{ selected.product ? productName(selected.product) : selected.product_id }}</n-descriptions-item>
          <n-descriptions-item :label="t('orders.quantity')">{{ selected.quantity }}</n-descriptions-item>
          <n-descriptions-item :label="t('orders.amount')">{{ selected.total_amount }}</n-descriptions-item>
          <n-descriptions-item :label="t('orders.orderStatus')">{{ statusLabel(selected.order_status) }}</n-descriptions-item>
          <n-descriptions-item :label="t('orders.paymentStatus')">{{ statusLabel(selected.payment_status) }}</n-descriptions-item>
          <n-descriptions-item :label="t('orders.logisticsStatus')">{{ statusLabel(selected.logistics_status) }}</n-descriptions-item>
          <n-descriptions-item :label="t('orders.trackingNo')">{{ selected.tracking_no || '-' }}</n-descriptions-item>
          <n-descriptions-item :label="t('orders.deliveredAt')">{{ selected.delivered_at || '-' }}</n-descriptions-item>
          <n-descriptions-item :label="t('orders.afterSaleStatus')">{{ statusLabel(selected.after_sale_status) }}</n-descriptions-item>
        </n-descriptions>
      </n-drawer-content>
    </n-drawer>

    <n-drawer v-model:show="showFormDrawer" :width="560">
      <n-drawer-content :title="editingId ? t('orders.editOrder') : t('orders.newOrder')">
        <n-form label-placement="top">
          <n-form-item :label="t('orders.orderNo')">
            <n-input v-model:value="form.order_no" />
          </n-form-item>
          <n-grid :cols="2" :x-gap="12">
            <n-form-item-gi :label="t('orders.userId')">
              <n-input-number v-model:value="form.user_id" :min="1" />
            </n-form-item-gi>
            <n-form-item-gi :label="t('orders.productId')">
              <n-input-number v-model:value="form.product_id" :min="1" />
            </n-form-item-gi>
          </n-grid>
          <n-grid :cols="2" :x-gap="12">
            <n-form-item-gi :label="t('orders.quantity')">
              <n-input-number v-model:value="form.quantity" :min="1" />
            </n-form-item-gi>
            <n-form-item-gi :label="t('orders.amount')">
              <n-input-number v-model:value="form.total_amount" :min="0" />
            </n-form-item-gi>
          </n-grid>
          <n-grid :cols="2" :x-gap="12">
            <n-form-item-gi :label="t('orders.orderStatus')">
              <n-select v-model:value="form.order_status" :options="orderStatusOptions" />
            </n-form-item-gi>
            <n-form-item-gi :label="t('orders.paymentStatus')">
              <n-select v-model:value="form.payment_status" :options="paymentStatusOptions" />
            </n-form-item-gi>
          </n-grid>
          <n-grid :cols="2" :x-gap="12">
            <n-form-item-gi :label="t('orders.logisticsStatus')">
              <n-select v-model:value="form.logistics_status" :options="logisticsStatusOptions" />
            </n-form-item-gi>
            <n-form-item-gi :label="t('orders.afterSaleStatus')">
              <n-select v-model:value="form.after_sale_status" :options="afterSaleStatusOptions" />
            </n-form-item-gi>
          </n-grid>
          <n-form-item :label="t('orders.trackingNo')">
            <n-input v-model:value="form.tracking_no" />
          </n-form-item>
          <n-space>
            <n-button type="primary" @click="saveOrder">{{ t('common.save') }}</n-button>
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
  NFormItemGi,
  NGrid,
  NInput,
  NInputNumber,
  NPopconfirm,
  NSelect,
  NSpace,
  NTag,
  useMessage
} from 'naive-ui'
import { useI18n } from 'vue-i18n'

import { api, type Order, type OrderPayload } from '@/api/client'
import { useDisplayText } from '@/i18n/display'

const message = useMessage()
const { t } = useI18n()
const { productName, statusLabel } = useDisplayText()
const orders = ref<Order[]>([])
const selected = ref<Order | null>(null)
const showDetailDrawer = ref(false)
const showFormDrawer = ref(false)
const editingId = ref<number | null>(null)

const form = reactive<OrderPayload>({
  order_no: '',
  user_id: 1,
  product_id: 1,
  quantity: 1,
  total_amount: 0,
  order_status: 'paid',
  payment_status: 'paid',
  logistics_status: 'pending',
  tracking_no: '',
  paid_at: null,
  shipped_at: null,
  delivered_at: null,
  after_sale_status: 'none'
})

const orderStatusOptions = computed(() => ['pending', 'paid', 'shipped', 'delivered', 'closed'].map(toOption))
const paymentStatusOptions = computed(() => ['unpaid', 'paid', 'refunded'].map(toOption))
const logisticsStatusOptions = computed(() => ['pending', 'shipped', 'delivered'].map(toOption))
const afterSaleStatusOptions = computed(() => ['none', 'applying', 'processing', 'done', 'rejected'].map(toOption))

const columns = computed<DataTableColumns<Order>>(() => [
  { title: t('orders.orderNo'), key: 'order_no' },
  { title: t('common.user'), key: 'user_id', width: 80 },
  { title: t('products.product'), key: 'product_id', render: (row) => (row.product ? productName(row.product) : row.product_id) },
  { title: t('orders.amount'), key: 'total_amount' },
  { title: t('orders.orderStatus'), key: 'order_status', render: (row) => statusLabel(row.order_status) },
  {
    title: t('orders.logistics'),
    key: 'logistics_status',
    render: (row) => h(NTag, { size: 'small' }, { default: () => statusLabel(row.logistics_status) })
  },
  { title: t('orders.afterSales'), key: 'after_sale_status', render: (row) => statusLabel(row.after_sale_status) },
  {
    title: t('common.actions'),
    key: 'actions',
    width: 210,
    render: (row) =>
      h(NSpace, { size: 8 }, {
        default: () => [
          h(NButton, { size: 'small', onClick: () => openDetail(row.id) }, { default: () => t('common.detail') }),
          h(NButton, { size: 'small', type: 'primary', secondary: true, onClick: () => openEdit(row) }, { default: () => t('common.edit') }),
          h(
            NPopconfirm,
            { onPositiveClick: () => removeOrder(row.id) },
            {
              trigger: () => h(NButton, { size: 'small', type: 'error', secondary: true }, { default: () => t('common.delete') }),
              default: () => t('orders.deleteConfirm')
            }
          )
        ]
      })
  }
])

function toOption(value: string) {
  return { label: statusLabel(value), value }
}

async function loadOrders() {
  orders.value = await api.getOrders()
}

async function openDetail(id: number) {
  selected.value = await api.getOrder(id)
  showDetailDrawer.value = true
}

function openCreate() {
  editingId.value = null
  Object.assign(form, {
    order_no: `MOCK${Date.now()}`,
    user_id: 1,
    product_id: 1,
    quantity: 1,
    total_amount: 399,
    order_status: 'paid',
    payment_status: 'paid',
    logistics_status: 'pending',
    tracking_no: '',
    paid_at: null,
    shipped_at: null,
    delivered_at: null,
    after_sale_status: 'none'
  })
  showFormDrawer.value = true
}

function openEdit(row: Order) {
  editingId.value = row.id
  Object.assign(form, {
    order_no: row.order_no,
    user_id: row.user_id,
    product_id: row.product_id,
    quantity: row.quantity,
    total_amount: row.total_amount,
    order_status: row.order_status,
    payment_status: row.payment_status,
    logistics_status: row.logistics_status,
    tracking_no: row.tracking_no || '',
    paid_at: row.paid_at,
    shipped_at: row.shipped_at,
    delivered_at: row.delivered_at,
    after_sale_status: row.after_sale_status
  })
  showFormDrawer.value = true
}

async function saveOrder() {
  if (editingId.value) {
    await api.updateOrder(editingId.value, form)
    message.success(t('orders.updated'))
  } else {
    await api.createOrder(form)
    message.success(t('orders.created'))
  }
  showFormDrawer.value = false
  await loadOrders()
}

async function removeOrder(id: number) {
  await api.deleteOrder(id)
  message.success(t('orders.deleted'))
  await loadOrders()
}

onMounted(loadOrders)
</script>
