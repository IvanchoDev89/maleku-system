<script setup lang="ts">
interface Props {
  modelValue: string
  label?: string
  placeholder?: string
  required?: boolean
  disabled?: boolean
  rows?: number
  maxLength?: number
  error?: string
}

const props = withDefaults(defineProps<Props>(), {
  required: false,
  disabled: false,
  rows: 4
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

function onInput(event: Event) {
  const target = event.target as HTMLTextAreaElement
  emit('update:modelValue', target.value)
}
</script>

<template>
  <div class="space-y-1">
    <label v-if="label" class="block text-sm font-medium text-gray-700">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>
    <textarea
      :value="modelValue"
      :placeholder="placeholder"
      :required="required"
      :disabled="disabled"
      :rows="rows"
      :maxlength="maxLength"
      :class="['w-full px-4 py-2.5 border rounded-xl text-gray-900 placeholder-gray-400 focus:ring-2 focus:ring-teal-500 focus:border-teal-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors resize-y', error ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-300']"
      @input="onInput"
    />
    <div v-if="maxLength" class="text-xs text-gray-400 text-right">{{ (modelValue || '').length }} / {{ maxLength }}</div>
    <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
  </div>
</template>
