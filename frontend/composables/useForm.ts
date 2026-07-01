interface UseFormOptions<T extends Record<string, any>> {
  initial: T
  validate?: (values: T) => Partial<Record<keyof T, string>>
  onSave?: (values: T) => Promise<void> | void
}

export function useForm<T extends Record<string, any>>(options: UseFormOptions<T>) {
  const original = ref(cloneDeep(options.initial))
  const values = ref(cloneDeep(options.initial))
  const errors = ref<Partial<Record<keyof T, string>>>({})
  const submitted = ref(false)
  const saving = ref(false)
  const saveError = ref('')

  const isDirty = computed(() => {
    return Object.keys(values.value).some(key => {
      const a = values.value[key]
      const b = original.value[key]
      if (Array.isArray(a) && Array.isArray(b)) {
        return JSON.stringify(a) !== JSON.stringify(b)
      }
      return a !== b
    })
  })

  const isValid = computed(() => {
    if (!options.validate) return true
    const errs = options.validate(values.value)
    return Object.keys(errs).length === 0
  })

  function validate(): boolean {
    if (!options.validate) return true
    errors.value = options.validate(values.value) as any
    return Object.keys(errors.value).length === 0
  }

  async function save() {
    if (saving.value) return
    submitted.value = true
    if (!validate()) return
    saving.value = true
    saveError.value = ''
    try {
      if (options.onSave) await options.onSave(values.value)
      original.value = cloneDeep(values.value)
    } catch (e: any) {
      saveError.value = e?.data?.detail || e?.message || 'Error al guardar'
      throw e
    } finally {
      saving.value = false
    }
  }

  function reset() {
    values.value = cloneDeep(original.value)
    errors.value = {}
    submitted.value = false
    saveError.value = ''
  }

  function setField<K extends keyof T>(key: K, value: T[K]) {
    values.value[key] = value
    if (submitted.value && options.validate) {
      const fieldErrors = options.validate(values.value)
      if (fieldErrors[key]) {
        errors.value[key] = fieldErrors[key] as any
      } else {
        delete errors.value[key]
      }
    }
  }

  function fieldError(key: keyof T): string | undefined {
    return errors.value[key]
  }

  function setOriginal(v: T) {
    original.value = cloneDeep(v)
    values.value = cloneDeep(v)
  }

  const unsavedWarning = computed(() => isDirty.value)

  function confirmLeave(): boolean {
    if (isDirty.value) {
      return window.confirm('Tienes cambios sin guardar. ¿Seguro que quieres salir?')
    }
    return true
  }

  onBeforeRouteLeave((to, from, next) => {
    if (isDirty.value) {
      const answer = window.confirm('Tienes cambios sin guardar. ¿Seguro que quieres salir?')
      if (answer) next()
      else next(false)
    } else {
      next()
    }
  })

  if (import.meta.client) {
    const handler = (e: BeforeUnloadEvent) => {
      if (isDirty.value) {
        e.preventDefault()
        e.returnValue = ''
      }
    }
    onMounted(() => window.addEventListener('beforeunload', handler))
    onUnmounted(() => window.removeEventListener('beforeunload', handler))
  }

  return {
    values: readonly(values),
    original: readonly(original),
    errors: readonly(errors),
    saving: readonly(saving),
    saveError: readonly(saveError),
    isDirty: readonly(isDirty),
    isValid: readonly(isValid),
    submitted: readonly(submitted),
    unsavedWarning: readonly(unsavedWarning),
    save,
    reset,
    setField,
    fieldError,
    setOriginal,
    validate,
    confirmLeave,
  }
}

function cloneDeep<T>(obj: T): T {
  return JSON.parse(JSON.stringify(obj))
}
