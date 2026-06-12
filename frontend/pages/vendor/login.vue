<template>
  <div class="bg-white rounded-2xl shadow-xl p-8">
    <div class="text-center mb-6">
      <div class="w-16 h-16 bg-primary-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
        <Store class="w-8 h-8 text-primary-600" />
      </div>
      <h2 class="text-2xl font-bold text-gray-900">Ingreso Proveedores</h2>
      <p class="text-gray-600 text-sm mt-1">Accede a tu panel de gestión</p>
    </div>

    <form @submit.prevent="handleLogin" class="space-y-5">
      <UiInput
        v-model="form.email"
        type="email"
        label="Email"
        placeholder="vendor@costaricatravel.dev"
        required
      />

      <UiInput
        v-model="form.password"
        type="password"
        label="Contraseña"
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
        {{ loading ? 'Ingresando...' : 'Iniciar Sesión' }}
      </UiButton>
    </form>

    <div class="mt-6 pt-6 border-t border-gray-100 text-center">
      <p class="text-gray-600 text-sm">
        ¿No tienes cuenta?
        <NuxtLink to="/vendor/register" class="text-primary-600 font-semibold hover:text-primary-700">
          Regístrate como proveedor
        </NuxtLink>
      </p>
    </div>

    <div class="mt-4 text-center">
      <NuxtLink to="/login" class="text-gray-400 hover:text-primary-600 text-sm inline-flex items-center gap-1">
        <ArrowLeft class="w-4 h-4" />
        Volver al login general
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Store, ArrowLeft } from 'lucide-vue-next'

const auth = useAuthStore()
const router = useRouter()

definePageMeta({
  layout: 'auth'
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

  if (result.success) {
    if (auth.isVendor) {
      router.push('/vendor/dashboard')
    } else {
      error.value = 'No tienes acceso de proveedor'
      auth.logout()
    }
  } else {
    error.value = result.error || 'Error al iniciar sesión'
  }

  loading.value = false
}

onMounted(() => {
  if (auth.isAuthenticated && auth.isVendor) {
    router.push('/vendor/dashboard')
  }
})
</script>
