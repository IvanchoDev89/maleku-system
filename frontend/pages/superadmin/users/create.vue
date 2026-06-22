<script setup lang="ts">
definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin'],
})

const router = useRouter()
const api = useApi()
const toast = useToast()

const loading = ref(false)
const form = ref({
  email: '',
  password: '',
  full_name: '',
  phone: '',
  role: 'client',
  is_active: true,
})

const errors = ref<Record<string, string>>({})

const roleOptions = [
  { value: 'client', label: 'Client' },
  { value: 'agent', label: 'Agent' },
  { value: 'admin', label: 'Admin' },
  { value: 'vendor', label: 'Vendor' },
]

function validate(): boolean {
  const errs: Record<string, string> = {}
  if (!form.value.email) errs.email = 'El email es requerido'
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.value.email)) errs.email = 'Email inválido'
  if (!form.value.password || form.value.password.length < 6) errs.password = 'Mínimo 6 caracteres'
  if (!form.value.full_name) errs.full_name = 'El nombre es requerido'
  errors.value = errs
  return Object.keys(errs).length === 0
}

async function submit() {
  if (!validate()) return
  loading.value = true
  try {
    const payload: Record<string, unknown> = {
      email: form.value.email,
      password: form.value.password,
      full_name: form.value.full_name,
      role: form.value.role,
      is_active: form.value.is_active,
    }
    if (form.value.phone) payload.phone = form.value.phone
    const result: any = await api.post('/superadmin/users', payload)
    toast.success('Usuario creado exitosamente')
    router.push(`/superadmin/users/${result.id}`)
  } catch (e: any) {
    const detail = e?.data?.detail
    if (detail?.includes?.('Email already registered') || detail?.includes?.('already registered')) {
      errors.value.email = 'Este email ya está registrado'
    } else {
      toast.error(detail || 'Error al crear usuario')
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="max-w-2xl mx-auto space-y-6">
    <!-- Header -->
    <div class="flex items-center gap-4">
      <button @click="router.push('/superadmin/users')" class="p-2 hover:bg-gray-100 rounded-lg">
        <span class="text-2xl">&larr;</span>
      </button>
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Nuevo Usuario</h1>
        <p class="text-gray-500">Crear un nuevo usuario en el sistema</p>
      </div>
    </div>

    <!-- Form -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <form @submit.prevent="submit" class="space-y-5">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <UiInput
            v-model="form.full_name"
            label="Nombre completo"
            placeholder="Nombre del usuario"
            required
            :error="errors.full_name"
          />
          <UiInput
            v-model="form.email"
            type="email"
            label="Email"
            placeholder="usuario@email.com"
            required
            :error="errors.email"
          />
          <UiInput
            v-model="form.password"
            type="password"
            label="Contraseña"
            placeholder="Mínimo 6 caracteres"
            required
            :error="errors.password"
          />
          <UiInput
            v-model="form.phone"
            type="tel"
            label="Teléfono"
            placeholder="+506 8888 8888"
          />
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div class="space-y-1">
            <label class="block text-sm font-medium text-gray-700">
              Rol <span class="text-red-500">*</span>
            </label>
            <UiSelect v-model="form.role" :options="roleOptions" />
          </div>
          <div class="flex items-end pb-3">
            <label class="flex items-center gap-3 cursor-pointer">
              <input
                v-model="form.is_active"
                type="checkbox"
                class="w-4 h-4 rounded border-gray-300 text-slate-900 focus:ring-slate-500"
              />
              <span class="text-sm font-medium text-gray-700">Activo</span>
            </label>
          </div>
        </div>

        <div class="flex justify-end gap-3 pt-4 border-t border-gray-100">
          <button
            type="button"
            @click="router.push('/superadmin/users')"
            class="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
          >
            Cancelar
          </button>
          <button
            type="submit"
            :disabled="loading"
            class="px-6 py-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <UiSpinner v-if="loading" size="sm" color="white" />
            {{ loading ? 'Creando...' : 'Crear Usuario' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
