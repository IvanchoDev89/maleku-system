export default defineNuxtPlugin(() => {
  const auth = useAuthStore()
  
  // Initialize auth from sessionStorage on app start
  if (process.client) {
    auth.initAuth()
  }
})
