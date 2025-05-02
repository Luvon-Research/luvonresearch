import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // <--- Import the router
import { clerkPlugin } from '@clerk/vue'
import PrimeVue from 'primevue/config';
import Lara from '@primeuix/themes/lara';
import 'bootstrap/dist/css/bootstrap.min.css'
import { definePreset } from '@primeuix/themes';

const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY ?? process.env.VITE_CLERK_PUBLISHABLE_KEY
const API_URL  = import.meta.env.VITE_API_URL ?? process.env.VITE_API_URL

if (!PUBLISHABLE_KEY) {
  throw new Error('Add your Clerk Publishable Key to the .env file')
}

const app = createApp(App)

const MyPreset = definePreset(Lara, {
    semantic: {
        primary: {
            50: '{gray.50}',
            100: '{gray.100}',
            200: '{gray.200}',
            300: '{gray.300}',
            400: '{gray.400}',
            500: '{gray.500}',
            600: '{gray.600}',
            700: '{gray.700}',
            800: '{gray.800}',
            900: '{gray.900}',
            950: '{gray.950}'
        },
        secondary: {
            50: '{green.500}',
            100: '{green.500}',
            200: '{green.500}',
            300: '{green.500}',
            400: '{green.500}',
            500: '{green.500}',
            600: '{green.500}',
            700: '{green.500}',
            800: '{green.500}',
            900: '{green.500}',
            950: '{green.500}' 
        }
    }
});

app.use(router) // <--- Tell the app to use the router
app.use(clerkPlugin, { publishableKey: PUBLISHABLE_KEY }) // <--- Configure Clerk authentication
app.use(PrimeVue, {
    theme: {
        preset: MyPreset,
        options: {
            darkModeSelector: '.light-mode'
        }
    }
});
app.mount('#app')