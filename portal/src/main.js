import './assets/main.css'
import './assets/variables.css'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import 'bootstrap-icons/font/bootstrap-icons.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import authPlugin from './plugins/auth'

const app = createApp(App)

app.use(authPlugin)
app.use(router)


app.mount('#app')