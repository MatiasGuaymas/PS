import './assets/main.css'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import 'bootstrap-icons/font/bootstrap-icons.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { authStore } from './stores/authStore' 

const app = createApp(App)

app.use(router)

authStore.checkAuth()

app.mount('#app')