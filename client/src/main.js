import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // <--- Import the router
import { clerkPlugin } from '@clerk/vue'
import PrimeVue from 'primevue/config';
import Lara from '@primeuix/themes/lara';
import 'bootstrap/dist/css/bootstrap.min.css'

const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

if (!PUBLISHABLE_KEY) {
  throw new Error('Add your Clerk Publishable Key to the .env file')
}

const app = createApp(App)

app.use(router) // <--- Tell the app to use the router
app.use(clerkPlugin, { publishableKey: PUBLISHABLE_KEY }) // <--- Configure Clerk authentication
app.use(PrimeVue, {
    theme: {
        preset: Lara,
        options: {
            darkModeSelector: '.light-mode'
        }
    }
});
app.mount('#app')