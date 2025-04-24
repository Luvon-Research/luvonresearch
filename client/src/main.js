import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // <--- Import the router
import { clerkPlugin } from '@clerk/vue'
import PrimeVue from 'primevue/config';
import Lara from '@primeuix/themes/lara';
import 'bootstrap/dist/css/bootstrap.min.css'
import { definePreset } from '@primeuix/themes';

const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

if (!PUBLISHABLE_KEY) {
  throw new Error('Add your Clerk Publishable Key to the .env file')
}

const app = createApp(App)

const MyPreset = definePreset(Lara, {
    semantic: {
        primary: {
            50: '{gray.950}',
            100: '{gray.950}',
            200: '{gray.950}',
            300: '{gray.950}',
            400: '{gray.950}',
            500: '{gray.950}',
            600: '{gray.950}',
            700: '{gray.950}',
            800: '{gray.950}',
            900: '{gray.950}',
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