<script setup lang="ts">
interface Props {
  variant?: 'card' | 'text' | 'image' | 'avatar' | 'button'
  count?: number
  wrapperClass?: string
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'text',
  count: 1,
  wrapperClass: ''
})

const getHeightClass = () => {
  switch (props.variant) {
    case 'card': return 'h-52'
    case 'image': return 'h-48'
    case 'avatar': return 'h-12 w-12'
    case 'button': return 'h-10'
    default: return 'h-4'
  }
}

const getWidthClass = () => {
  switch (props.variant) {
    case 'card': return 'w-full'
    case 'avatar': return 'w-12'
    case 'button': return 'w-24'
    default: return 'w-full'
  }
}
</script>

<template>
  <div :class="['animate-pulse', wrapperClass]">
    <div
      v-for="i in count"
      :key="i"
      class="bg-gray-200 rounded"
      :class="[getHeightClass(), variant === 'card' ? '' : getWidthClass()]"
    ></div>
  </div>
</template>