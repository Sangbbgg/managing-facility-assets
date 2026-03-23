import { createApp } from 'vue'
import { createPinia } from 'pinia'
import naive from 'naive-ui'
import router from '@/router'
import App from '@/App.vue'
createApp(App).use(createPinia()).use(naive).use(router).mount('#app')
