<template>
  <section class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">订单管理</h1>
        <p class="page-subtitle">维护订单、物流状态和售后状态。</p>
      </div>
      <div class="toolbar">
        <n-button secondary @click="loadOrders">刷新</n-button>
        <n-button type="primary" @click="openCreate">新增订单</n-button>
      </div>
    </div>

    <n-card size="small">
      <n-data-table :columns="columns" :data="orders" :pagination="{ pageSize: 8 }" />
    </n-card>

    <n-drawer v-model:show="showDetailDrawer" :width="480">
      <n-drawer-content title="订单详情">
        <n-descriptions v-if="selected" bordered :column="1" size="small">
          <n-descriptions-item label="订单号">{{ selected.order_no }}</n-descriptions-item>
          <n-descriptions-item label="用户 ID">{{ selected.user_id }}</n-descriptions-item>
          <n-descriptions-item label="商品">{{ selected.product?.name }}</n-descriptions-item>
          <n-descriptions-item label="数量">{{ selected.quantity }}</n-descriptions-item>
          <n-descriptions-item label="金额">{{ selected.total_amount }}</n-descriptions-item>
          <n-descriptions-item label="订单状态">{{ selected.order_status }}</n-descriptions-item>
          <n-descriptions-item label="支付状态">{{ selected.payment_status }}</n-descriptions-item>
          <n-descriptions-item label="物流状态">{{ selected.logistics_status }}</n-descriptions-item>
          <n-descriptions-item label="物流单号">{{ selected.tracking_no }}</n-descriptions-item>
          <n-descriptions-item label="签收时间">{{ selected.delivered_at || '-' }}</n-descriptions-item>
          <n-descriptions-item label="售后状态">{{ selected.after_sale_status }}</n-descriptions-item>
        </n-descriptions>
      </n-drawer-content>
    </n-drawer>

    <n-drawer v-model:show="showFormDrawer" :width="560">
      <n-drawer-content :title="editingId ? '编辑订单' : '新增订单'">
        <n-form label-placement="top">
          <n-form-item label="订单号">
            <n-input v-model:value="form.order_no" />
          </n-form-item>
          <n-grid :cols="2" :x-gap="12">
            <n-form-item-gi label="用户 ID">
              <n-input-number v-model:value="form.user_id" :min="1" />
            </n-form-item-gi>
            <n-form-item-gi label="商品 ID">
              <n-input-number v-model:value="form.product_id" :min="1" />
            </n-form-item-gi>
          </n-grid>
          <n-grid :cols="2" :x-gap="12">
            <n-form-item-gi label="数量">
              <n-input-number v-model:value="form.quantity" :min="1" />
            </n-form-item-gi>
            <n-form-item-gi label="金额">
              <n-input-number v-model:value="form.total_amount" :min="0" />
            </n-form-item-gi>
          </n-grid>
          <n-grid :cols="2" :x-gap="12">
            <n-form-item-gi label="订单状态">
              <n-select v-model:value="form.order_status" :options="orderStatusOptions" />
            </n-form-item-gi>
            <n-form-item-gi label="支付状态">
              <n-select v-model:value="form.payment_status" :options="paymentStatusOptions" />
            </n-form-item-gi>
          </n-grid>
          <n-grid :cols="2" :x-gap="12">
            <n-form-item-gi label="物流状态">
              <n-select v-model:value="form.logistics_status" :options="logisticsStatusOptions" />
            </n-form-item-gi>
            <n-form-item-gi label="售后状态">
              <n-select v-model:value="form.after_sale_status" :options="afterSaleStatusOptions" />
            </n-form-item-gi>
          </n-grid>
          <n-form-item label="物流单号">
            <n-input v-model:value="form.tracking_no" />
          </n-form-item>
          <n-space>
            <n-button type="primary" @click="saveOrder">保存</n-button>
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

import { api, type Order, type OrderPayload } from '@/api/client'

const message = useMessage()
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

const orderStatusOptions = ['pending', 'paid', 'shipped', 'delivered', 'closed'].map(toOption)
const paymentStatusOptions = ['unpaid', 'paid', 'refunded'].map(toOption)
const logisticsStatusOptions = ['pending', 'shipped', 'delivered'].map(toOption)
const afterSaleStatusOptions = ['none', 'applying', 'processing', 'done', 'rejected'].map(toOption)

const columns: DataTableColumns<Order> = [
  { title: '订单号', key: 'order_no' },
  { title: '用户', key: 'user_id', width: 80 },
  { title: '商品', key: 'product_id', width: 80 },
  { title: '金额', key: 'total_amount' },
  { title: '订单状态', key: 'order_status' },
  { title: '物流', key: 'logistics_status', render: (row) => h(NTag, { size: 'small' }, { default: () => row.logistics_status }) },
  { title: '售后', key: 'after_sale_status' },
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
            { onPositiveClick: () => removeOrder(row.id) },
            {
              trigger: () => h(NButton, { size: 'small', type: 'error', secondary: true }, { default: () => '删除' }),
              default: () => '确认删除该订单？'
            }
          )
        ]
      })
  }
]

function toOption(value: string) {
  return { label: value, value }
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
    message.success('订单已更新')
  } else {
    await api.createOrder(form)
    message.success('订单已新增')
  }
  showFormDrawer.value = false
  await loadOrders()
}

async function removeOrder(id: number) {
  await api.deleteOrder(id)
  message.success('订单已删除')
  await loadOrders()
}

onMounted(loadOrders)
</script>

