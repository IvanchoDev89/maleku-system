export default defineNuxtRouteMiddleware((to) => {
  const auth = useAuthStore()

  // Check if user is authenticated
  if (!auth.isAuthenticated || !auth.token) {
    return navigateTo('/login')
  }

  // Check role based on route
  if (to.path.startsWith('/vendor/')) {
    if (!auth.isVendor && auth.user?.role !== 'super_admin') {
      return navigateTo('/')
    }
  }

  if (to.path.startsWith('/admin/')) {
    if (!['super_admin', 'admin'].includes(auth.user?.role || '')) {
      return navigateTo('/')
    }
  }
})
