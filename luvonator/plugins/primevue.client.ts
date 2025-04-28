import { defineNuxtPlugin } from '#app'
import PrimeVue from 'primevue/config'
import { definePreset } from '@primeuix/themes'
import Lara from '@primeuix/themes/lara'
import Button from 'primevue/button'
import Menubar from 'primevue/menubar'
import InputText from 'primevue/inputtext'

export default defineNuxtPlugin((nuxtApp) => {
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
  })

  nuxtApp.vueApp.use(PrimeVue, {
    theme: {
      preset: MyPreset,
      options: {
        darkModeSelector: '.light-mode'
      }
    },
    ripple: true
  })

  // Register PrimeVue components
  nuxtApp.vueApp.component('Button', Button)
  nuxtApp.vueApp.component('Menubar', Menubar)
  nuxtApp.vueApp.component('InputText', InputText)
}) 