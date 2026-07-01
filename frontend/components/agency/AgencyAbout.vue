<template>
  <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 sm:p-8">
    <h2 class="text-xl font-bold text-gray-900 mb-4">Sobre Nosotros</h2>
    <p v-if="vendor.description" class="text-gray-600 leading-relaxed whitespace-pre-line">
      {{ vendor.description }}
    </p>
    <p v-else class="text-gray-400 italic">Sin descripción disponible</p>

    <div v-if="vendor.phone || vendor.email || vendor.address" class="mt-6 pt-6 border-t border-gray-100">
      <h3 class="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">Contacto</h3>
      <div class="space-y-2">
        <div v-if="vendor.phone" class="flex items-center gap-3 text-gray-600">
          <Icon name="lucide:phone" class="w-4 h-4 text-gray-400 shrink-0" />
          <a :href="`tel:${vendor.phone}`" class="hover:text-primary-600 transition-colors">{{ vendor.phone }}</a>
        </div>
        <div v-if="vendor.email" class="flex items-center gap-3 text-gray-600">
          <Icon name="lucide:mail" class="w-4 h-4 text-gray-400 shrink-0" />
          <a :href="`mailto:${vendor.email}`" class="hover:text-primary-600 transition-colors">{{ vendor.email }}</a>
        </div>
        <div v-if="vendor.address" class="flex items-center gap-3 text-gray-600">
          <Icon name="lucide:map-pin" class="w-4 h-4 text-gray-400 shrink-0" />
          <span>{{ vendor.address }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  vendor: {
    description: string | null
    phone: string | null
    email: string | null
    address: string | null
  }
}>()
</script>
