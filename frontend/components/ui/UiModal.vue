<script setup lang="ts">
import { watch } from 'vue'

interface Props {
  modelValue: boolean
  title?: string
  maxWidth?: string
  closeable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  maxWidth: 'max-w-lg',
  closeable: true
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

watch(() => props.modelValue, (val) => {
  if (val) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})

function close() {
  if (props.closeable) {
    emit('update:modelValue', false)
  }
}

function onBackdropClick(e: MouseEvent) {
  if ((e.target as HTMLElement).dataset?.backdrop) {
    close()
  }
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') close()
}
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-[9998] flex items-center justify-center p-4"
        @keydown="onKeydown"
        tabindex="-1"
      >
        <div class="fixed inset-0 bg-black/50 backdrop-blur-sm" data-backdrop="true" @click="onBackdropClick" />
        <div
          :class="['relative bg-white rounded-2xl shadow-elevated w-full overflow-hidden', maxWidth]"
          role="dialog"
          :aria-modal="true"
          :aria-label="title || 'Diálogo'"
        >
          <div v-if="title" class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
            <h2 class="text-lg font-semibold text-gray-900">{{ title }}</h2>
            <button
              v-if="closeable"
              @click="close"
              class="p-1.5 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
              aria-label="Cerrar"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div class="px-6 py-4 max-h-[70vh] overflow-y-auto">
            <slot />
          </div>
          <div v-if="$slots.footer" class="flex justify-end gap-3 px-6 py-4 border-t border-gray-100 bg-gray-50">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-enter-active { animation: modal-in 0.2s ease-out; }
.modal-leave-active { animation: modal-out 0.15s ease-in; }
@keyframes modal-in {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
@keyframes modal-out {
  from { opacity: 1; transform: scale(1); }
  to { opacity: 0; transform: scale(0.95); }
}
</style>
