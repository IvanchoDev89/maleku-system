<template>
  <div class="bg-white rounded-2xl shadow-xl p-8">
    <div class="text-center mb-6">
      <h2 class="text-2xl font-bold text-gray-900">Bienvenido de nuevo</h2>
      <p class="text-gray-500 text-sm mt-1">Ingresa para continuar</p>
    </div>

    <form @submit.prevent="handleLogin" class="space-y-5">
      <UiInput
        ref="emailRef"
        v-model="form.email"
        type="email"
        label="Correo electrónico"
        placeholder="tu@email.com"
        required
        :error="errors.email"
        @update:model-value="errors.email = ''"
      />

      <div class="space-y-1">
        <label class="block text-sm font-medium text-gray-700">Contraseña</label>
        <div class="relative">
          <input
            v-model="form.password"
            :type="showPassword ? 'text' : 'password'"
            class="w-full px-4 py-2.5 border rounded-xl text-gray-900 placeholder-gray-400 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
            :class="errors.password ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-300'"
            placeholder="••••••••"
            required
            @input="errors.password = ''"
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
        <label class="flex items-center gap-2 text-gray-600 hover:text-gray-800 cursor-pointer">
          <input
            v-model="rememberMe"
            type="checkbox"
            class="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          Recordarme
        </label>
        <a
          href="#"
          @click.prevent="handleForgotPassword"
          class="text-primary-600 hover:text-primary-700 font-medium hover:underline"
        >
          ¿Olvidaste tu contraseña?
        </a>
      </div>

      <div v-if="error" class="p-3 rounded-xl flex items-start gap-3" :class="errorVariant === 'error' ? 'bg-red-50 border border-red-200' : 'bg-amber-50 border border-amber-200'" role="alert">
        <AlertCircle v-if="errorVariant === 'error'" class="w-5 h-5 text-red-500 mt-0.5 shrink-0" />
        <Clock v-else class="w-5 h-5 text-amber-500 mt-0.5 shrink-0" />
        <p :class="errorVariant === 'error' ? 'text-red-700' : 'text-amber-700'" class="text-sm">{{ error }}</p>
      </div>

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
import { Eye, EyeOff, AlertCircle, Clock } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase

definePageMeta({
  layout: 'auth'
})

const emailRef = ref<HTMLInputElement | null>(null)
const showPassword = ref(false)
const rememberMe = ref(false)

const form = reactive({
  email: '',
  password: ''
})

const errors = reactive({
  email: '',
  password: ''
})

const loading = ref(false)
const error = ref('')
const errorVariant = ref<'error' | 'warning'>('error')
let retryCountdown = ref(0)
let countdownTimer: ReturnType<typeof setInterval> | null = null

function getDefaultRedirect(role: string): string {
  switch (role) {
    case 'super_admin': return '/superadmin/dashboard'
    case 'vendor': return '/vendor/dashboard'
    case 'admin': return '/admin/dashboard'
    default: return '/'
  }
}

function getRedirectUrl(role: string): string {
  return (route.query.redirect as string) || getDefaultRedirect(role)
}

function validate(): boolean {
  let valid = true
  errors.email = ''
  errors.password = ''

  if (!form.email) {
    errors.email = 'El correo electrónico es requerido'
    valid = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    errors.email = 'Ingresa un correo electrónico válido'
    valid = false
  }

  if (!form.password) {
    errors.password = 'La contraseña es requerida'
    valid = false
  }

  return valid
}

function handleForgotPassword() {
  error.value = 'Función de recuperación próximamente. Contacta al administrador.'
  errorVariant.value = 'warning'
}

function startRetryCountdown(seconds: number) {
  retryCountdown.value = seconds
  countdownTimer = setInterval(() => {
    retryCountdown.value--
    if (retryCountdown.value <= 0) {
      if (countdownTimer) clearInterval(countdownTimer)
      error.value = ''
    }
  }, 1000)
}

onMounted(() => {
  const auth = useAuthStore()

  // Restore session from localStorage if "remember me" was checked
  const stored = localStorage.getItem('remembered_session')
  if (stored) {
    try {
      const session = JSON.parse(stored)
      if (session.token && session.user) {
        auth.token = session.token
        auth.refreshTokenValue = session.refreshToken
        auth.user = session.user
        auth.isAuthenticated = true
        sessionStorage.setItem('token', session.token)
        sessionStorage.setItem('refreshToken', session.refreshToken)
        sessionStorage.setItem('user', JSON.stringify(session.user))
        router.push(getRedirectUrl(session.user.role))
        return
      }
    } catch {
      localStorage.removeItem('remembered_session')
    }
  }

  if (auth.isAuthenticated && auth.token && auth.user) {
    router.push(getRedirectUrl(auth.user.role))
  }

  // Auto-focus email field
  nextTick(() => {
    const input = document.querySelector<HTMLInputElement>('input[type="email"]')
    input?.focus()
  })
})

onUnmounted(() => {
  if (countdownTimer) clearInterval(countdownTimer)
})

const handleLogin = async () => {
  if (!validate()) return

  loading.value = true
  error.value = ''

  try {
    const auth = useAuthStore()
    const result = await auth.login(form.email, form.password)

    if (result.success) {
      if (rememberMe.value && result.user) {
        localStorage.setItem('remembered_session', JSON.stringify({
          token: auth.token,
          refreshToken: auth.refreshTokenValue,
          user: result.user
        }))
      } else {
        localStorage.removeItem('remembered_session')
      }
      router.push(getRedirectUrl(result.user?.role || 'client'))
    } else {
      const e = (result.error || '').toLowerCase()
      if (e.includes('rate limit') || e.includes('too many')) {
        error.value = 'Demasiados intentos. Espera 60 segundos antes de intentar de nuevo.'
        errorVariant.value = 'warning'
        startRetryCountdown(60)
      } else if (e.includes('invalid') || e.includes('credentials')) {
        error.value = 'Correo electrónico o contraseña incorrectos.'
        errorVariant.value = 'error'
      } else if (e.includes('locked') || e.includes('blocked') || e.includes('inactive')) {
        error.value = 'Tu cuenta ha sido bloqueada. Contacta al administrador.'
        errorVariant.value = 'error'
      } else {
        error.value = result.error || 'Error inesperado al iniciar sesión. Intenta de nuevo.'
        errorVariant.value = 'error'
      }
    }
  } catch (e) {
    error.value = 'Error inesperado al iniciar sesión. Intenta de nuevo.'
    errorVariant.value = 'error'
  }

  loading.value = false
}
</script>
