interface BlogForm {
  title: string
  slug: string
  excerpt: string
  content: string
  featured_image: string
  category: string
  seo_keywords: string
  seo_description: string
  scheduled_at: string
  status: string
}

export const useBlogEditor = (postId?: string) => {
  const api = useApi()
  const router = useRouter()
  const toast = useToast()

  const isEditing = computed(() => !!postId)
  const saving = ref(false)
  const tagsInput = ref('')
  const schedulePost = ref(false)

  const form = reactive<BlogForm>({
    title: '',
    slug: '',
    excerpt: '',
    content: '',
    featured_image: '',
    category: '',
    seo_keywords: '',
    seo_description: '',
    scheduled_at: '',
    status: 'draft'
  })

  const categoryOptions = ref([
    { value: 'destinos', label: 'Destinos' },
    { value: 'tours', label: 'Tours' },
    { value: 'hoteles', label: 'Hoteles' },
    { value: 'aventura', label: 'Aventura' },
    { value: 'cultura', label: 'Cultura' },
    { value: 'naturaleza', label: 'Naturaleza' },
    { value: 'consejos', label: 'Consejos de Viaje' },
  ])

  onMounted(async () => {
    try {
      const categories = await api.get<any[]>('/blog/categories')
      if (categories?.length) {
        categoryOptions.value = categories.map((c: any) => ({
          value: c.value || c.slug || c,
          label: c.label || c.name || c,
        }))
      }
    } catch {
      // keep defaults
    }
  })

  const insertFormat = (before: string, after: string) => {
    const textarea = document.querySelector('textarea') as HTMLTextAreaElement
    if (!textarea) return
    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    const text = form.content
    const selected = text.substring(start, end)
    form.content = text.substring(0, start) + before + selected + after + text.substring(end)
  }

  const buildPayload = () => ({
    ...form,
    tags: tagsInput.value.split(',').map((t: string) => t.trim()).filter(Boolean),
    scheduled_at: schedulePost.value ? form.scheduled_at : null
  })

  const loadPost = async () => {
    if (!postId) return
    try {
      const post = await api.get(`/blog/${postId}`)
      form.title = post.title
      form.slug = post.slug
      form.excerpt = post.excerpt || ''
      form.content = post.content || ''
      form.featured_image = post.featured_image || ''
      form.category = post.category || ''
      form.seo_keywords = post.seo_keywords || ''
      form.seo_description = post.seo_description || ''
      form.status = post.status
      tagsInput.value = post.tags?.join(', ') || ''
      if (post.scheduled_at) {
        schedulePost.value = true
        form.scheduled_at = post.scheduled_at.slice(0, 16)
      }
    } catch (error) {
      console.error('Error loading post:', error)
      useToast().add('Error loading post', 'error')
    }
  }

  const saveDraft = async () => {
    saving.value = true
    try {
      const data = { ...buildPayload(), status: 'draft' }
      if (postId) {
        await api.put(`/blog/${postId}`, data)
      } else {
        await api.post('/blog', data)
      }
      toast.success('Borrador guardado')
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Error al guardar')
    } finally {
      saving.value = false
    }
  }

  const publishPost = async () => {
    if (!form.title || !form.content) {
      toast.warning('Título y contenido son obligatorios')
      return
    }
    saving.value = true
    try {
      const data = { ...buildPayload(), status: schedulePost.value ? 'scheduled' : 'published' }
      if (postId) {
        await api.put(`/blog/${postId}`, data)
      } else {
        await api.post('/blog', data)
      }
      router.push('/admin/blog')
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Error al publicar')
    } finally {
      saving.value = false
    }
  }

  return { form, tagsInput, schedulePost, categoryOptions, insertFormat, saveDraft, publishPost, loadPost, saving, isEditing }
}
