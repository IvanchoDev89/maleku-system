<template>
  <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 space-y-6">
    <div>
      <label class="block text-gray-500 text-sm mb-2 font-medium">Título del Artículo</label>
      <input
        v-model="form.title"
        type="text"
        class="w-full text-3xl font-bold bg-transparent text-gray-900 border-b-2 border-gray-200 focus:border-primary pb-3 focus:outline-none transition-colors"
        placeholder="Título de tu artículo..."
      />
    </div>

    <div>
      <label class="block text-gray-500 text-sm mb-2 font-medium">Imagen Destacada</label>
      <div class="border-2 border-dashed border-gray-200 rounded-xl p-6 text-center hover:border-primary/50 transition-colors">
        <div v-if="form.featured_image" class="relative inline-block">
          <NuxtImg :src="form.featured_image" class="max-h-56 rounded-xl shadow-md" width="600" height="200" format="webp" />
          <button @click="form.featured_image = ''" type="button" class="absolute top-2 right-2 bg-red-500 text-white rounded-full p-2 hover:bg-red-600 transition-colors">✕</button>
        </div>
        <div v-else>
          <p class="text-gray-400 mb-3">Arrastra una imagen o pega una URL</p>
          <input v-model="form.featured_image" type="text" placeholder="https://..." class="w-full max-w-md bg-gray-50 text-gray-700 px-4 py-2.5 rounded-lg border border-gray-200 text-sm" />
        </div>
      </div>
    </div>

    <div>
      <label class="block text-gray-500 text-sm mb-2 font-medium">Extracto (Resumen)</label>
      <textarea v-model="form.excerpt" rows="2" class="w-full bg-gray-50 text-gray-700 px-4 py-3 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20" placeholder="Breve descripción para tarjetas y SEO..." />
    </div>

    <div>
      <label class="block text-gray-500 text-sm mb-2 font-medium">Contenido</label>
      <div class="border border-gray-200 rounded-xl overflow-hidden shadow-sm">
        <div class="bg-gray-50 px-4 py-3 flex gap-2 flex-wrap border-b border-gray-200">
          <button @click="insertFormat('**', '**')" type="button" class="px-3 py-1.5 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded-lg font-bold text-sm transition-colors" title="Negrita">B</button>
          <button @click="insertFormat('*', '*')" type="button" class="px-3 py-1.5 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded-lg text-sm italic transition-colors" title="Cursiva">I</button>
          <button @click="insertFormat('# ', '')" type="button" class="px-3 py-1.5 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded-lg text-sm font-bold transition-colors" title="Encabezado">H1</button>
          <button @click="insertFormat('## ', '')" type="button" class="px-3 py-1.5 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded-lg text-sm font-bold transition-colors" title="Subtítulo">H2</button>
          <button @click="insertFormat('- ', '')" type="button" class="px-3 py-1.5 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded-lg text-sm transition-colors" title="Lista">•</button>
          <button @click="insertFormat('1. ', '')" type="button" class="px-3 py-1.5 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded-lg text-sm transition-colors" title="Numeración">1.</button>
          <button @click="insertFormat('[', '](url)')" type="button" class="px-3 py-1.5 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded-lg text-sm transition-colors" title="Enlace">🔗</button>
          <button @click="insertFormat('![alt](', ')')" type="button" class="px-3 py-1.5 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded-lg text-sm transition-colors" title="Imagen">🖼️</button>
          <button @click="insertFormat('> ', '')" type="button" class="px-3 py-1.5 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded-lg text-sm transition-colors" title="Cita">"</button>
          <button @click="insertFormat('`', '`')" type="button" class="px-3 py-1.5 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded-lg text-sm font-mono transition-colors" title="Código">&lt;/&gt;</button>
        </div>
        <textarea v-model="form.content" rows="20" class="w-full bg-white text-gray-700 px-5 py-4 focus:outline-none font-mono text-sm leading-relaxed" placeholder="Escribe tu artículo en Markdown..." />
      </div>
      <p class="text-gray-400 text-xs mt-2">Usa Markdown para dar formato al texto</p>
    </div>

    <div class="bg-gray-50 rounded-xl p-5">
      <h3 class="text-gray-800 font-bold text-lg mb-4">🔍 SEO</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-gray-500 text-sm mb-1.5 font-medium">Slug (URL)</label>
          <input v-model="form.slug" type="text" class="w-full bg-white text-gray-700 px-4 py-2.5 rounded-lg border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20" placeholder="mi-articulo" />
        </div>
        <div>
          <label class="block text-gray-500 text-sm mb-1.5 font-medium">Palabras clave</label>
          <input v-model="form.seo_keywords" type="text" class="w-full bg-white text-gray-700 px-4 py-2.5 rounded-lg border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20" placeholder="palabra1, palabra2, palabra3" />
        </div>
        <div class="md:col-span-2">
          <label class="block text-gray-500 text-sm mb-1.5 font-medium">Meta descripción</label>
          <textarea v-model="form.seo_description" rows="2" class="w-full bg-white text-gray-700 px-4 py-2.5 rounded-lg border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20" placeholder="Descripción para motores de búsqueda (150-160 caracteres)" maxlength="160" />
          <p class="text-gray-400 text-xs mt-1.5">{{ form.seo_description?.length || 0 }}/160</p>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <label class="block text-gray-500 text-sm mb-1.5 font-medium">Categoría</label>
        <UiSelect v-model="form.category" :options="categoryOptions" placeholder="Seleccionar..." />
      </div>
      <div>
        <label class="block text-gray-500 text-sm mb-1.5 font-medium">Etiquetas (separadas por coma)</label>
        <input v-model="tagsInput" type="text" class="w-full bg-gray-50 text-gray-700 px-4 py-2.5 rounded-lg border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20" placeholder="costa rica, playa, aventura" />
      </div>
    </div>

    <div class="flex items-center gap-3">
      <input v-model="schedulePost" type="checkbox" id="schedule" class="w-5 h-5 text-primary rounded focus:ring-primary" />
      <label for="schedule" class="text-gray-700 font-medium">Programar publicación</label>
      <input v-if="schedulePost" v-model="form.scheduled_at" type="datetime-local" class="bg-gray-50 text-gray-700 px-4 py-2.5 rounded-lg border border-gray-200 ml-4" />
    </div>

    <div class="flex justify-end gap-3 pt-4 border-t border-gray-100">
      <slot name="actions">
        <NuxtLink to="/admin/blog" class="px-6 py-2.5 border border-gray-300 rounded-xl text-gray-700 font-medium hover:bg-gray-50 transition-colors">
          Cancelar
        </NuxtLink>
        <button @click="saveDraft" class="px-5 py-2.5 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 font-medium transition-colors">
          💾 Guardar Borrador
        </button>
        <button @click="publishPost" :disabled="saving" class="px-5 py-2.5 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 transition-colors disabled:opacity-50">
          {{ saving ? 'Publicando...' : '🚀 Publicar' }}
        </button>
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'

const props = defineProps<{ postId?: string }>()

const { form, tagsInput, schedulePost, categoryOptions, insertFormat, saveDraft, publishPost, loadPost, saving } = useBlogEditor(props.postId)

onMounted(() => {
  if (props.postId) loadPost()
})
</script>
