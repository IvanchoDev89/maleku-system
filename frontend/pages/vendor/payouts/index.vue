<template>
  <div>
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-2xl font-bold">Pagos</h1>
        <p class="text-gray-500">Historial de pagos y ganancias</p>
      </div>
    </div>

    <div class="space-y-6">
      <!-- Balance Card -->
      <div class="bg-white rounded-xl shadow-sm p-6">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <p class="text-gray-500 text-sm">Balance Disponible</p>
            <p class="text-3xl font-bold text-green-600">$1,250.00</p>
          </div>
          <div>
            <p class="text-gray-500 text-sm">Pendiente</p>
            <p class="text-3xl font-bold text-yellow-600">$850.00</p>
          </div>
          <div>
            <p class="text-gray-500 text-sm">Total Ganado</p>
            <p class="text-3xl font-bold">$12,580.00</p>
          </div>
        </div>
      </div>

      <!-- Payout History -->
      <div class="bg-white rounded-xl shadow-sm overflow-hidden">
        <div class="p-4 border-b">
          <h3 class="font-bold">Historial de Pagos</h3>
        </div>
        <table class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="text-left py-3 px-4 font-semibold text-gray-600">Fecha</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600">Monto</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600">Método</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600">Estado</th>
            </tr>
          </thead>
          <tbody>
            <tr class="border-t">
              <td class="py-3 px-4 text-sm">15 Mar 2026</td>
              <td class="py-3 px-4 font-semibold">$850.00</td>
              <td class="py-3 px-4">Stripe</td>
              <td class="py-3 px-4">
                <span class="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">Completado</span>
              </td>
            </tr>
            <tr class="border-t">
              <td class="py-3 px-4 text-sm">01 Mar 2026</td>
              <td class="py-3 px-4 font-semibold">$1,200.00</td>
              <td class="py-3 px-4">Stripe</td>
              <td class="py-3 px-4">
                <span class="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">Completado</span>
              </td>
            </tr>
            <tr class="border-t">
              <td class="py-3 px-4 text-sm">15 Feb 2026</td>
              <td class="py-3 px-4 font-semibold">$650.00</td>
              <td class="py-3 px-4">Stripe</td>
              <td class="py-3 px-4">
                <span class="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">Completado</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'vendor',
  middleware: ['auth']
})
</script>