<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const route = useRoute()
const sidebarOpen = ref(true)
const sidebarCollapsed = ref(false)
const currentTime = ref(new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }))
const mounted = ref(false)

onMounted(() => {
  mounted.value = true
})

setInterval(() => {
  currentTime.value = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
}, 1000)

const navigation = [
  { name: 'Dashboard', path: '/', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
  { name: 'Queue', path: '/queue', icon: 'M4 6h16M4 10h16M4 14h16M4 18h16' },
  { name: 'Review', path: '/review', icon: 'M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z' },
  { name: 'Library', path: '/library', icon: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10' },
  { name: 'Studio', path: '/studio', icon: 'M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z' },
  { name: 'Analytics', path: '/analytics', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' },
  { name: 'Settings', path: '/settings', icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z' },
]

function isActive(path: string) {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

const currentPage = computed(() => {
  const item = navigation.find(n => isActive(n.path))
  return item?.name || 'Dashboard'
})
</script>

<template>
  <div class="flex min-h-screen bg-studio-void">
    <!-- Noise texture overlay for premium feel -->
    <div class="noise-overlay"></div>

    <!-- Sidebar -->
    <aside
      :class="[
        'fixed lg:static inset-y-0 left-0 z-50',
        'flex flex-col',
        'transform transition-all duration-500 ease-smooth',
        sidebarCollapsed ? 'w-20' : 'w-72',
        sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
      ]"
    >
      <!-- Sidebar background with gradient -->
      <div class="absolute inset-0 bg-gradient-to-b from-studio-black via-studio-abyss to-studio-void"></div>

      <!-- Ambient glow -->
      <div class="absolute top-0 left-0 right-0 h-40 bg-gradient-to-b from-studio-rose-500/5 to-transparent pointer-events-none"></div>
      <div class="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-studio-violet-500/5 to-transparent pointer-events-none"></div>

      <!-- Content -->
      <div class="relative flex flex-col h-full">
        <!-- Logo Section -->
        <div class="relative p-6 border-b border-studio-graphite/30">
          <RouterLink
            to="/"
            class="flex items-center gap-4 group"
            :class="{ 'justify-center': sidebarCollapsed }"
          >
            <!-- Vinyl disc logo with enhanced animation -->
            <div class="relative flex-shrink-0">
              <div
                class="w-12 h-12 vinyl-disc animate-spin-slower group-hover:animate-spin-slow transition-all pause-on-hover"
              >
                <div class="vinyl-label w-4 h-4"></div>
              </div>
              <!-- Glow ring on hover -->
              <div class="absolute -inset-1 rounded-full bg-studio-rose-500/0 group-hover:bg-studio-rose-500/20 blur-md transition-all duration-500"></div>
            </div>

            <!-- Brand text -->
            <div v-if="!sidebarCollapsed" class="overflow-hidden">
              <h1 class="font-display text-2xl font-semibold italic tracking-tight text-studio-cream">
                Songflow
              </h1>
              <p class="text-2xs font-condensed text-studio-stone uppercase tracking-[0.25em] mt-0.5">
                Studio Control
              </p>
            </div>
          </RouterLink>

          <!-- Decorative line -->
          <div class="absolute bottom-0 left-6 right-6 h-px bg-gradient-to-r from-transparent via-studio-rose-500/20 to-transparent"></div>
        </div>

        <!-- System Status Indicator -->
        <div
          class="px-6 py-4 border-b border-studio-graphite/20"
          :class="{ 'px-4': sidebarCollapsed }"
        >
          <div
            class="flex items-center gap-3"
            :class="{ 'justify-center': sidebarCollapsed }"
          >
            <div class="led-indicator rose pulsing"></div>
            <span v-if="!sidebarCollapsed" class="text-xs font-mono text-studio-stone uppercase tracking-wider">
              System Active
            </span>
          </div>

          <!-- VU Meter visualization -->
          <div v-if="!sidebarCollapsed" class="mt-3 vu-meter-segmented">
            <div
              v-for="i in 10"
              :key="i"
              class="vu-meter-segment"
              :class="[
                i <= 4 ? 'active green' : i <= 7 ? 'active yellow' : i <= 8 ? 'active red' : '',
                { 'animate-led-pulse': i <= 6 }
              ]"
              :style="{ animationDelay: `${i * 0.05}s` }"
            ></div>
          </div>
        </div>

        <!-- Navigation -->
        <nav class="flex-1 p-3 space-y-1 overflow-y-auto">
          <RouterLink
            v-for="(item, index) in navigation"
            :key="item.path"
            :to="item.path"
            :class="[
              'nav-link group',
              isActive(item.path) && 'active',
              sidebarCollapsed && 'justify-center px-3'
            ]"
            :style="{
              opacity: mounted ? 1 : 0,
              transform: mounted ? 'translateX(0)' : 'translateX(-20px)',
              transition: `all 0.4s ease-out ${index * 0.05}s`
            }"
          >
            <svg
              class="nav-icon flex-shrink-0"
              :class="{ 'w-6 h-6': sidebarCollapsed }"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" :d="item.icon" />
            </svg>
            <span v-if="!sidebarCollapsed" class="font-medium truncate">{{ item.name }}</span>

            <!-- Active indicator dot -->
            <div
              v-if="isActive(item.path) && !sidebarCollapsed"
              class="ml-auto w-1.5 h-1.5 rounded-full bg-studio-rose-500"
              style="box-shadow: 0 0 8px rgba(204, 122, 90, 0.6);"
            ></div>
          </RouterLink>
        </nav>

        <!-- Collapse toggle (desktop) -->
        <button
          @click="sidebarCollapsed = !sidebarCollapsed"
          class="hidden lg:flex items-center justify-center mx-3 mb-3 p-2 rounded-lg text-studio-stone hover:text-studio-cream hover:bg-studio-graphite/30 transition-all"
        >
          <svg
            class="w-5 h-5 transition-transform duration-300"
            :class="{ 'rotate-180': sidebarCollapsed }"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
          </svg>
        </button>

        <!-- User Section -->
        <div
          class="p-4 border-t border-studio-graphite/30"
          :class="{ 'p-3': sidebarCollapsed }"
        >
          <div
            class="flex items-center gap-3"
            :class="{ 'flex-col': sidebarCollapsed }"
          >
            <!-- Avatar -->
            <div class="relative group">
              <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-studio-graphite to-studio-charcoal flex items-center justify-center border border-studio-graphite/50 group-hover:border-studio-rose-500/30 transition-all">
                <svg class="w-5 h-5 text-studio-rose-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <!-- Online indicator -->
              <div class="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full bg-studio-success border-2 border-studio-abyss"></div>
            </div>

            <!-- User info -->
            <div v-if="!sidebarCollapsed" class="flex-1 min-w-0">
              <div class="text-sm font-medium text-studio-cream truncate">
                {{ authStore.user?.username || 'Admin' }}
              </div>
              <div class="text-xs text-studio-stone font-mono">{{ currentTime }}</div>
            </div>

            <!-- Logout button -->
            <button
              @click="authStore.logout()"
              class="p-2.5 rounded-xl text-studio-stone hover:text-studio-error hover:bg-studio-error-dim/30 transition-all group"
              title="Logout"
            >
              <svg class="w-5 h-5 group-hover:translate-x-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </aside>

    <!-- Mobile sidebar toggle -->
    <button
      @click="sidebarOpen = !sidebarOpen"
      class="lg:hidden fixed top-4 left-4 z-50 p-3 rounded-xl transition-all shadow-card"
      :class="sidebarOpen
        ? 'bg-studio-charcoal text-studio-cream'
        : 'bg-studio-black/90 backdrop-blur-sm border border-studio-graphite/50 text-studio-rose-400'"
    >
      <svg v-if="!sidebarOpen" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 6h16M4 12h16M4 18h16" />
      </svg>
      <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>

    <!-- Main content -->
    <main class="flex-1 min-h-screen lg:ml-0 relative">
      <!-- Decorative background meshes -->
      <div class="absolute inset-0 pointer-events-none overflow-hidden">
        <div
          class="absolute -top-40 -right-40 w-[600px] h-[600px] rounded-full opacity-30"
          style="background: radial-gradient(circle, rgba(204, 122, 90, 0.08) 0%, transparent 60%);"
        ></div>
        <div
          class="absolute top-1/2 -left-20 w-[400px] h-[400px] rounded-full opacity-20"
          style="background: radial-gradient(circle, rgba(139, 92, 246, 0.06) 0%, transparent 60%);"
        ></div>
        <div
          class="absolute -bottom-20 right-1/4 w-[300px] h-[300px] rounded-full opacity-25"
          style="background: radial-gradient(circle, rgba(201, 162, 39, 0.05) 0%, transparent 60%);"
        ></div>
      </div>

      <!-- Top bar for mobile -->
      <div class="lg:hidden sticky top-0 z-40 px-4 py-3 bg-studio-void/80 backdrop-blur-md border-b border-studio-graphite/30">
        <div class="flex items-center justify-between pl-14">
          <h2 class="font-display text-lg font-semibold text-studio-cream">{{ currentPage }}</h2>
          <div class="waveform">
            <div class="waveform-bar"></div>
            <div class="waveform-bar"></div>
            <div class="waveform-bar"></div>
            <div class="waveform-bar"></div>
            <div class="waveform-bar"></div>
          </div>
        </div>
      </div>

      <!-- Page content -->
      <div class="relative p-4 lg:p-8 xl:p-10">
        <RouterView v-slot="{ Component }">
          <Transition
            name="page"
            mode="out-in"
            appear
          >
            <component :is="Component" />
          </Transition>
        </RouterView>
      </div>
    </main>

    <!-- Mobile overlay -->
    <Transition name="fade">
      <div
        v-if="sidebarOpen"
        @click="sidebarOpen = false"
        class="lg:hidden fixed inset-0 bg-studio-void/80 backdrop-blur-sm z-40"
      />
    </Transition>
  </div>
</template>

<style scoped>
/* Page transition */
.page-enter-active,
.page-leave-active {
  transition: all 0.3s ease-out;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Fade transition for overlay */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
