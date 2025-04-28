export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },
  
  css: [
    '~/assets/main.css',
    'bootstrap/dist/css/bootstrap.min.css',
    'primeicons/primeicons.css',
  ],

  modules: [
    '@nuxtjs/supabase',
    '@primevue/nuxt-module',
    '@clerk/nuxt',
  ],

  supabase: {
    redirect: false,
  },



  primevue: {
    theme: 'aura-light',
    options: {
      ripple: true
    },
    components: {
      include: ['Button', 'InputText', 'Menubar', 'DataTable', 'Calendar', 'Dropdown']
    }
  },

  // build: {
  //   transpile: ['primevue', '@clerk/vue']
  // },

  app: {
    head: {
      title: 'Luvon',
      meta: [
        { name: 'viewport', content: 'width=device-width, initial-scale=1' }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
      ]
    }
  },

  runtimeConfig: {
    public: {
      clerkPublishableKey: process.env.NUXT_PUBLIC_CLERK_PUBLISHABLE_KEY || '',
    },
    clerkSecretKey: process.env.CLERK_SECRET_KEY || '',
  }
})
