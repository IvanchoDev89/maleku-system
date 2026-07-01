<script setup lang="ts">
import { Inbox } from 'lucide-vue-next'
import type { Component } from 'vue'

interface Props {
  icon?: Component
  title?: string
  description?: string
  actionLabel?: string
  actionTo?: string
  compact?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  icon: Inbox,
  compact: false,
})
</script>

<template>
  <div :class="['flex flex-col items-center justify-center text-center', compact ? 'py-8' : 'py-16']">
    <component :is="icon" class="w-12 h-12 text-gray-300 mb-4" />
    <h3 v-if="title" class="text-lg font-semibold text-gray-900 mb-1">{{ title }}</h3>
    <p v-if="description" class="text-sm text-gray-500 max-w-sm mb-6">{{ description }}</p>
    <NuxtLink
      v-if="actionLabel && actionTo"
      :to="actionTo"
      class="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium"
    >
      {{ actionLabel }}
    </NuxtLink>
    <slot />
  </div>
</template>
