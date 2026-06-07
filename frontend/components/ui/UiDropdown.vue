<script setup lang="ts">
import { ref } from 'vue'
import { onClickOutside } from '@vueuse/core'

interface Props {
  align?: 'left' | 'right'
}

const props = withDefaults(defineProps<Props>(), {
  align: 'left'
})

const open = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)

onClickOutside(dropdownRef, () => { open.value = false })

function toggle() { open.value = !open.value }
function close() { open.value = false }
</script>

<template>
  <div ref="dropdownRef" class="relative inline-block">
    <div @click="toggle" @keydown.enter="toggle" @keydown.space.prevent="toggle" role="button" tabindex="0" :aria-expanded="open">
      <slot name="trigger" />
    </div>
    <Transition name="dropdown">
      <div
        v-if="open"
        :class="[
          'absolute top-full mt-1 z-50 min-w-[180px] bg-white rounded-xl shadow-elevated border border-gray-100 py-1 overflow-hidden',
          align === 'right' ? 'right-0' : 'left-0'
        ]"
        @click="close"
      >
        <slot name="items" />
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.dropdown-enter-active { animation: drop-in 0.15s ease-out; }
.dropdown-leave-active { animation: drop-out 0.1s ease-in; }
@keyframes drop-in {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes drop-out {
  from { opacity: 1; transform: translateY(0); }
  to { opacity: 0; transform: translateY(-4px); }
}
</style>
