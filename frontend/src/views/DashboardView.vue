<script setup lang="ts">
import { onMounted, computed, ref } from 'vue'
import { useSongsStore } from '@/stores/songs'
import { RouterLink } from 'vue-router'

const store = useSongsStore()
const mounted = ref(false)

onMounted(() => {
  store.fetchSystemStatus()
  store.fetchSongs(10)
  // Trigger entrance animations
  setTimeout(() => {
    mounted.value = true
  }, 100)
})

const stats = computed(() => store.systemStatus)
const songs = computed(() => store.songs)

// Calculate week-over-week change percentage
const weeklyGrowth = computed(() => {
  const total = stats.value?.songs?.total || 0
  const thisWeek = stats.value?.songs?.by_status?.pending || 0
  // Simple approximation: if we have songs this week, show growth
  if (total === 0) return { value: 0, isPositive: true }
  // In a real app, this would compare with last week's data from API
  const growth = total > 0 ? Math.round((thisWeek / total) * 100) : 0
  return { value: growth, isPositive: growth >= 0 }
})

// Pipeline steps with counts from stats
const pipelineSteps = computed(() => [
  { icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z', label: 'Detect', status: 'completed', count: stats.value?.songs?.by_status?.pending || 0 },
  { icon: 'M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12', label: 'Upload', status: 'completed', count: stats.value?.songs?.by_status?.uploading || 0 },
  { icon: 'M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3', label: 'Generate', status: 'active', count: stats.value?.songs?.by_status?.generating || 0 },
  { icon: 'M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4', label: 'Download', status: 'pending', count: stats.value?.songs?.by_status?.downloaded || 0 },
  { icon: 'M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z', label: 'Evaluate', status: 'pending', count: stats.value?.songs?.by_status?.evaluated || 0 },
  { icon: 'M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z', label: 'Publish', status: 'pending', count: stats.value?.songs?.by_status?.uploaded || 0 },
])

const statusMap: Record<string, string> = {
  pending: 'status-pending',
  generating: 'status-generating',
  downloaded: 'status-downloaded',
  evaluated: 'status-evaluated',
  uploaded: 'status-uploaded',
  failed: 'status-failed',
}

// Format large numbers
function formatNumber(num: number): string {
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'k'
  }
  return num.toString()
}
</script>

<template>
  <div class="space-y-8">
    <!-- Header Section -->
    <header
      class="flex flex-col lg:flex-row lg:items-end justify-between gap-6"
      :style="{
        opacity: mounted ? 1 : 0,
        transform: mounted ? 'translateY(0)' : 'translateY(-20px)',
        transition: 'all 0.6s ease-out'
      }"
    >
      <div>
        <div class="flex items-center gap-3 mb-3">
          <div class="w-1 h-8 rounded-full bg-gradient-to-b from-studio-rose-500 to-studio-violet-500"></div>
          <span class="text-xs font-condensed text-studio-stone uppercase tracking-[0.2em]">Overview</span>
        </div>
        <h1 class="font-display text-4xl lg:text-5xl font-semibold text-studio-cream tracking-tight">
          Dashboard
        </h1>
        <p class="text-studio-sand font-body mt-2 max-w-lg">
          Real-time overview of your song automation pipeline. Monitor generation, downloads, and publishing status.
        </p>
      </div>

      <!-- Status indicator -->
      <div class="flex items-center gap-4 self-start lg:self-auto">
        <div class="flex items-center gap-3 px-5 py-3 rounded-2xl bg-studio-black/60 backdrop-blur-sm border border-studio-graphite/40">
          <div class="led-indicator green pulsing"></div>
          <span class="text-sm font-medium text-studio-sand">Pipeline Active</span>
        </div>

        <!-- Waveform visualization -->
        <div class="hidden sm:flex waveform px-3">
          <div class="waveform-bar"></div>
          <div class="waveform-bar"></div>
          <div class="waveform-bar"></div>
          <div class="waveform-bar"></div>
          <div class="waveform-bar"></div>
        </div>
      </div>
    </header>

    <!-- Stats Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
      <!-- Total Songs -->
      <div
        class="stat-card rose group"
        :style="{
          opacity: mounted ? 1 : 0,
          transform: mounted ? 'translateY(0)' : 'translateY(20px)',
          transition: 'all 0.5s ease-out 0.1s'
        }"
      >
        <div class="flex items-start justify-between">
          <div>
            <p class="text-xs font-condensed text-studio-stone uppercase tracking-wider mb-2">Total Songs</p>
            <p class="text-4xl font-display font-semibold text-studio-cream">
              {{ formatNumber(stats?.songs?.total || 0) }}
            </p>
            <p v-if="weeklyGrowth.value > 0" class="text-xs text-studio-stone mt-2 flex items-center gap-1">
              <svg class="w-3 h-3 text-studio-success" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clip-rule="evenodd" />
              </svg>
              <span class="text-studio-success">+{{ weeklyGrowth.value }}%</span> pending
            </p>
            <p v-else class="text-xs text-studio-stone mt-2">
              All songs in library
            </p>
          </div>
          <div class="w-14 h-14 rounded-2xl bg-studio-graphite/50 flex items-center justify-center group-hover:bg-studio-rose-500/10 transition-all duration-300">
            <svg class="w-7 h-7 text-studio-rose-400 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
            </svg>
          </div>
        </div>
      </div>

      <!-- Pending Tasks -->
      <div
        class="stat-card amber group"
        :style="{
          opacity: mounted ? 1 : 0,
          transform: mounted ? 'translateY(0)' : 'translateY(20px)',
          transition: 'all 0.5s ease-out 0.15s'
        }"
      >
        <div class="flex items-start justify-between">
          <div>
            <p class="text-xs font-condensed text-studio-stone uppercase tracking-wider mb-2">Pending Tasks</p>
            <p class="text-4xl font-display font-semibold text-studio-cream">
              {{ stats?.tasks?.by_status?.pending || 0 }}
            </p>
            <p class="text-xs text-studio-stone mt-2">
              In queue for processing
            </p>
          </div>
          <div class="w-14 h-14 rounded-2xl bg-studio-graphite/50 flex items-center justify-center group-hover:bg-amber-500/10 transition-all duration-300">
            <svg class="w-7 h-7 text-amber-400 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
      </div>

      <!-- Running -->
      <div
        class="stat-card violet group"
        :style="{
          opacity: mounted ? 1 : 0,
          transform: mounted ? 'translateY(0)' : 'translateY(20px)',
          transition: 'all 0.5s ease-out 0.2s'
        }"
      >
        <div class="flex items-start justify-between">
          <div>
            <p class="text-xs font-condensed text-studio-stone uppercase tracking-wider mb-2">Running</p>
            <p class="text-4xl font-display font-semibold text-studio-cream">
              {{ stats?.tasks?.by_status?.running || 0 }}
            </p>
            <p class="text-xs text-studio-stone mt-2 flex items-center gap-2">
              <span class="inline-block w-1.5 h-1.5 rounded-full bg-studio-violet-500 animate-led-pulse"></span>
              Active processing
            </p>
          </div>
          <div class="w-14 h-14 rounded-2xl bg-studio-graphite/50 flex items-center justify-center group-hover:bg-studio-violet-500/10 transition-all duration-300">
            <svg class="w-7 h-7 text-studio-violet-400 group-hover:scale-110 transition-transform animate-pulse-soft" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
        </div>
      </div>

      <!-- Published -->
      <div
        class="stat-card gold group"
        :style="{
          opacity: mounted ? 1 : 0,
          transform: mounted ? 'translateY(0)' : 'translateY(20px)',
          transition: 'all 0.5s ease-out 0.25s'
        }"
      >
        <div class="flex items-start justify-between">
          <div>
            <p class="text-xs font-condensed text-studio-stone uppercase tracking-wider mb-2">Published</p>
            <p class="text-4xl font-display font-semibold text-studio-cream">
              {{ stats?.songs?.by_status?.uploaded || 0 }}
            </p>
            <p class="text-xs text-studio-stone mt-2">
              Live on YouTube
            </p>
          </div>
          <div class="w-14 h-14 rounded-2xl bg-studio-graphite/50 flex items-center justify-center group-hover:bg-studio-gold/10 transition-all duration-300">
            <svg class="w-7 h-7 text-studio-gold group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- Pipeline Status -->
    <section
      class="card-static"
      :style="{
        opacity: mounted ? 1 : 0,
        transform: mounted ? 'translateY(0)' : 'translateY(20px)',
        transition: 'all 0.5s ease-out 0.3s'
      }"
    >
      <div class="flex items-center gap-3 mb-8">
        <div class="w-2 h-2 rounded-full bg-studio-rose-500" style="box-shadow: 0 0 8px rgba(204, 122, 90, 0.5);"></div>
        <h3 class="text-sm font-condensed text-studio-sand uppercase tracking-widest">Pipeline Status</h3>
      </div>

      <div class="flex items-center justify-between overflow-x-auto pb-4 px-2 -mx-2">
        <template v-for="(step, index) in pipelineSteps" :key="step.label">
          <div class="flex flex-col items-center min-w-[100px] group">
            <div class="relative">
              <!-- Step circle -->
              <div
                :class="[
                  'w-16 h-16 lg:w-20 lg:h-20 rounded-2xl flex items-center justify-center transition-all duration-500',
                  step.status === 'completed'
                    ? 'bg-gradient-to-br from-studio-rose-500 to-studio-amber shadow-glow-rose'
                    : step.status === 'active'
                      ? 'border-2 border-studio-success bg-studio-graphite/50 animate-pulse-glow'
                      : 'border border-studio-slate/30 bg-studio-charcoal/30'
                ]"
                :style="{
                  opacity: mounted ? 1 : 0,
                  transform: mounted ? 'scale(1)' : 'scale(0.8)',
                  transition: `all 0.4s ease-out ${0.3 + index * 0.08}s`
                }"
              >
                <svg
                  :class="[
                    'w-7 h-7 lg:w-8 lg:h-8 transition-all',
                    step.status === 'completed' ? 'text-white' : step.status === 'active' ? 'text-studio-success' : 'text-studio-slate'
                  ]"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" :d="step.icon" />
                </svg>
              </div>

              <!-- Badge count -->
              <Transition name="scale">
                <div
                  v-if="step.count > 0"
                  class="absolute -top-2 -right-2 min-w-[28px] h-7 px-2 rounded-full bg-gradient-to-r from-studio-rose-500 to-studio-amber text-white text-xs font-bold flex items-center justify-center shadow-lg"
                >
                  {{ step.count }}
                </div>
              </Transition>
            </div>

            <span class="text-xs text-studio-sand mt-4 font-medium">{{ step.label }}</span>

            <!-- Status dot -->
            <div
              v-if="step.status === 'active'"
              class="w-1.5 h-1.5 rounded-full bg-studio-success mt-2 animate-led-pulse"
            ></div>
          </div>

          <!-- Connector line -->
          <div
            v-if="index < pipelineSteps.length - 1"
            :class="[
              'flex-1 h-0.5 mx-2 lg:mx-4 rounded-full transition-all duration-700',
              step.status === 'completed'
                ? 'bg-gradient-to-r from-studio-rose-500 to-studio-amber'
                : 'bg-studio-graphite/50'
            ]"
            :style="{
              opacity: mounted ? 1 : 0,
              transition: `all 0.5s ease-out ${0.4 + index * 0.1}s`
            }"
          />
        </template>
      </div>
    </section>

    <!-- Recent Songs -->
    <section
      class="card-static"
      :style="{
        opacity: mounted ? 1 : 0,
        transform: mounted ? 'translateY(0)' : 'translateY(20px)',
        transition: 'all 0.5s ease-out 0.4s'
      }"
    >
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-3">
          <div class="w-2 h-2 rounded-full bg-studio-rose-500" style="box-shadow: 0 0 8px rgba(204, 122, 90, 0.5);"></div>
          <h3 class="text-sm font-condensed text-studio-sand uppercase tracking-widest">Recent Songs</h3>
        </div>
        <RouterLink
          to="/library"
          class="group flex items-center gap-2 text-sm text-studio-rose-400 hover:text-studio-rose-300 transition-colors font-condensed uppercase tracking-wider"
        >
          View All
          <svg class="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </RouterLink>
      </div>

      <!-- Songs list -->
      <div v-if="songs.length" class="space-y-3">
        <RouterLink
          v-for="(song, index) in songs"
          :key="song.id"
          :to="`/library/${song.id}`"
          class="group flex items-center justify-between p-4 rounded-xl bg-studio-charcoal/20 border border-transparent hover:border-studio-rose-500/20 hover:bg-studio-charcoal/40 transition-all duration-300 cursor-pointer"
          :style="{
            opacity: mounted ? 1 : 0,
            transform: mounted ? 'translateX(0)' : 'translateX(-20px)',
            transition: `all 0.4s ease-out ${0.5 + index * 0.05}s`
          }"
        >
          <div class="flex items-center gap-4">
            <!-- Vinyl mini disc -->
            <div class="relative w-14 h-14 flex-shrink-0">
              <div
                class="w-full h-full vinyl-disc group-hover:animate-spin-slow transition-all"
              >
                <div class="vinyl-label w-4 h-4"></div>
              </div>
              <!-- Play overlay on hover -->
              <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                <div class="w-8 h-8 rounded-full bg-studio-rose-500/90 flex items-center justify-center shadow-lg">
                  <svg class="w-4 h-4 text-white ml-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z" />
                  </svg>
                </div>
              </div>
            </div>

            <div class="min-w-0">
              <h4 class="font-medium text-studio-cream group-hover:text-studio-rose-400 transition-colors truncate">
                {{ song.title }}
              </h4>
              <div class="flex items-center gap-3 mt-1">
                <span class="text-xs text-studio-stone font-mono px-2 py-0.5 rounded bg-studio-graphite/50">
                  {{ song.genre || 'Unknown' }}
                </span>
                <span class="text-xs text-studio-slate">
                  {{ song.created_at?.slice(0, 10) }}
                </span>
              </div>
            </div>
          </div>

          <!-- Status badge -->
          <div :class="['status-badge', statusMap[song.status] || 'status-pending']">
            <span class="dot"></span>
            {{ song.status }}
          </div>
        </RouterLink>
      </div>

      <!-- Empty state -->
      <div v-else class="text-center py-20">
        <div class="relative w-24 h-24 mx-auto mb-6">
          <div class="absolute inset-0 rounded-full bg-studio-graphite/30 animate-pulse"></div>
          <div class="absolute inset-2 vinyl-disc">
            <div class="vinyl-label w-6 h-6"></div>
          </div>
        </div>
        <h4 class="text-lg font-display font-medium text-studio-cream mb-2">No songs yet</h4>
        <p class="text-sm text-studio-stone max-w-xs mx-auto">
          Add song files to the pipeline to start generating music
        </p>
        <RouterLink
          to="/queue"
          class="btn btn-primary mt-6"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 4v16m8-8H4" />
          </svg>
          Add Songs
        </RouterLink>
      </div>
    </section>
  </div>
</template>

<style scoped>
/* Scale transition for badges */
.scale-enter-active,
.scale-leave-active {
  transition: all 0.3s ease;
}

.scale-enter-from,
.scale-leave-to {
  opacity: 0;
  transform: scale(0.5);
}
</style>
