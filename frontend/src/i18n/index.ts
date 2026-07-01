import { createI18n } from 'vue-i18n'

import { messages, type Locale } from './messages'

const savedLocale = localStorage.getItem('locale') as Locale | null

export const i18n = createI18n({
  legacy: false,
  locale: savedLocale && savedLocale in messages ? savedLocale : 'en',
  fallbackLocale: 'en',
  messages
})
