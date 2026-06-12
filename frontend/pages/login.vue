<template>
  <div class="bg-white rounded-2xl shadow-xl p-8">
    <div class="text-center mb-6">
      <h2 class="text-2xl font-bold text-gray-900">{{ t('auth.login.title') }}</h2>
      <p class="text-gray-500 text-sm mt-1">{{ t('auth.login.subtitle', 'Ingresa para continuar') }}</p>
    </div>

    <form @submit.prevent="handleLogin" class="space-y-5">
      <UiInput
        v-model="form.email"
        type="email"
        :label="t('auth.login.email')"
        placeholder="tu@email.com"
        required
      />

      <UiInput
        v-model="form.password"
        type="password"
        :label="t('auth.login.password')"
        placeholder="••••••••"
        required
      />

      <div v-if="error" class="p-3 bg-red-50 border border-red-200 rounded-xl" role="alert">
        <p class="text-red-600 text-sm text-center">{{ error }}</p>
      </div>

      <UiButton
        type="submit"
        :loading="loading"
        variant="primary"
        size="lg"
        full-width
      >
        {{ loading ? t('common.loading') : t('auth.login.submit') }}
      </UiButton>
    </form>

    <div class="mt-6 pt-6 border-t border-gray-100 text-center">
      <p class="text-gray-500 text-sm">
        {{ t('auth.login.noAccount', '¿No tienes cuenta?') }}
        <NuxtLink to="/register" class="text-primary-600 font-semibold hover:text-primary-700 ml-1">
          {{ t('auth.login.register', 'Regístrate') }}
        </NuxtLink>
      </p>
    </div>

    <div class="mt-4 text-center">
      <p class="text-gray-400 text-sm">
        ¿Eres proveedor?
        <NuxtLink to="/vendor/login" class="text-primary-600 hover:text-primary-700 font-medium ml-1">
          Ingresa aquí
        </NuxtLink>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
const { t } = useI18n()
const route = useRoute()
const auth = useAuthStore()
const router = useRouter()

definePageMeta({
  layout: 'auth'
})

function getDefaultRedirect(role: string): string {
  switch (role) {
    case 'super_admin': return '/superadmin/dashboard'
    case 'vendor': return '/vendor/dashboard'
    case 'admin': return '/admin/dashboard'
    default: return '/dashboard'
  }
}

function getRedirectUrl(role: string): string {
  return (route.query.redirect as string) || getDefaultRedirect(role)
}

onMounted(() => {
  if (auth.isAuthenticated && auth.token && auth.user) {
    router.push(getRedirectUrl(auth.user.role))
  }
})

const form = reactive({
  email: '',
  password: ''
})

const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  loading.value = true
  error.value = ''

  const result = await auth.login(form.email, form.password)
  
  if (result.success && result.user) {
    router.push(getRedirectUrl(result.user.role))
  } else {
    error.value = result.error || 'Error al iniciar sesión'
  }
  
  loading.value = false
}
</script>
