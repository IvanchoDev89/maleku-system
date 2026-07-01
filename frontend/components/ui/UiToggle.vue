<script setup lang="ts">
interface Props {
  modelValue: boolean
  label?: string
  description?: string
  disabled?: boolean
  size?: 'sm' | 'md'
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  size: 'md',
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

function toggle() {
  if (!props.disabled) {
    emit('update:modelValue', !props.modelValue)
  }
}

const toggleId = computed(() => {
  if (!props.label) return undefined
  return props.label.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '')
})

const sizeClasses = computed(() => ({
  sm: { track: 'w-8 h-4', thumb: 'w-3 h-3', translateOn: 'translate-x-4' },
  md: { track: 'w-11 h-6', thumb: 'w-5 h-5', translateOn: 'translate-x-5' },
}[props.size]))
</script>

<template>
  <div class="flex items-center gap-3">
    <button
      :id="toggleId"
      type="button"
      role="switch"
      :aria-checked="modelValue"
      :disabled="disabled"
      :class="[
        'relative inline-flex items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
        modelValue ? 'bg-primary-600' : 'bg-gray-300',
        disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer',
        sizeClasses.track,
      ]"
      @click="toggle"
    >
      <span
        :class="[
          'inline-block rounded-full bg-white shadow transform transition-transform',
          modelValue ? sizeClasses.translateOn : 'translate-x-0.5',
          sizeClasses.thumb,
        ]"
      />
    </button>
    <div v-if="label" class="text-sm leading-5">
      <label :for="toggleId" class="font-medium text-gray-700 cursor-pointer" @click="toggle">{{ label }}</label>
      <p v-if="description" class="text-gray-400">{{ description }}</p>
    </div>
  </div>
</template>
