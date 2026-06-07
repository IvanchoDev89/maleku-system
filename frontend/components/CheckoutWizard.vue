<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  User, Mail, Phone, CreditCard, Shield, Check,
  ChevronRight, ChevronLeft, Lock, Calendar, Users,
  MapPin, Sparkles, AlertCircle, Info, Loader2
} from 'lucide-vue-next'

const props = defineProps<{
  totalPrice: number
  travelers?: number
  experienceName?: string
}>()

const emit = defineEmits<{
  complete: [bookingData: any]
  cancel: []
}>()

// Wizard state
const currentStep = ref(1)
const isProcessing = ref(false)
const totalSteps = 3

// Form data
const contactForm = ref({
  firstName: '',
  lastName: '',
  email: '',
  phone: '',
  country: 'CR'
})

const travelers = ref<Array<{
  firstName: string
  lastName: string
  documentType: 'passport' | 'id'
  documentNumber: string
  birthday: string
}>>([
  { firstName: '', lastName: '', documentType: 'id', documentNumber: '', birthday: '' }
])

const paymentForm = ref({
  method: 'card' as 'card' | 'paypal' | 'transfer',
  cardNumber: '',
  cardHolder: '',
  expiry: '',
  cvc: '',
  saveCard: false
})

const extras = ref({
  insurance: true,
  flexibleCancel: false,
  prioritySupport: false
})

// Validation
const isContactValid = computed(() => {
  return contactForm.value.firstName &&
         contactForm.value.lastName &&
         contactForm.value.email &&
         /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(contactForm.value.email) &&
         contactForm.value.phone
})

const isTravelersValid = computed(() => {
  return travelers.value.every(t => 
    t.firstName && t.lastName && t.documentNumber
  )
})

const isPaymentValid = computed(() => {
  if (paymentForm.value.method === 'card') {
    return paymentForm.value.cardNumber.length >= 16 &&
           paymentForm.value.cardHolder &&
           paymentForm.value.expiry &&
           paymentForm.value.cvc.length >= 3
  }
  return true
})

const canProceed = computed(() => {
  switch (currentStep.value) {
    case 1: return isContactValid.value
    case 2: return isTravelersValid.value
    case 3: return isPaymentValid.value
    default: return false
  }
})

// Computed totals
const extrasTotal = computed(() => {
  let total = 0
  if (extras.value.insurance) total += 45
  if (extras.value.flexibleCancel) total += 25
  if (extras.value.prioritySupport) total += 15
  return total * travelers.value.length
})

const finalTotal = computed(() => {
  return props.totalPrice + extrasTotal.value
})

// Methods
const addTraveler = () => {
  if (travelers.value.length < 10) {
    travelers.value.push({
      firstName: '',
      lastName: '',
      documentType: 'id',
      documentNumber: '',
      birthday: ''
    })
  }
}

const removeTraveler = (index: number) => {
  if (travelers.value.length > 1) {
    travelers.value.splice(index, 1)
  }
}

const nextStep = () => {
  if (currentStep.value < totalSteps) {
    currentStep.value++
  }
}

const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

const submitBooking = async () => {
  isProcessing.value = true
  
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 2000))
  
  const bookingData = {
    contact: contactForm.value,
    travelers: travelers.value,
    payment: paymentForm.value,
    extras: extras.value,
    total: finalTotal.value,
    bookingId: 'CR-' + Date.now().toString().slice(-8)
  }
  
  emit('complete', bookingData)
  isProcessing.value = false
}

const formatCardNumber = (value: string) => {
  return value.replace(/\D/g, '').replace(/(\d{4})(?=\d)/g, '$1 ').slice(0, 19)
}

const formatExpiry = (value: string) => {
  return value.replace(/\D/g, '').replace(/(\d{2})(?=\d)/, '$1/').slice(0, 5)
}
</script>

<template>
  <div class="bg-white rounded-3xl shadow-xl overflow-hidden max-w-4xl mx-auto">
    <!-- Header -->
    <div class="bg-gradient-to-r from-primary-600 to-accent-600 p-6 text-white">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-2xl font-bold">Checkout seguro</h2>
          <p class="text-white/80 text-sm">Paso {{ currentStep }} de {{ totalSteps }}</p>
        </div>
        <div class="text-right">
          <p class="text-3xl font-bold">${{ finalTotal.toLocaleString() }}</p>
          <p class="text-white/80 text-sm">Total a pagar</p>
        </div>
      </div>
    </div>

    <!-- Progress -->
    <div class="flex border-b border-gray-200">
      <div 
        v-for="step in totalSteps" 
        :key="step"
        class="flex-1 py-4 text-center text-sm font-medium relative"
        :class="{
          'text-primary-600': currentStep >= step,
          'text-gray-400': currentStep < step
        }"
      >
        <div 
          class="w-8 h-8 rounded-full flex items-center justify-center mx-auto mb-1"
          :class="{
            'bg-primary-600 text-white': currentStep > step,
            'bg-primary-100 text-primary-600 border-2 border-primary-600': currentStep === step,
            'bg-gray-100 text-gray-400': currentStep < step
          }"
        >
          <Check v-if="currentStep > step" class="w-4 h-4" />
          <span v-else>{{ step }}</span>
        </div>
        {{ 
          step === 1 ? 'Contacto' :
          step === 2 ? 'Viajeros' :
          'Pago'
        }}
        <div 
          v-if="step < totalSteps"
          class="absolute top-8 right-0 w-1/2 h-0.5"
          :class="currentStep > step ? 'bg-primary-600' : 'bg-gray-200'"
        />
      </div>
    </div>

    <!-- Content -->
    <div class="p-8">
      <!-- Step 1: Contact -->
      <div v-if="currentStep === 1" class="max-w-xl mx-auto">
        <h3 class="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
          <User class="w-5 h-5 text-primary-600" />
          Información de contacto
        </h3>
        
        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Nombre</label>
              <input 
                v-model="contactForm.firstName"
                type="text"
                class="w-full p-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="Juan"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Apellido</label>
              <input 
                v-model="contactForm.lastName"
                type="text"
                class="w-full p-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="Pérez"
              />
            </div>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input 
              v-model="contactForm.email"
              type="email"
              class="w-full p-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="tu@email.com"
            />
            <p v-if="contactForm.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(contactForm.email)" class="text-red-500 text-sm mt-1">
              Email inválido
            </p>
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Teléfono</label>
              <input 
                v-model="contactForm.phone"
                type="tel"
                class="w-full p-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="+506 8888-8888"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">País</label>
              <select 
                v-model="contactForm.country"
                class="w-full p-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="CR">Costa Rica</option>
                <option value="US">Estados Unidos</option>
                <option value="MX">México</option>
                <option value="ES">España</option>
                <option value="other">Otro</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Contact Summary -->
        <div class="mt-6 p-4 bg-blue-50 rounded-xl">
          <div class="flex items-start gap-3">
            <Info class="w-5 h-5 text-blue-600 mt-0.5" />
            <div class="text-sm text-blue-800">
              <p class="font-medium">¿Por qué necesitamos esto?</p>
              <p>Te enviaremos la confirmación y detalles del viaje a este email. El teléfono es para contactarte en caso de emergencias.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Step 2: Travelers -->
      <div v-if="currentStep === 2" class="max-w-2xl mx-auto">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-xl font-bold text-gray-900 flex items-center gap-2">
            <Users class="w-5 h-5 text-primary-600" />
            Información de viajeros
          </h3>
          <button 
            @click="addTraveler"
            :disabled="travelers.length >= 10"
            class="px-4 py-2 bg-primary-50 text-primary-700 rounded-lg font-medium hover:bg-primary-100 transition-colors disabled:opacity-50"
          >
            + Agregar viajero
          </button>
        </div>

        <div class="space-y-4">
          <div 
            v-for="(traveler, index) in travelers" 
            :key="index"
            class="p-4 border border-gray-200 rounded-xl"
          >
            <div class="flex items-center justify-between mb-4">
              <h4 class="font-medium text-gray-900">Viajero {{ index + 1 }}</h4>
              <button 
                v-if="travelers.length > 1"
                @click="removeTraveler(index)"
                class="text-red-500 text-sm hover:underline"
              >
                Eliminar
              </button>
            </div>
            
            <div class="grid md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm text-gray-600 mb-1">Nombre</label>
                <input 
                  v-model="traveler.firstName"
                  type="text"
                  class="w-full p-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div>
                <label class="block text-sm text-gray-600 mb-1">Apellido</label>
                <input 
                  v-model="traveler.lastName"
                  type="text"
                  class="w-full p-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div>
                <label class="block text-sm text-gray-600 mb-1">Tipo de documento</label>
                <select 
                  v-model="traveler.documentType"
                  class="w-full p-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500"
                >
                  <option value="id">Cédula de identidad</option>
                  <option value="passport">Pasaporte</option>
                </select>
              </div>
              <div>
                <label class="block text-sm text-gray-600 mb-1">Número de documento</label>
                <input 
                  v-model="traveler.documentNumber"
                  type="text"
                  class="w-full p-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div class="md:col-span-2">
                <label class="block text-sm text-gray-600 mb-1">Fecha de nacimiento</label>
                <input 
                  v-model="traveler.birthday"
                  type="date"
                  class="w-full p-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Step 3: Payment -->
      <div v-if="currentStep === 3">
        <div class="grid lg:grid-cols-2 gap-8">
          <!-- Payment Form -->
          <div>
            <h3 class="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
              <CreditCard class="w-5 h-5 text-primary-600" />
              Método de pago
            </h3>

            <!-- Payment Methods -->
            <div class="flex gap-3 mb-6">
              <button 
                @click="paymentForm.method = 'card'"
                class="flex-1 p-4 border-2 rounded-xl transition-all text-left"
                :class="paymentForm.method === 'card' ? 'border-primary-500 bg-primary-50' : 'border-gray-200'"
              >
                <div class="font-medium">Tarjeta de crédito</div>
                <div class="text-sm text-gray-500">Visa, Mastercard, Amex</div>
              </button>
              <button 
                @click="paymentForm.method = 'paypal'"
                class="flex-1 p-4 border-2 rounded-xl transition-all text-left"
                :class="paymentForm.method === 'paypal' ? 'border-primary-500 bg-primary-50' : 'border-gray-200'"
              >
                <div class="font-medium">PayPal</div>
                <div class="text-sm text-gray-500">Pago rápido y seguro</div>
              </button>
            </div>

            <!-- Card Form -->
            <div v-if="paymentForm.method === 'card'" class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Número de tarjeta</label>
                <div class="relative">
                  <input 
                    :value="paymentForm.cardNumber"
                    @input="paymentForm.cardNumber = formatCardNumber($event.target.value)"
                    type="text"
                    class="w-full p-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent font-mono"
                    placeholder="1234 5678 9012 3456"
                  />
                  <CreditCard class="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                </div>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Titular de la tarjeta</label>
                <input 
                  v-model="paymentForm.cardHolder"
                  type="text"
                  class="w-full p-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="NOMBRE APELLIDO"
                />
              </div>

              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Vencimiento</label>
                  <div class="relative">
                    <input 
                      :value="paymentForm.expiry"
                      @input="paymentForm.expiry = formatExpiry($event.target.value)"
                      type="text"
                      class="w-full p-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      placeholder="MM/AA"
                    />
                    <Calendar class="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  </div>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">CVC</label>
                  <div class="relative">
                    <input 
                      v-model="paymentForm.cvc"
                      type="text"
                      maxlength="4"
                      class="w-full p-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      placeholder="123"
                    />
                    <Lock class="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  </div>
                </div>
              </div>

              <label class="flex items-center gap-3 p-3 bg-gray-50 rounded-xl cursor-pointer">
                <input 
                  v-model="paymentForm.saveCard"
                  type="checkbox"
                  class="w-5 h-5 text-primary-600 rounded focus:ring-primary-500"
                />
                <span class="text-sm text-gray-700">Guardar tarjeta para futuras compras</span>
              </label>
            </div>

            <!-- PayPal Form -->
            <div v-else class="p-8 text-center">
              <p class="text-gray-600 mb-4">Serás redirigido a PayPal para completar el pago de forma segura.</p>
              <button class="px-8 py-3 bg-[#0070BA] text-white rounded-xl font-medium hover:bg-[#003087] transition-colors">
                Continuar con PayPal
              </button>
            </div>

            <!-- Security Badge -->
            <div class="mt-6 flex items-center justify-center gap-4 text-sm text-gray-500">
              <div class="flex items-center gap-1">
                <Lock class="w-4 h-4" />
                <span>Encriptación SSL</span>
              </div>
              <div class="flex items-center gap-1">
                <Shield class="w-4 h-4" />
                <span>PCI Compliant</span>
              </div>
            </div>
          </div>

          <!-- Order Summary -->
          <div class="lg:pl-8 lg:border-l border-gray-200">
            <h3 class="text-xl font-bold text-gray-900 mb-6">Resumen del pedido</h3>
            
            <!-- Experience -->
            <div v-if="experienceName" class="flex items-start gap-3 mb-4 p-3 bg-gray-50 rounded-xl">
              <MapPin class="w-5 h-5 text-primary-600 mt-0.5" />
              <div>
                <p class="font-medium text-gray-900">{{ experienceName }}</p>
                <p class="text-sm text-gray-500">{{ travelers.length }} viajero{{ travelers.length > 1 ? 's' : '' }}</p>
              </div>
            </div>

            <!-- Extras -->
            <div class="space-y-3 mb-6">
              <h4 class="font-medium text-gray-900">Servicios adicionales</h4>
              
              <label class="flex items-center justify-between p-3 border border-gray-200 rounded-xl cursor-pointer hover:border-primary-300 transition-colors">
                <div class="flex items-center gap-3">
                  <input 
                    v-model="extras.insurance"
                    type="checkbox"
                    class="w-5 h-5 text-primary-600 rounded focus:ring-primary-500"
                  />
                  <div>
                    <p class="font-medium text-gray-900">Seguro de viaje</p>
                    <p class="text-sm text-gray-500">Cobertura médica y cancelación</p>
                  </div>
                </div>
                <span class="font-medium text-gray-900">$45</span>
              </label>
              
              <label class="flex items-center justify-between p-3 border border-gray-200 rounded-xl cursor-pointer hover:border-primary-300 transition-colors">
                <div class="flex items-center gap-3">
                  <input 
                    v-model="extras.flexibleCancel"
                    type="checkbox"
                    class="w-5 h-5 text-primary-600 rounded focus:ring-primary-500"
                  />
                  <div>
                    <p class="font-medium text-gray-900">Cancelación flexible</p>
                    <p class="text-sm text-gray-500">Reembolso hasta 24h antes</p>
                  </div>
                </div>
                <span class="font-medium text-gray-900">$25</span>
              </label>
              
              <label class="flex items-center justify-between p-3 border border-gray-200 rounded-xl cursor-pointer hover:border-primary-300 transition-colors">
                <div class="flex items-center gap-3">
                  <input 
                    v-model="extras.prioritySupport"
                    type="checkbox"
                    class="w-5 h-5 text-primary-600 rounded focus:ring-primary-500"
                  />
                  <div>
                    <p class="font-medium text-gray-900">Soporte prioritario</p>
                    <p class="text-sm text-gray-500">Atención 24/7 dedicada</p>
                  </div>
                </div>
                <span class="font-medium text-gray-900">$15</span>
              </label>
            </div>

            <!-- Totals -->
            <div class="border-t pt-4 space-y-2">
              <div class="flex justify-between text-gray-600">
                <span>Experiencia</span>
                <span>${{ totalPrice.toLocaleString() }}</span>
              </div>
              <div v-if="extrasTotal > 0" class="flex justify-between text-gray-600">
                <span>Extras</span>
                <span>${{ extrasTotal.toLocaleString() }}</span>
              </div>
              <div class="flex justify-between items-center pt-4 border-t">
                <span class="font-bold text-lg text-gray-900">Total</span>
                <span class="font-bold text-2xl text-primary-600">${{ finalTotal.toLocaleString() }}</span>
              </div>
              <p class="text-sm text-gray-500 text-right">
                ${{ Math.round(finalTotal / travelers.length).toLocaleString() }} por persona
              </p>
            </div>

            <!-- Submit Button -->
            <button 
              @click="submitBooking"
              :disabled="!canProceed || isProcessing"
              class="w-full mt-6 py-4 bg-gradient-to-r from-primary-600 to-accent-600 text-white rounded-xl font-bold text-lg hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              <Loader2 v-if="isProcessing" class="w-5 h-5 animate-spin" />
              <Lock v-else class="w-5 h-5" />
              <span v-if="isProcessing">Procesando...</span>
              <span v-else>Pagar ${{ finalTotal.toLocaleString() }}</span>
            </button>

            <p class="text-center text-sm text-gray-500 mt-4">
              Al completar la compra, aceptas nuestros términos y condiciones
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer Navigation -->
    <div v-if="currentStep < 4" class="flex justify-between p-6 border-t border-gray-200 bg-gray-50">
      <button 
        v-if="currentStep > 1"
        @click="prevStep"
        class="px-6 py-3 bg-white border border-gray-300 rounded-xl font-medium text-gray-700 hover:bg-gray-50 transition-colors flex items-center gap-2"
      >
        <ChevronLeft class="w-5 h-5" />
        Anterior
      </button>
      <div v-else></div>
      
      <button 
        v-if="currentStep < 3"
        @click="nextStep"
        :disabled="!canProceed"
        class="px-6 py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Continuar
        <ChevronRight class="w-5 h-5" />
      </button>
    </div>
  </div>
</template>
