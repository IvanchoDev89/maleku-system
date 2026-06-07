<script setup lang="ts">
import { ref, reactive, computed } from 'vue'

useSeo({
  title: 'Contacto',
  description: 'Contáctanos para información sobre viajes, reservas y experiencias en Costa Rica.'
})

const form = reactive({
  name: '',
  email: '',
  message: ''
})

const errors = reactive({
  name: '',
  email: '',
  message: ''
})

const loading = ref(false)
const success = ref(false)

const isValidEmail = (email: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)

const formValid = computed(() => {
  return form.name.trim() && isValidEmail(form.email) && form.message.trim().length >= 10
})

function validate() {
  let valid = true
  errors.name = ''
  errors.email = ''
  errors.message = ''

  if (!form.name.trim()) {
    errors.name = 'El nombre es obligatorio'
    valid = false
  }

  if (!form.email.trim()) {
    errors.email = 'El email es obligatorio'
    valid = false
  } else if (!isValidEmail(form.email)) {
    errors.email = 'Email inválido'
    valid = false
  }

  if (!form.message.trim()) {
    errors.message = 'El mensaje es obligatorio'
    valid = false
  } else if (form.message.trim().length < 10) {
    errors.message = 'El mensaje debe tener al menos 10 caracteres'
    valid = false
  }

  return valid
}

async function handleSubmit() {
  if (!validate()) return

  loading.value = true
  success.value = false

  try {
    const api = useApi()
    await api.post('/contact', {
      name: form.name,
      email: form.email,
      message: form.message
    })
    form.name = ''
    form.email = ''
    form.message = ''
    success.value = true
    setTimeout(() => { success.value = false }, 5000)
  } catch (e) {
    errors.message = 'Error al enviar el mensaje. Intenta de nuevo.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 py-12">
    <div class="container mx-auto px-4 max-w-4xl">
      <h1 class="text-3xl font-bold mb-8">Contacto</h1>
      <div class="grid md:grid-cols-2 gap-8">
        <div>
          <h2 class="text-xl font-semibold mb-4">Información de contacto</h2>
          <div class="space-y-4">
            <div>
              <p class="font-medium">Email</p>
              <p class="text-gray-600">info@costaricatravel.dev</p>
            </div>
            <div>
              <p class="font-medium">Teléfono</p>
              <p class="text-gray-600">+506 8000-0000</p>
            </div>
            <div>
              <p class="font-medium">Horario</p>
              <p class="text-gray-600">Lunes a Viernes, 8am - 6pm CST</p>
            </div>
            <div>
              <p class="font-medium">Dirección</p>
              <p class="text-gray-600">San José, Costa Rica</p>
            </div>
          </div>
        </div>
        <div>
          <h2 class="text-xl font-semibold mb-4">Envíanos un mensaje</h2>
          <form @submit.prevent="handleSubmit" class="space-y-4" novalidate>
            <UiInput v-model="form.name" label="Nombre" placeholder="Tu nombre" required :error="errors.name" />
            <UiInput v-model="form.email" type="email" label="Email" placeholder="tu@email.com" required :error="errors.email" />
            <UiTextarea v-model="form.message" label="Mensaje" placeholder="¿En qué podemos ayudarte?" required :error="errors.message" :max-length="1000" />

            <div v-if="success" class="p-3 bg-green-50 border border-green-200 rounded-xl">
              <p class="text-green-700 text-sm text-center">Mensaje enviado con éxito. Te contactaremos pronto.</p>
            </div>

            <UiButton type="submit" variant="primary" size="lg" full-width :loading="loading" :disabled="!formValid">
              {{ loading ? 'Enviando...' : 'Enviar mensaje' }}
            </UiButton>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>
