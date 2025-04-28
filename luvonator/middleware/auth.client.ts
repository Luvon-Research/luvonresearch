import { useAuthCheck } from '../composables/useAuthCheck'

export default defineNuxtRouteMiddleware((to) => {
  // Only run on client-side
  if (process.server) return
  
  const { checkAuth } = useAuthCheck()
  
  if (to.meta.requiresAuth && !checkAuth(true)) {
    return navigateTo('/')
  }
}) 