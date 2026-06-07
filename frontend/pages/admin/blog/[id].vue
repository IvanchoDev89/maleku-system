<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <NuxtLink to="/admin/blog" class="text-gray-500 hover:text-gray-700 flex items-center gap-2 font-medium">
        ← Volver al Blog
      </NuxtLink>
    </div>

    <BlogEditorForm :post-id="route.params.id as string" />
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'admin',
  middleware: ['auth'],
})

const route = useRoute()
</script>
