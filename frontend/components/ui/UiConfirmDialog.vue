<script setup lang="ts">
interface Props {
  modelValue: boolean
  title?: string
  message: string
  confirmText?: string
  cancelText?: string
  variant?: 'danger' | 'warning' | 'info'
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Confirmar',
  confirmText: 'Confirmar',
  cancelText: 'Cancelar',
  variant: 'danger',
  loading: false
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'confirm': []
}>()

function onConfirm() {
  emit('confirm')
}

function onCancel() {
  emit('update:modelValue', false)
}
</script>

<template>
  <UiModal
    :model-value="modelValue"
    :title="title"
    max-width="max-w-sm"
    :closeable="!loading"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <p class="text-gray-600">{{ message }}</p>
    <template #footer>
      <UiButton variant="outline" :disabled="loading" @click="onCancel">{{ cancelText }}</UiButton>
      <UiButton
        :variant="variant === 'danger' ? 'primary' : 'secondary'"
        :loading="loading"
        @click="onConfirm"
      >{{ confirmText }}</UiButton>
    </template>
  </UiModal>
</template>
