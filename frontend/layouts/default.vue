<template>
  <div class="min-h-screen flex flex-col bg-gray-50">
    <!-- Skip to main content -->
    <a href="#main-content" class="skip-link">Ir al contenido principal</a>

    <!-- Header Mejorado -->
    <header class="bg-gradient-to-r from-primary-700 via-primary-600 to-emerald-600 shadow-xl sticky top-0 z-50">
      <nav class="container mx-auto px-4 py-3">
        <div class="flex items-center justify-between">
          <!-- Logo -->
          <NuxtLink to="/" class="flex items-center gap-3 group">
            <div class="w-11 h-11 bg-white rounded-xl flex items-center justify-center shadow-lg group-hover:scale-105 transition-transform">
              <span class="text-2xl">🌴</span>
            </div>
            <div class="hidden md:block">
              <span class="text-xl font-bold text-white">Costa Rica Travel</span>
            </div>
          </NuxtLink>

          <!-- Desktop Nav -->
          <div class="hidden lg:flex items-center gap-1">
              <NuxtLink
                v-for="item in navItems"
                :key="item.path"
                :to="item.path"
                class="flex items-center gap-2 px-4 py-2 text-white/90 hover:text-white hover:bg-white/10 font-medium rounded-lg transition-all backdrop-blur-sm"
                :class="{ 'bg-white/20 text-white': $route.path.startsWith(item.path) }"
                :aria-current="$route.path.startsWith(item.path) ? 'page' : undefined"
              >
              <component :is="item.icon" class="w-4 h-4" />
              <span>{{ item.label }}</span>
            </NuxtLink>
          </div>

          <!-- Right Side -->
          <div class="flex items-center gap-2">
            <!-- Dark Mode Toggle -->
            <ClientOnly>
              <button
                @click="toggleColorMode"
                class="p-2.5 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-all backdrop-blur-sm"
                :aria-label="isDark ? 'Modo claro' : 'Modo oscuro'"
                :title="isDark ? 'Modo claro' : 'Modo oscuro'"
              >
                <Sun v-if="isDark" class="w-5 h-5" />
                <Moon v-else class="w-5 h-5" />
              </button>
              <template #fallback>
                <div class="p-2.5 bg-white/10 rounded-lg">
                  <div class="w-5 h-5"></div>
                </div>
              </template>
            </ClientOnly>

            <!-- Search Toggle -->
            <button
              @click="showSearch = !showSearch"
              class="p-2.5 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-all backdrop-blur-sm"
              aria-label="Buscar"
              title="Buscar"
            >
              <Search class="w-5 h-5" />
            </button>

            <!-- Language Dropdown -->
            <div class="relative" ref="langMenuRef">
              <button
                @click="langMenuOpen = !langMenuOpen"
                class="flex items-center gap-1 px-3 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-all backdrop-blur-sm"
                aria-label="Seleccionar idioma"
              >
                <Globe class="w-4 h-4" />
                <span class="text-sm font-medium uppercase">{{ locale }}</span>
                <ChevronDown class="w-4 h-4" />
              </button>
              <Transition name="dropdown">
                <div v-if="langMenuOpen" class="absolute right-0 mt-2 w-44 bg-white rounded-xl shadow-xl border border-gray-100 py-2 z-50">
                  <button
                    v-for="lang in languages"
                    :key="lang.code"
                    @click="changeLocale(lang.code)"
                    class="w-full px-4 py-2.5 text-left flex items-center gap-3 hover:bg-gray-50 transition-colors"
                    :class="locale === lang.code ? 'bg-primary-50 text-primary-700' : 'text-gray-700'"
                  >
                    <span class="text-lg">{{ lang.flag }}</span>
                    <span class="text-sm font-medium">{{ lang.name }}</span>
                  </button>
                </div>
              </Transition>
            </div>

            <!-- Auth -->
            <template v-if="isAuthenticated">
              <NuxtLink
                v-if="isVendor"
                to="/vendor/dashboard"
                class="hidden sm:flex items-center gap-2 px-4 py-2 bg-white text-primary-700 font-semibold rounded-lg hover:bg-gray-100 transition-all text-sm shadow"
              >
                <LayoutDashboard class="w-4 h-4" />
                Mi Panel
              </NuxtLink>
              <NuxtLink
                v-else
                to="/"
                class="hidden sm:flex items-center gap-2 px-4 py-2 bg-white text-primary-700 font-semibold rounded-lg hover:bg-gray-100 transition-all text-sm shadow"
              >
                <LayoutDashboard class="w-4 h-4" />
                Mi Cuenta
              </NuxtLink>
              <button
                @click="logout"
                class="p-2.5 bg-white/10 hover:bg-red-500 text-white rounded-lg transition-all"
                aria-label="Cerrar sesión"
              >
                <LogOut class="w-5 h-5" />
              </button>
            </template>
            <template v-else>
              <NuxtLink
                to="/login"
                class="hidden sm:flex items-center gap-2 px-4 py-2 text-white hover:bg-white/10 rounded-lg transition-all text-sm font-medium"
              >
                <LogIn class="w-4 h-4" />
                Entrar
              </NuxtLink>
              <NuxtLink
                to="/register"
                class="flex items-center gap-2 px-4 py-2 bg-white text-primary-700 font-bold rounded-lg hover:bg-gray-100 transition-all text-sm shadow"
              >
                <UserPlus class="w-4 h-4" />
                <span class="hidden sm:inline">Registrarse</span>
              </NuxtLink>
            </template>

            <!-- Mobile Menu -->
            <button
              @click="mobileMenuOpen = !mobileMenuOpen"
              class="lg:hidden p-2.5 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-all"
              :aria-label="mobileMenuOpen ? 'Cerrar menú' : 'Abrir menú'"
              :aria-expanded="mobileMenuOpen"
            >
              <Menu v-if="!mobileMenuOpen" class="w-5 h-5" />
              <X v-else class="w-5 h-5" />
            </button>
          </div>
        </div>

        <!-- Search Bar Expandida -->
        <Transition name="expand">
          <div v-if="showSearch" class="mt-4 pb-2">
            <div class="bg-white rounded-xl p-4 shadow-xl">
              <form @submit.prevent="handleSearch" class="flex flex-col sm:flex-row gap-3" role="search">
                <div class="flex-1 relative">
                  <Search class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    v-model="searchQuery"
                    type="text"
                    placeholder="¿Qué estás buscando?"
                    class="w-full pl-12 pr-4 py-3.5 border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:ring-0 outline-none transition-all text-gray-800 placeholder-gray-400 font-medium"
                  />
                </div>
                <button
                  type="submit"
                  class="px-8 py-3.5 bg-gradient-to-r from-primary-600 to-emerald-600 text-white font-bold rounded-xl hover:shadow-lg transition-all flex items-center justify-center gap-2"
                >
                  <Search class="w-5 h-5" />
                  <span>Buscar</span>
                </button>
              </form>
              <div class="flex flex-wrap gap-2 mt-3 items-center">
                <span class="text-xs text-gray-500 font-medium">Sugerencias:</span>
                <button
                  v-for="tag in popularSearches"
                  :key="tag"
                  @click="searchQuery = tag; handleSearch()"
                  class="text-xs px-3 py-1.5 bg-primary-50 hover:bg-primary-100 text-primary-700 rounded-full transition-colors font-medium border border-primary-200"
                >
                  {{ tag }}
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </nav>

      <!-- Mobile Menu -->
      <Transition name="slide-down">
        <div v-if="mobileMenuOpen" class="lg:hidden bg-primary-800 border-t border-white/10">
          <div class="container mx-auto px-4 py-4 space-y-1">
            <NuxtLink
              v-for="item in navItems"
              :key="item.path"
              :to="item.path"
              @click="mobileMenuOpen = false"
              class="flex items-center gap-3 px-4 py-3 text-white hover:bg-white/10 rounded-lg font-medium transition-colors"
              :class="{ 'bg-white/15': $route.path.startsWith(item.path) }"
            >
              <component :is="item.icon" class="w-5 h-5" />
              {{ item.label }}
            </NuxtLink>
            <div class="pt-4 border-t border-white/10 mt-4 space-y-2">
              <NuxtLink
                to="/login"
                @click="mobileMenuOpen = false"
                class="flex items-center gap-3 px-4 py-3 text-white hover:bg-white/10 rounded-lg font-medium"
              >
                <LogIn class="w-5 h-5" />
                Entrar
              </NuxtLink>
              <NuxtLink
                to="/register"
                @click="mobileMenuOpen = false"
                class="flex items-center justify-center gap-2 px-4 py-3 bg-white text-primary-700 rounded-lg font-bold"
              >
                <UserPlus class="w-5 h-5" />
                Registrarse
              </NuxtLink>
            </div>
          </div>
        </div>
      </Transition>
    </header>

    <!-- Main Content -->
    <main id="main-content" class="flex-1">
      <slot />
    </main>

    <!-- Footer -->
    <FooterV2 />

    <!-- Toast Notifications -->
    <UiToast />
  </div>
</template>

<script setup lang="ts">
import {
  Search,
  MapPin,
  Building2,
  Compass,
  FileText,
  Globe,
  ChevronDown,
  LogIn,
  LogOut,
  UserPlus,
  LayoutDashboard,
  Menu,
  X,
  Palmtree,
  Sun,
  Moon
} from 'lucide-vue-next'

const { locale } = useI18n()
const auth = useAuthStore()
const router = useRouter()

const mobileMenuOpen = ref(false)
const showSearch = ref(false)
const searchQuery = ref('')
const langMenuOpen = ref(false)

const colorMode = useColorMode()
const isDark = computed(() => colorMode.value === 'dark')

const toggleColorMode = () => {
  colorMode.preference = isDark.value ? 'light' : 'dark'
}

const isAuthenticated = computed(() => auth.isAuthenticated)
const isVendor = computed(() => auth.isVendor)

const navItems = [
  { path: '/destinos', label: 'Destinos', icon: MapPin },
  { path: '/hoteles', label: 'Hoteles', icon: Building2 },
  { path: '/tours', label: 'Tours', icon: Compass },
  { path: '/blog', label: 'Blog', icon: FileText },
  { path: '/planificador', label: 'Planificador', icon: Palmtree },
]

const languages = [
  { code: 'es', name: 'Español', flag: '🇪🇸' },
  { code: 'en', name: 'English', flag: '🇺🇸' },
  { code: 'fr', name: 'Français', flag: '🇫🇷' },
]

const popularSearches = ['Playa del Carmen', 'Volcán Arenal', 'Monteverde', 'Manuel Antonio']

const logout = () => {
  auth.logout()
  router.push('/')
  mobileMenuOpen.value = false
}

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push(`/search?q=${encodeURIComponent(searchQuery.value)}`)
    showSearch.value = false
  }
}

const changeLocale = (code: string) => {
  locale.value = code
  langMenuOpen.value = false
}

const langMenuRef = ref<HTMLElement | null>(null)

const closeLangMenu = (event: MouseEvent) => {
  if (langMenuRef.value && !langMenuRef.value.contains(event.target as Node)) {
    langMenuOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', closeLangMenu)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', closeLangMenu)
})
</script>

<style scoped>
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px) scale(0.95);
}

.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}
.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
  margin-top: 0;
}
.expand-enter-to,
.expand-leave-from {
  opacity: 1;
  max-height: 200px;
}

.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}
.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>
