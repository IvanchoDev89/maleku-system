<script setup lang="ts">
interface Props {
  variant?: 'text' | 'card' | 'table-row' | 'avatar' | 'image'
  width?: string
  height?: string
  lines?: number
  rounded?: 'sm' | 'md' | 'lg' | 'full'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'text',
  lines: 1,
  rounded: 'md',
})

const roundedClass = computed(() => ({
  sm: 'rounded-sm', md: 'rounded-md', lg: 'rounded-lg', full: 'rounded-full',
}[props.rounded]))
</script>

<template>
  <div v-if="variant === 'text'" class="space-y-2" :style="{ width }">
    <div
      v-for="i in lines"
      :key="i"
      :class="['animate-pulse bg-gray-200', roundedClass]"
      :style="{ height: height || '14px', width: i === lines && lines > 1 ? '60%' : '100%' }"
    />
  </div>

  <div v-else-if="variant === 'card'" :class="['animate-pulse bg-gray-200 rounded-xl p-6', roundedClass]" :style="{ width: width || '100%', height: height || '200px' }">
    <div class="space-y-4">
      <div class="h-4 bg-gray-300 rounded w-3/4" />
      <div class="h-3 bg-gray-300 rounded w-1/2" />
      <div class="h-3 bg-gray-300 rounded w-full" />
      <div class="h-3 bg-gray-300 rounded w-5/6" />
    </div>
  </div>

  <div v-else-if="variant === 'table-row'" :class="['animate-pulse flex gap-4 py-3', roundedClass]">
    <div v-for="i in (lines || 5)" :key="i" class="h-4 bg-gray-200 rounded flex-1" />
  </div>

  <div v-else-if="variant === 'avatar'" :class="['animate-pulse bg-gray-200 rounded-full shrink-0', roundedClass]" :style="{ width: width || '40px', height: height || width || '40px' }" />

  <div v-else-if="variant === 'image'" :class="['animate-pulse bg-gray-200', roundedClass]" :style="{ width: width || '100%', height: height || '200px' }" />
</template>
