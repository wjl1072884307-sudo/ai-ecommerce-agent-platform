import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import type { KnowledgeChunk, KnowledgeDocument, Product, SessionItem } from '@/api/client'

type LocalizedText = {
  en: string
  zh: string
}

const productCatalog: Record<string, { name: LocalizedText; category: LocalizedText; description: LocalizedText; policy: LocalizedText }> = {
  'AUDIO-NEBULA-001': {
    name: { en: 'Nebula Noise-Cancelling Headset', zh: '星云降噪耳机' },
    category: { en: 'Digital Audio', zh: '数码音频' },
    description: {
      en: 'Wireless noise-cancelling headset for commuting and remote meetings.',
      zh: '适合通勤和远程会议的无线降噪耳机。'
    },
    policy: {
      en: '7-day no-reason return if unused; 15-day replacement for verified quality issues.',
      zh: '未使用可 7 天无理由退货；确认质量问题可 15 天换新。'
    }
  },
  'PHONE-AURORA-PRO': {
    name: { en: 'Aurora Pro Smartphone', zh: '极光 Pro 手机' },
    category: { en: 'Smartphone', zh: '手机数码' },
    description: {
      en: 'Flagship smartphone with high-refresh display and fast charging.',
      zh: '配备高刷新率屏幕和快充能力的旗舰手机。'
    },
    policy: {
      en: 'Unopened devices support 7-day return; activated devices follow quality inspection rules.',
      zh: '未拆封支持 7 天退货；已激活设备按质检规则处理。'
    }
  },
  'KEYBOARD-BLUE-001': {
    name: { en: 'Blue Switch Mechanical Keyboard', zh: '青轴机械键盘' },
    category: { en: 'Computer Peripheral', zh: '电脑外设' },
    description: {
      en: 'Mechanical keyboard with tactile blue switches and backlight.',
      zh: '带背光的青轴机械键盘，适合办公和游戏。'
    },
    policy: {
      en: 'Supports return within 7 days if accessories are complete and key switches are not damaged.',
      zh: '配件齐全且轴体无损坏时，支持 7 天内退货。'
    }
  },
  'MONITOR-AURORA-027': {
    name: { en: 'Aurora 27-inch Monitor', zh: '极光 27 英寸显示器' },
    category: { en: 'Computer Display', zh: '电脑显示器' },
    description: {
      en: '27-inch monitor for office work, design review, and gaming.',
      zh: '适合办公、设计预览和游戏的 27 英寸显示器。'
    },
    policy: {
      en: 'Dead pixels, screen flicker, or power faults can be handled through replacement review.',
      zh: '坏点、闪屏或电源故障可进入换货审核。'
    }
  },
  'WATCH-PULSE-FIT': {
    name: { en: 'Pulse Fit Smartwatch', zh: 'Pulse Fit 智能手表' },
    category: { en: 'Wearable', zh: '智能穿戴' },
    description: {
      en: 'Smartwatch with fitness tracking and notification sync.',
      zh: '支持运动记录和消息同步的智能手表。'
    },
    policy: {
      en: 'Battery or sensor faults can be reviewed for replacement within 15 days.',
      zh: '电池或传感器故障可在 15 天内申请换货审核。'
    }
  },
  'CHARGER-GAN-065': {
    name: { en: 'GaN Fast Charger 65W', zh: '65W 氮化镓快充' },
    category: { en: 'Phone Accessory', zh: '手机配件' },
    description: {
      en: 'Compact 65W GaN charger for phones, tablets, and laptops.',
      zh: '适用于手机、平板和轻薄本的 65W 小型氮化镓充电器。'
    },
    policy: {
      en: 'Charging failure or abnormal heat can be submitted for after-sales inspection.',
      zh: '无法充电或异常发热可提交售后检测。'
    }
  },
  'SPEAKER-MINI-BT': {
    name: { en: 'Mini Bluetooth Speaker', zh: '迷你蓝牙音箱' },
    category: { en: 'Audio', zh: '音频设备' },
    description: {
      en: 'Portable Bluetooth speaker for desktop and outdoor use.',
      zh: '适合桌面和户外使用的便携蓝牙音箱。'
    },
    policy: {
      en: 'Crackling sound, pairing failure, or water damage requires manual after-sales review.',
      zh: '杂音、无法配对或进水问题需进入人工售后审核。'
    }
  }
}

const sessionTitles: Record<string, LocalizedText> = {
  'Headset after-sales consultation': { en: 'Headset after-sales consultation', zh: '耳机售后咨询' },
  '耳机售后咨询': { en: 'Headset after-sales consultation', zh: '耳机售后咨询' },
  'Monitor logistics delay': { en: 'Monitor logistics delay', zh: '显示器物流延迟' },
  'Smartwatch battery complaint': { en: 'Smartwatch battery complaint', zh: '智能手表电池投诉' },
  'Charger invoice request': { en: 'Charger invoice request', zh: '充电器发票申请' },
  'Speaker refund follow-up': { en: 'Speaker refund follow-up', zh: '音箱退款跟进' }
}

const knowledgeDocs: Record<string, { title: LocalizedText; type: LocalizedText; chunks: LocalizedText[] }> = {
  return_refund: {
    title: { en: 'Return and Refund Policy', zh: '退货退款基础政策' },
    type: { en: 'Policy', zh: '政策' },
    chunks: [
      {
        en: 'Consumers may request a 7-day no-reason return after receiving goods when the product is intact and does not affect resale.',
        zh: '消费者签收商品后 7 天内，在商品完好且不影响二次销售的情况下，可以申请 7 天无理由退货。'
      },
      {
        en: 'If a product has quality issues such as headset noise, connection failure, or button failure, customers may request return or replacement within 15 days after signing.',
        zh: '如果商品存在质量问题，例如耳机杂音、无法连接、按键失灵等，用户可在签收后 15 天内申请退货或换货。'
      },
      {
        en: 'Requests beyond the after-sales window or involving higher refund amounts require manual review before the final handling result is issued.',
        zh: '超过售后期限或订单金额较高的申请，需要人工审核后再给出最终处理结果。'
      }
    ]
  },
  logistics: {
    title: { en: 'Logistics Inquiry Handling Rules', zh: '物流查询处理规范' },
    type: { en: 'Logistics', zh: '物流' },
    chunks: [
      {
        en: 'When users ask about logistics, customer service should first check the order logistics status and tracking number.',
        zh: '用户咨询物流时，客服应优先查询订单物流状态和物流单号。'
      },
      {
        en: 'If a shipped order has not updated for a long time, create a logistics exception ticket and tell the user customer service will follow up.',
        zh: '如果订单已发货但长时间未更新，应创建物流异常工单，并提示用户客服会继续跟进。'
      }
    ]
  },
  complaint: {
    title: { en: 'Complaint Handling Rules', zh: '投诉问题处理规范' },
    type: { en: 'Complaint', zh: '投诉' },
    chunks: [
      {
        en: 'For complaint requests, record the problem, order context, and expected resolution before deciding whether manual review is required.',
        zh: '处理投诉时，应记录问题、订单背景和用户期望，再判断是否需要人工审核。'
      }
    ]
  },
  screen_protector: {
    title: { en: 'Phone Screen Protector After-sales Policy', zh: '手机屏幕保护膜售后政策' },
    type: { en: 'Policy', zh: '政策' },
    chunks: [
      {
        en: 'Screen protector issues such as bubbles, edge lifting, or wrong model can be handled according to accessory after-sales rules.',
        zh: '保护膜出现气泡、翘边或型号不匹配时，可按配件售后规则处理。'
      }
    ]
  }
}

const knowledgeTitleKeys: Record<string, keyof typeof knowledgeDocs> = {
  '退货退款基础政策': 'return_refund',
  'Return and Refund Policy': 'return_refund',
  '物流查询处理规范': 'logistics',
  'Logistics Inquiry Handling Rules': 'logistics',
  '投诉问题处理规范': 'complaint',
  'Complaint Handling Rules': 'complaint',
  '手机屏幕保护膜售后政策': 'screen_protector',
  'Phone Screen Protector After-sales Policy': 'screen_protector'
}

const statusLabels: Record<string, LocalizedText> = {
  active: { en: 'active', zh: '启用' },
  inactive: { en: 'inactive', zh: '停用' },
  open: { en: 'open', zh: '打开' },
  closed: { en: 'closed', zh: '已关闭' },
  pending: { en: 'pending', zh: '待处理' },
  paid: { en: 'paid', zh: '已支付' },
  unpaid: { en: 'unpaid', zh: '未支付' },
  shipped: { en: 'shipped', zh: '已发货' },
  delivered: { en: 'delivered', zh: '已签收' },
  refunded: { en: 'refunded', zh: '已退款' },
  none: { en: 'none', zh: '无' },
  applying: { en: 'applying', zh: '申请中' },
  processing: { en: 'processing', zh: '处理中' },
  done: { en: 'done', zh: '已完成' },
  rejected: { en: 'rejected', zh: '已拒绝' },
  resolved: { en: 'resolved', zh: '已解决' },
  cancelled: { en: 'cancelled', zh: '已取消' },
  success: { en: 'success', zh: '成功' },
  failed: { en: 'failed', zh: '失败' },
  error: { en: 'error', zh: '错误' },
  completed: { en: 'completed', zh: '已完成' },
  ok: { en: 'ok', zh: '正常' },
  checking: { en: 'checking', zh: '检查中' },
  high: { en: 'high', zh: '高' },
  medium: { en: 'medium', zh: '中' },
  low: { en: 'low', zh: '低' },
  return: { en: 'return', zh: '退货' },
  refund: { en: 'refund', zh: '退款' },
  complaint: { en: 'complaint', zh: '投诉' },
  logistics: { en: 'logistics', zh: '物流' }
}

function normalize(value: string | null | undefined) {
  return (value || '').trim()
}

function pick(text: LocalizedText, locale: string) {
  return locale === 'zh' ? text.zh : text.en
}

function knowledgeKeyFromDocument(document: Pick<KnowledgeDocument, 'title' | 'document_type'>) {
  return knowledgeTitleKeys[normalize(document.title)] || (normalize(document.document_type) as keyof typeof knowledgeDocs)
}

export function useDisplayText() {
  const { locale } = useI18n()
  const currentLocale = computed(() => String(locale.value))
  const localize = (text: LocalizedText) => pick(text, currentLocale.value)

  function productName(product: Pick<Product, 'sku' | 'name'>) {
    return productCatalog[product.sku]?.name ? localize(productCatalog[product.sku].name) : product.name
  }

  function productCategory(product: Pick<Product, 'sku' | 'category'>) {
    return productCatalog[product.sku]?.category ? localize(productCatalog[product.sku].category) : product.category
  }

  function productDescription(product: Pick<Product, 'sku' | 'description'>) {
    return productCatalog[product.sku]?.description ? localize(productCatalog[product.sku].description) : product.description || '-'
  }

  function productPolicy(product: Pick<Product, 'sku' | 'after_sale_policy'>) {
    return productCatalog[product.sku]?.policy ? localize(productCatalog[product.sku].policy) : product.after_sale_policy || '-'
  }

  function sessionTitle(session: Pick<SessionItem, 'title'>) {
    return sessionTitles[normalize(session.title)] ? localize(sessionTitles[normalize(session.title)]) : session.title
  }

  function knowledgeTitle(document: Pick<KnowledgeDocument, 'title' | 'document_type'> | Pick<KnowledgeChunk, 'document_title' | 'document_type'>) {
    if ('title' in document) {
      const key = knowledgeKeyFromDocument(document)
      return knowledgeDocs[key]?.title ? localize(knowledgeDocs[key].title) : document.title
    }
    const key = knowledgeTitleKeys[normalize(document.document_title)] || (normalize(document.document_type) as keyof typeof knowledgeDocs)
    return knowledgeDocs[key]?.title ? localize(knowledgeDocs[key].title) : document.document_title || '-'
  }

  function knowledgeType(document: Pick<KnowledgeDocument, 'title' | 'document_type'>) {
    const key = knowledgeKeyFromDocument(document)
    return knowledgeDocs[key]?.type ? localize(knowledgeDocs[key].type) : statusLabel(document.document_type)
  }

  function knowledgeContent(document: Pick<KnowledgeDocument, 'title' | 'document_type' | 'content'>) {
    const key = knowledgeKeyFromDocument(document)
    const chunks = knowledgeDocs[key]?.chunks
    return chunks ? chunks.map(localize).join('\n') : document.content
  }

  function knowledgeChunk(chunk: KnowledgeChunk) {
    const key = knowledgeTitleKeys[normalize(chunk.document_title)] || (normalize(chunk.document_type) as keyof typeof knowledgeDocs)
    const localized = knowledgeDocs[key]?.chunks[chunk.chunk_index]
    return localized ? localize(localized) : chunk.content
  }

  function statusLabel(value: string | null | undefined) {
    const key = normalize(value)
    return statusLabels[key] ? localize(statusLabels[key]) : key || '-'
  }

  return {
    productName,
    productCategory,
    productDescription,
    productPolicy,
    sessionTitle,
    knowledgeTitle,
    knowledgeType,
    knowledgeContent,
    knowledgeChunk,
    statusLabel
  }
}
