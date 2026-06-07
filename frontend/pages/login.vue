<template>
  <div class="min-h-screen flex">
    <!-- Left Side - Visual (hidden on mobile) -->
    <div class="hidden lg:flex lg:w-1/2 relative">
      <NuxtImg 
        src="https://images.unsplash.com/photo-1518638150340-f706e86654de?w=1200&q=80" 
        class="absolute inset-0 w-full h-full object-cover"
        alt="Costa Rica"
        width="1200"
        height="800"
        format="webp"
      />
      <div class="absolute inset-0 bg-gradient-to-br from-teal-900/80 to-emerald-900/80"></div>
      <div class="relative z-10 flex flex-col justify-center px-12 text-white">
        <span class="text-5xl mb-4">🌴</span>
        <h1 class="text-3xl font-bold mb-2">Costa Rica Travel</h1>
        <p class="text-white/80">Tu aventura comienza aquí</p>
      </div>
    </div>

    <!-- Right Side - Form -->
    <div class="w-full lg:w-1/2 flex items-center justify-center bg-gray-50 p-8">
      <div class="w-full max-w-md">
        <div class="bg-white rounded-2xl shadow-xl p-8">
          <div class="text-center mb-6">
            <h2 class="text-2xl font-bold text-gray-900">{{ t('auth.login.title') }}</h2>
            <p class="text-gray-600 text-sm mt-1">Ingresa para continuar</p>
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

            <div v-if="error" class="p-3 bg-red-50 border border-red-200 rounded-xl">
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
            <p class="text-gray-600 text-sm">
              {{ t('auth.login.noAccount') }}
              <NuxtLink to="/register" class="text-teal-600 font-semibold hover:text-teal-700">
                {{ t('auth.login.register') }}
              </NuxtLink>
            </p>
          </div>
        </div>

        <!-- Vendor Login Link -->
        <div class="mt-6 text-center">
          <p class="text-gray-600 text-sm">
            ¿Eres proveedor?
            <NuxtLink to="/vendor/login" class="text-teal-600 hover:text-teal-700 font-medium">
              Ingresa aquí
            </NuxtLink>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const route = useRoute()
const auth = useAuthStore()
const router = useRouter()

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
  auth.initAuth()
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

definePageMeta({
  layout: 'auth'
})
</script>