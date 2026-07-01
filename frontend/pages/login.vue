<template>
  <div class="bg-white rounded-2xl shadow-xl p-8">
    <div class="text-center mb-6">
      <h2 class="text-2xl font-bold text-gray-900">Bienvenido de nuevo</h2>
      <p class="text-gray-500 text-sm mt-1">Ingresa para continuar</p>
    </div>

    <form @submit.prevent="handleSubmit" class="space-y-5">
      <UiInput
        v-model="email"
        type="email"
        label="Correo electrónico"
        placeholder="tu@email.com"
        required
        :error="errors.email"
      />

      <div class="space-y-1">
        <label class="block text-sm font-medium text-gray-700">Contraseña</label>
        <div class="relative">
          <input
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            class="w-full px-4 py-2.5 border rounded-xl text-gray-900 placeholder-gray-400 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
            :class="errors.password ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-300'"
            placeholder="••••••••"
            required
          />
          <button
            type="button"
            @click="showPassword = !showPassword"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
            :aria-label="showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'"
            tabindex="-1"
          >
            <Eye v-if="!showPassword" class="w-5 h-5" />
            <EyeOff v-else class="w-5 h-5" />
          </button>
        </div>
        <p v-if="errors.password" class="text-sm text-red-600">{{ errors.password }}</p>
      </div>

      <div class="flex items-center justify-between text-sm">
        <UiCheckbox v-model="rememberMe" label="Recordarme" />
        <a
          href="#"
          @click.prevent="handleForgotPassword"
          class="text-primary-600 hover:text-primary-700 font-medium hover:underline"
        >
          ¿Olvidaste tu contraseña?
        </a>
      </div>

      <UiAlert v-if="error" :variant="errorVariant" dismissible @dismiss="error = ''">
        {{ error }}
      </UiAlert>

      <UiButton
        type="submit"
        :loading="loading"
        variant="primary"
        size="lg"
        full-width
        :disabled="loading"
      >
        {{ loading ? 'Ingresando...' : 'Iniciar Sesión' }}
      </UiButton>
    </form>

    <div class="mt-6 pt-6 border-t border-gray-100 text-center">
      <p class="text-gray-500 text-sm">
        ¿No tienes cuenta?
        <NuxtLink to="/register" class="text-primary-600 font-semibold hover:text-primary-700 ml-1">
          Regístrate
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
import { Eye, EyeOff } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

definePageMeta({ layout: 'auth' })

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const rememberMe = ref(false)
const loading = ref(false)
const error = ref('')
const errorVariant = ref<'error' | 'warning'>('error')

const errors = reactive({ email: '', password: '' })

let retryCountdown = 0
let countdownTimer: ReturnType<typeof setInterval> | null = null

function getDefaultRedirect(role: string): string {
  switch (role) {
    case 'super_admin': return '/superadmin/dashboard'
    case 'vendor': return '/vendor/dashboard'
    case 'admin': return '/admin/dashboard'
    default: return '/'
  }
}

function isSafeRedirect(redirect: string): boolean {
  try {
    const url = new URL(redirect, window.location.origin)
    return url.origin === window.location.origin
  } catch {
    return redirect.startsWith('/')
  }
}

function getRedirectUrl(role: string): string {
  const redirect = route.query.redirect as string
  if (redirect && isSafeRedirect(redirect)) return redirect
  return getDefaultRedirect(role)
}

function validate(): boolean {
  let valid = true
  errors.email = ''
  errors.password = ''
  if (!email.value) { errors.email = 'El correo es requerido'; valid = false }
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) { errors.email = 'Correo inválido'; valid = false }
  if (!password.value) { errors.password = 'La contraseña es requerida'; valid = false }
  return valid
}

function handleForgotPassword() {
  error.value = 'Función de recuperación próximamente. Contacta al administrador.'
  errorVariant.value = 'warning'
}

function startRetryCountdown(seconds: number) {
  retryCountdown = seconds
  countdownTimer = setInterval(() => {
    retryCountdown--
    if (retryCountdown <= 0) {
      if (countdownTimer) clearInterval(countdownTimer)
      error.value = ''
    }
  }, 1000)
}

onMounted(async () => {
  const auth = useAuthStore()
  const stored = localStorage.getItem('remembered_session')
  if (stored) {
    try {
      const session = JSON.parse(stored)
      if (session.refreshToken && session.user) {
        auth.user = session.user
        auth.refreshTokenValue = session.refreshToken
        const refreshed = await auth.refreshToken()
        if (refreshed) { router.push(getRedirectUrl(session.user.role)); return }
      }
    } catch { localStorage.removeItem('remembered_session') }
  }
  if (auth.isAuthenticated && auth.token && auth.user) {
    router.push(getRedirectUrl(auth.user.role))
  }
  nextTick(() => document.querySelector<HTMLInputElement>('input[type="email"]')?.focus())
})

onUnmounted(() => { if (countdownTimer) clearInterval(countdownTimer) })

async function handleSubmit() {
  if (!validate()) return
  loading.value = true
  error.value = ''
  try {
    const auth = useAuthStore()
    const result = await auth.login(email.value, password.value)
    if (result.success) {
      if (rememberMe.value && result.user) {
        localStorage.setItem('remembered_session', JSON.stringify({ refreshToken: auth.refreshTokenValue, user: result.user }))
      } else {
        localStorage.removeItem('remembered_session')
      }
      router.push(getRedirectUrl(result.user?.role || 'client'))
    } else {
      const e = (result.error || '').toLowerCase()
      if (e.includes('rate limit') || e.includes('too many')) {
        error.value = 'Demasiados intentos. Espera 60 segundos.'
        errorVariant.value = 'warning'
        startRetryCountdown(60)
      } else if (e.includes('invalid') || e.includes('credentials')) {
        error.value = 'Correo o contraseña incorrectos.'
        errorVariant.value = 'error'
      } else if (e.includes('locked') || e.includes('blocked') || e.includes('inactive')) {
        error.value = 'Cuenta bloqueada. Contacta al administrador.'
        errorVariant.value = 'error'
      } else {
        error.value = result.error || 'Error inesperado.'
        errorVariant.value = 'error'
      }
    }
  } catch {
    error.value = 'Error inesperado. Intenta de nuevo.'
    errorVariant.value = 'error'
  }
  loading.value = false
}
</script>
