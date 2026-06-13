<script setup lang="ts">
/**
 * FAQ Section
 * Preguntas frecuentes con acordion
 */
import { ref } from 'vue'

const openIndex = ref<number | null>(0)

const faqs = [
  {
    question: '¿Cuál es la mejor época para visitar Costa Rica?',
    answer: 'La temporada seca (diciembre - abril) es ideal para playas y actividades al aire libre. La temporada verde (mayo - noviembre) ofrece precios más bajos, menos turistas y la selva en su máximo esplendor. Ambas temporadas tienen sus ventajas dependiendo de tus preferencias.'
  },
  {
    question: '¿Necesito visa para entrar a Costa Rica?',
    answer: 'Ciudadanos de EE.UU., Canadá, UE y la mayoría de países latinoamericanos no necesitan visa para estancias de hasta 90 días. Solo necesitas pasaporte vigente (6+ meses de validez) y boleto de salida. Revisa requisitos específicos según tu nacionalidad.'
  },
  {
    question: '¿Es seguro viajar a Costa Rica?',
    answer: 'Costa Rica es uno de los países más seguros de Centroamérica. Como en cualquier destino turístico, se recomienda precaución básica con pertenencias en zonas concurridas. No se requieren vacunas especiales y el agua potable es segura en la mayoría del país.'
  },
  {
    question: '¿Cuánto cuesta un viaje típico a Costa Rica?',
    answer: 'Un viaje de 7 días puede costar entre $1,200-$3,000+ por persona dependiendo del nivel de alojamiento y actividades. Incluimos opciones para todos los presupuestos: hostales desde $20/noche hasta resorts de lujo en $500+/noche. Nuestros paquetes ofrecen los mejores precios garantizados.'
  },
  {
    question: '¿Qué debo empacar para Costa Rica?',
    answer: 'Ropa ligera y de secado rápido, protector solar biodegradable (obligatorio en parques), repelente de insectos, impermeable ligero, zapatos para caminar, traje de baño y sandalias. Para zonas de montaña (Monteverde) incluye una chaqueta ligera. Deja espacio en tu maleta para souvenirs de café y artesanías.'
  },
  {
    question: '¿Puedo cancelar o modificar mi reserva?',
    answer: 'Sí, ofrecemos cancelación gratuita hasta 48 horas antes para la mayoría de tours y actividades. Hoteles y paquetes tienen políticas específicas según la temporada. Puedes modificar fechas sin costo adicional hasta 72 horas antes. Revisa los términos específicos de cada reserva en tu confirmación.'
  }
]

const toggleFaq = (index: number) => {
  openIndex.value = openIndex.value === index ? null : index
}
</script>

<template>
  <section class="py-20 bg-gray-50">
    <div class="container mx-auto px-4 max-w-4xl">
      <!-- Header -->
      <div class="text-center mb-12">
        <span class="inline-block px-4 py-1.5 bg-primary-100 text-primary-600 font-semibold rounded-full text-sm mb-4">
          ¿Preguntas?
        </span>
        <h2 class="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
          Preguntas Frecuentes
        </h2>
        <p class="text-xl text-gray-600">
          Todo lo que necesitas saber antes de tu viaje
        </p>
      </div>

      <!-- FAQ Accordion -->
      <div class="space-y-4">
        <div
          v-for="(faq, index) in faqs"
          :key="index"
          class="bg-white rounded-xl shadow-sm overflow-hidden"
        >
          <button
            @click="toggleFaq(index)"
            class="w-full px-6 py-5 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
          >
            <span class="font-semibold text-gray-900 pr-4">{{ faq.question }}</span>
            <span
              :class="['text-primary-600 text-2xl transition-transform duration-300', openIndex === index ? 'rotate-45' : '']"
            >
              +
            </span>
          </button>
          <Transition
            enter="transition-all duration-300 ease-out"
            enter-from="opacity-0 max-h-0"
            enter-to="opacity-100 max-h-96"
            leave="transition-all duration-300 ease-in"
            leave-from="opacity-100 max-h-96"
            leave-to="opacity-0 max-h-0"
          >
            <div
              v-show="openIndex === index"
              class="overflow-hidden"
            >
              <div class="px-6 pb-5 text-gray-600 leading-relaxed">
                {{ faq.answer }}
              </div>
            </div>
          </Transition>
        </div>
      </div>

      <!-- More Questions CTA -->
      <div class="mt-12 text-center bg-white rounded-2xl p-8 shadow-sm">
        <h3 class="text-xl font-bold text-gray-900 mb-2">¿Tienes más preguntas?</h3>
        <p class="text-gray-600 mb-4">
          Nuestro equipo está listo para ayudarte a planificar el viaje perfecto.
        </p>
        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <a
            href="mailto:ayuda@costaricatravel.dev"
            class="inline-flex items-center justify-center gap-2 px-6 py-3 bg-primary-600 text-white font-semibold rounded-xl hover:bg-primary-700 transition-colors"
          >
            <span>✉️</span>
            Escríbenos
          </a>
          <NuxtLink
            to="/ayuda"
            class="inline-flex items-center justify-center gap-2 px-6 py-3 border-2 border-gray-300 text-gray-700 font-semibold rounded-xl hover:border-primary-600 hover:text-primary-600 transition-colors"
          >
            <span>📚</span>
            Centro de Ayuda
          </NuxtLink>
        </div>
      </div>
    </div>
  </section>
</template>
