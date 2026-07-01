<script setup lang="ts">
interface Props {
  modelValue: boolean
  label?: string
  description?: string
  required?: boolean
  disabled?: boolean
  error?: string
  indeterminate?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  required: false,
  disabled: false,
  indeterminate: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const inputRef = ref<HTMLInputElement | null>(null)

watch(() => props.indeterminate, (val) => {
  if (inputRef.value) inputRef.value.indeterminate = val
}, { immediate: true })

function onChange(event: Event) {
  if (!props.disabled) {
    emit('update:modelValue', (event.target as HTMLInputElement).checked)
  }
}

const checkboxId = computed(() => {
  if (!props.label) return undefined
  return props.label.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '')
})
</script>

<template>
  <div class="flex items-start gap-3">
    <div class="flex items-center h-5">
      <input
        :id="checkboxId"
        ref="inputRef"
        type="checkbox"
        :checked="modelValue"
        :disabled="disabled"
        :required="required"
        :aria-invalid="!!error"
        :aria-describedby="error ? `${checkboxId}-error` : undefined"
        class="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
        @change="onChange"
      />
    </div>
    <div class="text-sm leading-5">
      <label v-if="label" :for="checkboxId" class="font-medium text-gray-700 cursor-pointer">
        {{ label }}
        <span v-if="required" class="text-red-500">*</span>
      </label>
      <p v-if="description" class="text-gray-400">{{ description }}</p>
      <p v-if="error" :id="`${checkboxId}-error`" class="text-red-600">{{ error }}</p>
    </div>
  </div>
</template>
