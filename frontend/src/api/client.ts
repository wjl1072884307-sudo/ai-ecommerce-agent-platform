import axios from 'axios'
import { createDiscreteApi } from 'naive-ui'

const { message } = createDiscreteApi(['message'])

export const apiClient = axios.create({
  baseURL: '/api',
  timeout: 10000
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const detail = error.response?.data?.detail
    const fallback = error.message || '请求失败，请稍后重试'
    message.error(typeof detail === 'string' ? detail : fallback)
    return Promise.reject(error)
  }
)

export interface Product {
  id: number
  name: string
  sku: string
  category: string
  description: string | null
  price: number
  stock: number
  after_sale_policy: string | null
  status: string
}

export interface Order {
  id: number
  order_no: string
  user_id: number
  product_id: number
  quantity: number
  total_amount: number
  order_status: string
  payment_status: string
  logistics_status: string
  tracking_no: string | null
  paid_at: string | null
  shipped_at: string | null
  delivered_at: string | null
  after_sale_status: string
  product?: Product
}

export interface SessionItem {
  id: number
  user_id: number
  title: string
  status: string
  last_message_at: string | null
}

export interface MessageItem {
  id: number
  session_id: number
  sender_id: number | null
  sender_type: string
  content: string
  message_type: string
  metadata_json: string | null
  created_at: string
}

export interface KnowledgeChunk {
  id: number
  document_id: number
  chunk_index: number
  content: string
  keywords: string | null
  metadata_json: string | null
  created_at: string
  document_title?: string
  document_type?: string
}

export interface KnowledgeDocument {
  id: number
  title: string
  document_type: string
  content: string
  status: string
  chunks?: KnowledgeChunk[]
}

export interface AgentRun {
  id: number
  session_id: number
  message_id: number
  user_id: number
  intent: string | null
  status: string
  summary: string | null
  started_at: string | null
  finished_at: string | null
  error_message: string | null
  created_at: string
}

export interface AgentNodeLog {
  id: number
  run_id: number
  node_name: string
  status: string
  input_json: string | null
  output_json: string | null
  error_message: string | null
  duration_ms: number | null
}

export interface ReplySuggestion {
  id: number
  content: string
  intent: string
  confidence: number
  status: string
  source_summary: string | null
}

export interface ReviewTask {
  id: number
  run_id: number
  reply_suggestion_id: number
  task_type: string
  title: string
  risk_level: string
  risk_reason: string | null
  status: string
  reviewer_id: number | null
  review_comment: string | null
}

export interface Ticket {
  id: number
  ticket_no: string
  ticket_type: string
  user_id: number
  order_id: number | null
  session_id: number | null
  run_id: number | null
  title: string
  description: string
  priority: string
  status: string
  resolution: string | null
}

export interface AgentRunResult {
  run: AgentRun
  reply_suggestion: ReplySuggestion | null
  review_task: ReviewTask | null
  ticket: Ticket | null
}

export interface StatItem {
  name: string
  value: number
}

export async function getHealth() {
  const response = await apiClient.get<{ status: string }>('/health')
  return response.data
}

export const api = {
  getSummary: () => apiClient.get('/dashboard/summary').then((res) => res.data),
  getIntentStats: () => apiClient.get<StatItem[]>('/dashboard/intent-stats').then((res) => res.data),
  getTicketStats: () => apiClient.get<StatItem[]>('/dashboard/ticket-stats').then((res) => res.data),
  getProducts: (keyword?: string) =>
    apiClient.get<Product[]>('/products', { params: { keyword: keyword || undefined } }).then((res) => res.data),
  getProduct: (id: number) => apiClient.get<Product>(`/products/${id}`).then((res) => res.data),
  getOrders: () => apiClient.get<Order[]>('/orders').then((res) => res.data),
  getOrder: (id: number) => apiClient.get<Order>(`/orders/${id}`).then((res) => res.data),
  getSessions: () => apiClient.get<SessionItem[]>('/sessions').then((res) => res.data),
  getMessages: (sessionId: number) =>
    apiClient.get<MessageItem[]>(`/sessions/${sessionId}/messages`).then((res) => res.data),
  sendMessage: (sessionId: number, content: string, senderId = 1) =>
    apiClient
      .post<MessageItem>(`/sessions/${sessionId}/messages`, {
        sender_id: senderId,
        sender_type: 'customer',
        content
      })
      .then((res) => res.data),
  runAgent: (sessionId: number, messageId: number) =>
    apiClient.post<AgentRunResult>('/agent/runs', { session_id: sessionId, message_id: messageId }).then((res) => res.data),
  getAgentRuns: () => apiClient.get<AgentRun[]>('/agent/runs').then((res) => res.data),
  getAgentLogs: (runId: number) =>
    apiClient.get<AgentNodeLog[]>(`/agent/runs/${runId}/node-logs`).then((res) => res.data),
  getDocuments: () => apiClient.get<KnowledgeDocument[]>('/knowledge/documents').then((res) => res.data),
  getDocument: (id: number) => apiClient.get<KnowledgeDocument>(`/knowledge/documents/${id}`).then((res) => res.data),
  searchKnowledge: (query: string) =>
    apiClient.get<KnowledgeChunk[]>('/knowledge/search', { params: { query } }).then((res) => res.data),
  getReviewTasks: () => apiClient.get<ReviewTask[]>('/review-tasks').then((res) => res.data),
  approveReviewTask: (id: number, review_comment: string) =>
    apiClient.post<ReviewTask>(`/review-tasks/${id}/approve`, { reviewer_id: 3, review_comment }).then((res) => res.data),
  rejectReviewTask: (id: number, review_comment: string) =>
    apiClient.post<ReviewTask>(`/review-tasks/${id}/reject`, { reviewer_id: 3, review_comment }).then((res) => res.data),
  getTickets: () => apiClient.get<Ticket[]>('/tickets').then((res) => res.data),
  updateTicketStatus: (id: number, status: string, resolution?: string) =>
    apiClient.post<Ticket>(`/tickets/${id}/status`, { status, resolution }).then((res) => res.data)
}

