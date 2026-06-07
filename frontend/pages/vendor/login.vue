<template>
  <div class="w-full max-w-md">
    <!-- Mobile Logo -->
    <div class="lg:hidden text-center mb-8">
      <NuxtLink to="/" class="inline-flex items-center gap-2">
        <span class="text-4xl">🌴</span>
        <span class="text-2xl font-bold text-teal-600">Costa Rica Travel</span>
      </NuxtLink>
      <p class="text-gray-700 text-sm mt-2">Panel de Proveedores</p>
    </div>

    <div class="bg-white rounded-2xl shadow-xl p-8">
      <div class="text-center mb-6">
        <div class="w-16 h-16 bg-teal-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <Store class="w-8 h-8 text-teal-600" />
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
          <NuxtLink to="/register" class="text-teal-600 font-semibold hover:text-teal-700">
            Regístrate como proveedor
          </NuxtLink>
        </p>
      </div>
    </div>

    <div class="mt-6 text-center">
      <NuxtLink to="/login" class="text-gray-700 hover:text-teal-600 text-sm flex items-center justify-center gap-1">
        <ArrowLeft class="w-4 h-4" />
        Volver al login general
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Store, ArrowLeft } from 'lucide-vue-next'

const auth = useAuthStore()
const router = useRouter()

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

definePageMeta({
  layout: 'auth'
})
</script>
