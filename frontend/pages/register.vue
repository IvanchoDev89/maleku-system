<template>
  <div>
    <div class="bg-white rounded-2xl shadow-xl p-8">
      <div class="text-center mb-6">
        <h2 class="text-2xl font-bold text-gray-900">{{ t('auth.register.title') }}</h2>
        <p class="text-gray-600 text-sm mt-1">Crea tu cuenta para comenzar</p>
      </div>

      <form @submit.prevent="handleRegister" class="space-y-4">
        <UiInput
          v-model="form.full_name"
          type="text"
          :label="t('auth.register.name')"
          placeholder="Tu nombre completo"
          required
        />

        <UiInput
          v-model="form.email"
          type="email"
          :label="t('auth.register.email')"
          placeholder="tu@email.com"
          required
        />

        <UiInput
          v-model="form.password"
          type="password"
          :label="t('auth.register.password')"
          placeholder="••••••••"
          required
          :error="errors.password"
        />

        <UiInput
          v-model="form.passwordConfirm"
          type="password"
          label="Confirmar contraseña"
          placeholder="••••••••"
          required
          :error="errors.passwordConfirm"
        />

        <UiInput
          v-model="form.phone"
          type="tel"
          label="Teléfono (opcional)"
          placeholder="+506 8888 8888"
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
          {{ loading ? t('common.loading') : t('auth.register.submit') }}
        </UiButton>
      </form>

      <div class="mt-6 pt-6 border-t border-gray-100 text-center">
        <p class="text-gray-600 text-sm">
          {{ t('auth.register.hasAccount') }}
          <NuxtLink to="/login" class="text-primary-600 font-semibold hover:text-primary-700">
            {{ t('auth.register.login') }}
          </NuxtLink>
        </p>
      </div>
    </div>

    <!-- Vendor Registration Link -->
    <div class="mt-6 text-center">
      <p class="text-gray-600 text-sm">
        ¿Quieres ofrecer tus servicios?
        <NuxtLink to="/vendor/register" class="text-primary-600 hover:text-primary-700 font-medium">
          Regístrate como proveedor
        </NuxtLink>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const auth = useAuthStore()
const router = useRouter()

const form = reactive({
  full_name: '',
  email: '',
  password: '',
  passwordConfirm: '',
  phone: ''
})

const errors = reactive({
  password: '',
  passwordConfirm: ''
})

const loading = ref(false)
const error = ref('')

function validate() {
  let valid = true
  errors.password = ''
  errors.passwordConfirm = ''

  if (form.password.length < 6) {
    errors.password = 'La contraseña debe tener al menos 6 caracteres'
    valid = false
  }

  if (form.password !== form.passwordConfirm) {
    errors.passwordConfirm = 'Las contraseñas no coinciden'
    valid = false
  }

  return valid
}

const handleRegister = async () => {
  if (!validate()) return

  loading.value = true
  error.value = ''

  const result = await auth.register({
    full_name: form.full_name,
    email: form.email,
    password: form.password,
    phone: form.phone
  })

  if (result.success) {
    router.push('/')
  } else {
    error.value = result.error || 'Error al registrar'
  }

  loading.value = false
}

definePageMeta({
  layout: 'auth'
})
</script>
