<template>
  <div class="min-h-screen flex flex-col bg-gray-50">
    <PublicHeader />
    <main id="main-content" class="flex-1">
      <slot />
    </main>
    <FooterV2 />
  </div>
</template>
