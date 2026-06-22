<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { ChevronLeft, ChevronRight, Check, X } from 'lucide-vue-next'
import type { CalendarDay } from '~/types'

const props = defineProps<{
  roomId: string
  checkIn?: string | null
  checkOut?: string | null
  minStay?: number
  pricePerNight?: number
}>()

const emit = defineEmits<{
  'update:checkIn': [value: string | null]
  'update:checkOut': [value: string | null]
  nightsChanged: [nights: number]
}>()

const api = useApi()

const loading = ref(true)
const error = ref('')
const calendarDays = ref<CalendarDay[]>([])
const currentMonth = ref(new Date().getMonth())
const currentYear = ref(new Date().getFullYear())
const hoverDate = ref<string | null>(null)

const monthNames = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

const dayNames = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']

const viewStart = computed(() => new Date(currentYear.value, currentMonth.value, 1))
const viewEnd = computed(() => {
  const d = new Date(currentYear.value, currentMonth.value + 1, 0)
  d.setDate(d.getDate() + 1)
  return d
})

const daysInMonth = computed(() => {
  const start = viewStart.value
  const end = viewEnd.value
  const days: { date: string; day: number; isPadding: boolean }[] = []

  const padStart = start.getDay()
  for (let i = padStart - 1; i >= 0; i--) {
    const d = new Date(start)
    d.setDate(d.getDate() - i - 1)
    days.push({ date: fmtDate(d), day: d.getDate(), isPadding: true })
  }

  for (let d = new Date(start); d < end; d.setDate(d.getDate() + 1)) {
    days.push({ date: fmtDate(d), day: d.getDate(), isPadding: false })
  }

  const remaining = 42 - days.length
  for (let i = 0; i < remaining; i++) {
    const d = new Date(end)
    d.setDate(d.getDate() + i)
    days.push({ date: fmtDate(d), day: d.getDate(), isPadding: true })
  }

  return days
})

const fmtDate = (d: Date) => {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

const getDayData = (dateStr: string): CalendarDay | undefined => {
  return calendarDays.value.find(d => d.date === dateStr)
}

const isSelectable = (dateStr: string): boolean => {
  const day = getDayData(dateStr)
  if (!day) return false
  if (day.is_past) return false
  if (!day.available) return false
  return true
}

const isInRange = (dateStr: string): boolean => {
  if (!props.checkIn || !hoverDate.value) return false
  if (dateStr === props.checkIn) return false
  const d = new Date(dateStr)
  const ci = new Date(props.checkIn)
  const ho = new Date(hoverDate.value)
  if (ho < ci) return d <= ci && d >= ho
  return d >= ci && d <= ho
}

const getPriceForDate = (dateStr: string): number | null => {
  const day = getDayData(dateStr)
  if (day?.price_override != null) return day.price_override
  return props.pricePerNight ?? null
}

const selectDate = (dateStr: string) => {
  if (!isSelectable(dateStr)) return

  if (!props.checkIn || (props.checkIn && props.checkOut)) {
    emit('update:checkIn', dateStr)
    emit('update:checkOut', null)
    emit('nightsChanged', 0)
    return
  }

  const ci = new Date(props.checkIn)
  const cd = new Date(dateStr)

  if (cd < ci) {
    emit('update:checkIn', dateStr)
    emit('update:checkOut', null)
    emit('nightsChanged', 0)
    return
  }

  if (cd.getTime() === ci.getTime()) {
    emit('update:checkIn', null)
    emit('update:checkOut', null)
    emit('nightsChanged', 0)
    return
  }

  emit('update:checkOut', dateStr)
  const nights = Math.round((cd.getTime() - ci.getTime()) / (1000 * 60 * 60 * 24))
  emit('nightsChanged', nights)
}

const dayClass = (dateStr: string) => {
  const day = getDayData(dateStr)
  if (!day) return ''

  const classes: string[] = []

  if (day.is_past || !day.available) classes.push('opacity-40 cursor-not-allowed')
  else classes.push('cursor-pointer hover:bg-primary-100')

  if (dateStr === props.checkIn || dateStr === props.checkOut) {
    classes.push('bg-primary-600 text-white hover:bg-primary-700')
  } else if (isInRange(dateStr)) {
    classes.push('bg-primary-50')
  }

  if (day.price_override != null && day.price_override !== props.pricePerNight) {
    classes.push('ring-2 ring-amber-400')
  }

  return classes.join(' ')
}

const loadCalendar = async () => {
  loading.value = true
  error.value = ''
  try {
    const data = await api.get<{ room_id: string; dates: CalendarDay[] }>(
      `/availability/rooms/${props.roomId}/calendar`,
      {
        start_date: viewStart.value.toISOString(),
        days: 60,
      }
    )
    calendarDays.value = data.dates || []
  } catch (e: any) {
    error.value = 'Error al cargar disponibilidad'
  } finally {
    loading.value = false
  }
}

const prevMonth = () => {
  if (currentMonth.value === 0) {
    currentMonth.value = 11
    currentYear.value--
  } else {
    currentMonth.value--
  }
}

const nextMonth = () => {
  if (currentMonth.value === 11) {
    currentMonth.value = 0
    currentYear.value++
  } else {
    currentMonth.value++
  }
}

watch([currentMonth, currentYear], () => { loadCalendar() })

onMounted(() => { loadCalendar() })
</script>

<template>
  <div class="bg-white rounded-xl border border-gray-200 p-4">
    <!-- Header -->
    <div class="flex items-center justify-between mb-4">
      <button
        @click="prevMonth"
        class="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
        :disabled="loading"
      >
        <ChevronLeft class="w-5 h-5 text-gray-600" />
      </button>
      <h3 class="font-semibold text-gray-900">
        {{ monthNames[currentMonth] }} {{ currentYear }}
      </h3>
      <button
        @click="nextMonth"
        class="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
        :disabled="loading"
      >
        <ChevronRight class="w-5 h-5 text-gray-600" />
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="py-8 text-center text-gray-500 text-sm">
      <div class="animate-pulse space-y-2">
        <div class="h-4 bg-gray-200 rounded w-3/4 mx-auto"></div>
        <div class="h-4 bg-gray-200 rounded w-1/2 mx-auto"></div>
      </div>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="py-4 text-center text-red-500 text-sm">
      {{ error }}
    </div>

    <!-- Calendar Grid -->
    <div v-else>
      <div class="grid grid-cols-7 mb-1">
        <div
          v-for="dn in dayNames"
          :key="dn"
          class="text-center text-xs font-medium text-gray-500 py-1"
        >
          {{ dn }}
        </div>
      </div>

      <div class="grid grid-cols-7">
        <div
          v-for="(cell, idx) in daysInMonth"
          :key="idx"
          class="relative"
        >
          <div
            v-if="!cell.isPadding"
            :class="[
              'w-full aspect-square flex items-center justify-center text-sm rounded-lg transition-colors',
              dayClass(cell.date)
            ]"
            @click="selectDate(cell.date)"
            @mouseenter="hoverDate = cell.date"
            @mouseleave="hoverDate = null"
          >
            <div class="flex flex-col items-center leading-tight">
              <span>{{ cell.day }}</span>
              <span
                v-if="getPriceForDate(cell.date) && getPriceForDate(cell.date) !== pricePerNight"
                class="text-[9px] text-amber-600 font-medium"
              >${{ getPriceForDate(cell.date) }}</span>
            </div>
          </div>
          <div v-else class="w-full aspect-square"></div>
        </div>
      </div>

      <!-- Legend -->
      <div class="flex items-center gap-4 mt-3 pt-3 border-t border-gray-100 text-xs text-gray-500">
        <div class="flex items-center gap-1">
          <div class="w-3 h-3 rounded bg-primary-100"></div>
          <span>Seleccionado</span>
        </div>
        <div class="flex items-center gap-1">
          <div class="w-3 h-3 rounded bg-green-100 border border-green-300"></div>
          <span>Disponible</span>
        </div>
        <div class="flex items-center gap-1">
          <div class="w-3 h-3 rounded bg-gray-100"></div>
          <span>No disponible</span>
        </div>
        <div class="flex items-center gap-1">
          <div class="w-3 h-3 rounded border-2 border-amber-400"></div>
          <span>Precio especial</span>
        </div>
      </div>
    </div>
  </div>
</template>
