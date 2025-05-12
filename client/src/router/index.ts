import { createRouter, createWebHistory } from 'vue-router'
import LandingPage from '../pages/LandingPage.vue'
// 1. Import the DashboardPage
import DashboardPage from '../pages/DashboardPage.vue'

const routes = [
  {
    path: '/',
    name: 'Landing',
    component: LandingPage
  },
  // 2. Add the dashboard route
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DashboardPage,
    // Optional: Add meta field for routes that require authentication
    meta: { requiresAuth: true }
  }
  // Add more routes here later
]

// ... rest of the router setup ...
const BASE_URL = '/'

const router = createRouter({
  history: createWebHistory(BASE_URL),
  routes
})

// Optional: Global navigation guard (example for protecting routes)
// This is NOT strictly needed for the landing page redirect,
// but useful for protecting '/dashboard' directly.
// router.beforeEach((to, from, next) => {
//   // This assumes you have Clerk initialized and potentially useAuth available globally
//   // or you implement a more robust auth state check here.
//   // For simplicity, this example might need adjustment based on Clerk's loading state.
//   const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
//   const isAuthenticated = false; // Replace with actual check, e.g., using useAuth().isSignedIn.value (needs careful handling of reactivity/loading)

//   if (requiresAuth && !isAuthenticated) {
//     // Redirect to login or landing page if trying to access protected route while logged out
//     next({ name: 'Landing' }); // Or trigger Clerk sign-in
//   } else {
//     next(); // Proceed as normal
//   }
// });


export default router