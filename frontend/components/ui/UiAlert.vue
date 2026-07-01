<script setup lang="ts">
import { AlertCircle, AlertTriangle, CheckCircle, Info, X } from 'lucide-vue-next'

interface Props {
  variant?: 'info' | 'success' | 'warning' | 'error'
  dismissible?: boolean
  title?: string
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'info',
  dismissible: false,
})

const emit = defineEmits<{
  dismiss: []
}>()

const visible = ref(true)

function dismiss() {
  visible.value = false
  emit('dismiss')
}

const iconMap = {
  info: Info,
  success: CheckCircle,
  warning: AlertTriangle,
  error: AlertCircle,
}

const styleMap = {
  info: { bg: 'bg-blue-50', border: 'border-blue-200', icon: 'text-blue-500', title: 'text-blue-800', text: 'text-blue-700' },
  success: { bg: 'bg-green-50', border: 'border-green-200', icon: 'text-green-500', title: 'text-green-800', text: 'text-green-700' },
  warning: { bg: 'bg-amber-50', border: 'border-amber-200', icon: 'text-amber-500', title: 'text-amber-800', text: 'text-amber-700' },
  error: { bg: 'bg-red-50', border: 'border-red-200', icon: 'text-red-500', title: 'text-red-800', text: 'text-red-700' },
}
</script>

<template>
  <Transition name="alert">
    <div v-if="visible" role="alert" :class="[styleMap[variant].bg, styleMap[variant].border, 'rounded-xl border p-4']">
      <div class="flex items-start gap-3">
        <component :is="iconMap[variant]" :class="[styleMap[variant].icon, 'w-5 h-5 mt-0.5 shrink-0']" />
        <div class="flex-1 min-w-0">
          <p v-if="title" :class="[styleMap[variant].title, 'font-semibold text-sm']">{{ title }}</p>
          <div :class="[styleMap[variant].text, 'text-sm', { 'mt-1': !!title }]">
            <slot />
          </div>
        </div>
        <button
          v-if="dismissible"
          @click="dismiss"
          :class="[styleMap[variant].text, 'hover:opacity-70 transition-opacity shrink-0']"
          aria-label="Cerrar"
        >
          <X class="w-4 h-4" />
        </button>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.alert-enter-active { transition: all 0.3s ease; }
.alert-leave-active { transition: all 0.2s ease; }
.alert-enter-from { opacity: 0; transform: translateY(-8px); }
.alert-leave-to { opacity: 0; transform: translateY(-8px); }
</style>
