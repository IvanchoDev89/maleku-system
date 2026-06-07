export function useReducedMotion() {
  const prefersReduced = ref(false)

  if (import.meta.client) {
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)')
    prefersReduced.value = mq.matches
    mq.addEventListener('change', (e) => {
      prefersReduced.value = e.matches
    })
  }

  return {
    prefersReduced: readonly(prefersReduced),
    noAnimationsClass: computed(() => prefersReduced.value ? 'reduce-motion' : '')
  }
}
