<template>
  <main class="login-page">
    <section class="login-panel">
      <div>
        <h1>{{ t('brand.name') }}</h1>
        <p>{{ t('login.subtitle') }}</p>
      </div>

      <n-form @submit.prevent="submit">
        <n-form-item :label="t('login.username')">
          <n-input v-model:value="username" autocomplete="username" />
        </n-form-item>
        <n-form-item :label="t('login.password')">
          <n-input v-model:value="password" type="password" autocomplete="current-password" />
        </n-form-item>
        <n-button type="primary" block attr-type="submit" :loading="loading">{{ t('login.submit') }}</n-button>
      </n-form>
    </section>
  </main>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NForm, NFormItem, NInput, useMessage } from 'naive-ui'
import { useI18n } from 'vue-i18n'

import { api } from '@/api/client'
import { setCurrentUser } from '@/auth/session'

const router = useRouter()
const message = useMessage()
const { t } = useI18n()
const username = ref('admin_demo')
const password = ref('admin123456')
const loading = ref(false)

async function submit() {
  loading.value = true
  try {
    await api.login(username.value, password.value)
    setCurrentUser(await api.getCurrentUser())
    message.success(t('login.signedIn'))
    await router.replace('/dashboard')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  display: grid;
  min-height: 100vh;
  place-items: center;
  background: #f4f6f8;
}

.login-panel {
  display: grid;
  width: min(420px, calc(100vw - 32px));
  gap: 20px;
  padding: 28px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #ffffff;
}

h1 {
  margin: 0 0 6px;
  font-size: 24px;
}

p {
  margin: 0;
  color: #667085;
}
</style>
