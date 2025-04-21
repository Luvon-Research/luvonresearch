import { createRouter, createWebHistory } from 'vue-router'
import LandingPage from '../pages/LandingPage.vue' // Import your page

const routes = [
  {
    path: '/', // The root URL
    name: 'Landing',
    component: LandingPage // Assign the component to this route
  },
  // Add more routes here later, e.g.:
  // {
  //   path: '/about',
  //   name: 'About',
  //   // Lazy load route components for better performance
  //   component: () => import('../pages/AboutPage.vue')
  // }
]

// Replace import.meta.env.BASE_URL with a static value or environment variable
const BASE_URL = '/' // or process.env.BASE_URL if using Node.js environment variables

const router = createRouter({
  history: createWebHistory(BASE_URL), // Use HTML5 history mode
  routes // short for `routes: routes`
})

export default router