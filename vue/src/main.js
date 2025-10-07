import './assets/css/other/tailwind.css'
import './config/appResourceCss'
import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

import { AppPrimeConfig, primeConfUse } from '@/config/vue-prime/appPrimeConfig'
import { AppComponent, appComponentSetup } from '@/config/appComponent.js'
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import ConfirmationService from 'primevue/confirmationservice'
import DialogService from 'primevue/dialogservice'

import Vue3EasyDataTable from 'vue3-easy-data-table'

import VueSmoothScroll from 'vue3-smooth-scroll'

const app = createApp(App)

app.use(createPinia())
app.use(router)

const primeConf = new AppPrimeConfig(app)
app.use(PrimeVue, primeConfUse)
app.use(ToastService)
app.use(ConfirmationService)
app.use(DialogService)
app.use(VueSmoothScroll)

primeConf.init()

// -----------------------------

app.component('EasyDataTable', Vue3EasyDataTable)
new AppComponent(app)

// -----------------------------
app.mount('#app')

new appComponentSetup()
