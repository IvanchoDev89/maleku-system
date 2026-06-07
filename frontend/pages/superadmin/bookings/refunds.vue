<script setup lang="ts">
/**
 * Refunds Management
 * Gestion de reembolsos
 */
import { ref } from 'vue'

definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

interface Refund {
  id: string
  bookingId: string
  customer: string
  amount: number
  reason: string
  status: 'pending' | 'approved' | 'rejected' | 'processed'
  requestedAt: string
}

const refunds = ref<Refund[]>([
  { id: 'R-001', bookingId: 'BK-004', customer: 'Lisa Johnson', amount: 95, reason: 'Cancelacion por enfermedad', status: 'pending', requestedAt: '2024-02-03' },
  { id: 'R-002', bookingId: 'BK-015', customer: 'Carlos Ruiz', amount: 250, reason: 'No cumplio expectativas', status: 'approved', requestedAt: '2024-02-01' },
  { id: 'R-003', bookingId: 'BK-023', customer: 'Anna Schmidt', amount: 450, reason: 'Doble pago', status: 'processed', requestedAt: '2024-01-28' }
])

const statusColors = {
  pending: 'bg-yellow-100 text-yellow-800',
  approved: 'bg-blue-100 text-blue-800',
  rejected: 'bg-red-100 text-red-800',
  processed: 'bg-green-100 text-green-800'
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Reembolsos</h1>
        <p class="mt-1 text-gray-500">Gestion de solicitudes de reembolso</p>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Pendientes</div>
        <div class="text-3xl font-bold text-yellow-600">{{ refunds.filter(r => r.status === 'pending').length }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Aprobados</div>
        <div class="text-3xl font-bold text-blue-600">{{ refunds.filter(r => r.status === 'approved').length }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Procesados</div>
        <div class="text-3xl font-bold text-green-600">{{ refunds.filter(r => r.status === 'processed').length }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Monto Total Pendiente</div>
        <div class="text-3xl font-bold text-gray-900">
          ${{ refunds.filter(r => r.status === 'pending').reduce((sum, r) => sum + r.amount, 0) }}
        </div>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reserva</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cliente</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Monto</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Motivo</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Acciones</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="refund in refunds" :key="refund.id">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ refund.id }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-blue-600">{{ refund.bookingId }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ refund.customer }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${{ refund.amount }}</td>
            <td class="px-6 py-4 text-sm text-gray-500">{{ refund.reason }}</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="['px-2 py-1 text-xs font-medium rounded-full', statusColors[refund.status]]">
                {{ refund.status }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <button v-if="refund.status === 'pending'" class="text-green-600 hover:text-green-900 mr-2">Aprobar</button>
              <button v-if="refund.status === 'pending'" class="text-red-600 hover:text-red-900">Rechazar</button>
              <button v-if="refund.status === 'approved'" class="text-blue-600 hover:text-blue-900">Procesar</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
