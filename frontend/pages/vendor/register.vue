<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary/10 to-accent/10 py-12 px-4">
    <div class="w-full max-w-lg">
      <div class="text-center mb-8">
        <NuxtLink to="/" class="inline-flex items-center gap-2">
          <span class="text-4xl">🌴</span>
          <span class="text-2xl font-bold text-primary">Costa Rica Travel</span>
        </NuxtLink>
      </div>

      <div class="bg-white rounded-2xl shadow-lg p-8">
        <div class="text-center mb-6">
          <span class="text-5xl mb-4 block">🏪</span>
          <h2 class="text-3xl font-bold">Registro de Proveedor</h2>
          <p class="text-gray-500 mt-2">Únete como hotel, tour operador o restaurante</p>
        </div>

        <form @submit.prevent="handleRegister" class="space-y-4">
          <h3 class="font-semibold text-gray-700 border-b pb-2">Información Personal</h3>

          <div class="grid grid-cols-2 gap-4">
            <UiInput v-model="form.full_name" label="Nombre" placeholder="Tu nombre" required />
            <UiInput v-model="form.phone" type="tel" label="Teléfono" placeholder="+506 8888 8888" />
          </div>

          <UiInput v-model="form.email" type="email" label="Email" placeholder="tu@email.com" required />

          <UiInput v-model="form.password" type="password" label="Contraseña" placeholder="••••••••" required />

          <h3 class="font-semibold text-gray-700 border-b pb-2 pt-4">Información del Negocio</h3>

          <UiInput v-model="form.business_name" label="Nombre del Negocio" placeholder="Nombre de tu negocio" required />

          <UiSelect v-model="form.business_type" :options="businessTypeOptions" placeholder="Selecciona..." />

          <div v-if="error" class="p-3 bg-red-50 border border-red-200 rounded-xl">
            <p class="text-red-600 text-sm text-center">{{ error }}</p>
          </div>

          <UiButton type="submit" :loading="loading" variant="primary" size="lg" full-width>
            {{ loading ? 'Registrando...' : 'Crear Cuenta de Proveedor' }}
          </UiButton>
        </form>

        <div class="mt-6 text-center">
          <p class="text-gray-600">
            ¿Ya tienes cuenta?
            <NuxtLink to="/vendor/login" class="text-primary font-semibold">Inicia sesión</NuxtLink>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const auth = useAuthStore()
const router = useRouter()

const form = reactive({
  full_name: '',
  email: '',
  password: '',
  phone: '',
  business_name: '',
  business_type: ''
})

const loading = ref(false)
const error = ref('')

const businessTypeOptions = [
  { value: 'hotel', label: 'Hotel / Alojamiento' },
  { value: 'tour_operator', label: 'Tour Operador' },
  { value: 'restaurant', label: 'Restaurante' },
  { value: 'transport', label: 'Transporte' },
  { value: 'activity', label: 'Actividad / Aventura' },
]

const handleRegister = async () => {
  loading.value = true
  error.value = ''

  const result = await auth.registerVendor(form)
  
  if (result.success) {
    router.push('/vendor/dashboard')
  } else {
    error.value = result.error || 'Error al registrar'
  }
  
  loading.value = false
}

definePageMeta({
  layout: 'auth'
})
</script>