import { ref, onMounted, onUnmounted } from 'vue'

export const useScrollProgress = () => {
  const scrollProgress = ref(0)

  const updateProgress = () => {
    const scrollTop = window.scrollY
    const docHeight = document.documentElement.scrollHeight - window.innerHeight
    scrollProgress.value = docHeight > 0 ? Math.min((scrollTop / docHeight) * 100, 100) : 0
  }

  onMounted(() => {
    window.addEventListener('scroll', updateProgress, { passive: true })
    updateProgress()
  })

  onUnmounted(() => {
    window.removeEventListener('scroll', updateProgress)
  })

  return { scrollProgress }
}
