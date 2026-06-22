<template>
  <div class="bg-white" :class="classes">
    <slot />
  </div>
</template>

<script setup lang="ts">
const props = withDefaults(defineProps<{
  padding?: 'none' | 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  rounded?: 'lg' | 'xl' | '2xl'
  shadow?: 'none' | 'sm' | 'md'
  bordered?: boolean
  hover?: boolean
  overflowHidden?: boolean
}>(), {
  padding: 'md',
  rounded: 'xl',
  shadow: 'sm',
  bordered: true,
  hover: false,
  overflowHidden: false,
})

const paddingMap: Record<string, string> = { none: '', xs: 'p-4', sm: 'p-5', md: 'p-6', lg: 'p-8', xl: 'p-12' }

const classes = computed(() => [
  `rounded-${props.rounded}`,
  props.shadow !== 'none' ? `shadow-${props.shadow}` : '',
  props.bordered ? 'border border-gray-100' : '',
  paddingMap[props.padding],
  props.hover ? 'hover:shadow-md transition-shadow' : '',
  props.overflowHidden ? 'overflow-hidden' : '',
].filter(Boolean).join(' '))
</script>
