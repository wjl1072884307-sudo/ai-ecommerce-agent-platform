import { computed, ref } from 'vue'

export type UserRole = 'admin' | 'reviewer' | 'agent' | 'viewer'

export interface CurrentUser {
  id: number
  username: string
  display_name: string
  role: UserRole
  status: string
}

const tokenKey = 'ai_ecommerce_auth_token'

const token = ref<string | null>(localStorage.getItem(tokenKey))
const currentUser = ref<CurrentUser | null>(null)

export const authToken = computed(() => token.value)
export const user = computed(() => currentUser.value)
export const role = computed(() => currentUser.value?.role ?? null)
export const isAuthenticated = computed(() => Boolean(token.value))

export function setToken(value: string) {
  token.value = value
  localStorage.setItem(tokenKey, value)
}

export function setCurrentUser(value: CurrentUser | null) {
  currentUser.value = value
}

export function clearSession() {
  token.value = null
  currentUser.value = null
  localStorage.removeItem(tokenKey)
}

export function canAccess(allowedRoles?: UserRole[]) {
  if (!allowedRoles?.length) return true
  return Boolean(currentUser.value && allowedRoles.includes(currentUser.value.role))
}
