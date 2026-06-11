<script setup lang="ts">
interface Props {
  items: { label: string; to?: string }[]
}

const props = defineProps<Props>()
</script>

<template>
  <nav class="mb-4" aria-label="Breadcrumb">
    <ol class="flex items-center gap-1.5 text-sm text-gray-500">
      <li v-if="items.length" class="flex items-center gap-1.5">
        <NuxtLink to="/" class="hover:text-primary-600 transition-colors">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
        </NuxtLink>
      </li>
      <template v-for="(item, idx) in items" :key="idx">
        <li class="flex items-center gap-1.5">
          <svg class="w-3.5 h-3.5 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
          <NuxtLink
            v-if="item.to && idx < items.length - 1"
            :to="item.to"
            class="hover:text-primary-600 transition-colors"
          >{{ item.label }}</NuxtLink>
          <span v-else class="text-gray-900 font-medium" aria-current="page">{{ item.label }}</span>
        </li>
      </template>
    </ol>
  </nav>
</template>
