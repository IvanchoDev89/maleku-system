<template>
  <div></div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

onMounted(() => {
  navigateTo('/superadmin/dashboard')
})
</script>
