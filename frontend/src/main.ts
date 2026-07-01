import { createApp } from 'vue'
import 'vfonts/Lato.css'

import App from './App.vue'
import { i18n } from './i18n'
import router from './router'
import './styles/main.css'

createApp(App).use(i18n).use(router).mount('#app')
