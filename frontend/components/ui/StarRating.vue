<template>
  <div class="flex items-center gap-1" :class="sizeClass">
    <span v-for="i in max" :key="i" class="inline-block" :class="starClass(i)">
      <Icon v-if="i <= filled" name="lucide:star" class="fill-current" />
      <Icon v-else-if="i - 0.5 <= filled" name="lucide:star-half" class="fill-current" />
      <Icon v-else name="lucide:star" />
    </span>
    <span v-if="showValue" class="ml-1.5 font-semibold text-gray-700 text-sm">
      {{ rounded }}
    </span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  rating: number
  max?: number
  size?: 'sm' | 'md' | 'lg'
  showValue?: boolean
}>(), {
  max: 5,
  size: 'md',
  showValue: false,
})

const filled = computed(() => Math.max(0, Math.min(props.max, props.rating)))
const rounded = computed(() => Math.round(props.rating * 10) / 10)

const sizeClass = computed(() => {
  const sizes = { sm: 'text-sm', md: 'text-base', lg: 'text-xl' }
  return sizes[props.size]
})

const starClass = (i: number) => {
  const val = filled.value
  const base = 'transition-colors'
  const color = i <= val || i - 0.5 <= val
    ? 'text-amber-400'
    : 'text-gray-300'
  return `${base} ${color}`
}
</script>
