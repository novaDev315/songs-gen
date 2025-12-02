<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useStudioStore } from '@/stores/studio'
import { api } from '@/api/client'

const store = useStudioStore()
const songs = ref<any[]>([])
const isLoading = ref(true)
const filter = ref('')
const mounted = ref(false)

onMounted(async () => {
  try {
    songs.value = await api.getSongs(100, 'downloaded')
  } catch (e) {
    console.error('Failed to load songs', e)
  } finally {
    isLoading.value = false
    setTimeout(() => mounted.value = true, 100)
  }
})

const filteredSongs = computed(() => {
  if (!filter.value) return songs.value
  const q = filter.value.toLowerCase()
  return songs.value.filter(s =>
    s.title.toLowerCase().includes(q) ||
    s.genre.toLowerCase().includes(q)
  )
})

function selectSong(song: any) {
  store.selectSong(song)
}

function formatDuration(seconds: number): string {
  if (!seconds) return '--:--'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}
</script>

<template>
  <div class="space-y-6">
    <!-- Step Header -->
    <div class="flex items-start justify-between">
      <div>
        <div class="flex items-center gap-2 mb-2">
          <div class="led-indicator amber"></div>
          <span class="text-xs font-condensed text-studio-stone uppercase tracking-widest">Source Selection</span>
        </div>
        <h2 class="text-xl font-display font-semibold text-studio-cream">Select a Song</h2>
        <p class="text-sm text-studio-sand mt-1">Choose a downloaded track for video production</p>
      </div>
      <div class="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-studio-charcoal/50 border border-studio-graphite/40">
        <svg class="w-4 h-4 text-studio-stone" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
        </svg>
        <span class="text-xs text-studio-sand">{{ songs.length }} tracks</span>
      </div>
    </div>

    <!-- Search Input -->
    <div class="input-group">
      <svg class="input-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
      <input
        v-model="filter"
        type="text"
        placeholder="Search by title or genre..."
        class="input-field with-icon"
      />
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex flex-col items-center justify-center py-16">
      <div class="relative w-16 h-16 mb-4">
        <div class="absolute inset-0 rounded-full border-4 border-studio-graphite/30"></div>
        <div class="absolute inset-0 rounded-full border-4 border-studio-rose-500 border-t-transparent animate-spin"></div>
      </div>
      <p class="text-studio-sand text-sm">Loading your library...</p>
    </div>

    <!-- Song Grid -->
    <div v-else-if="filteredSongs.length > 0" class="grid gap-3 md:grid-cols-2">
      <button
        v-for="(song, index) in filteredSongs"
        :key="song.id"
        @click="selectSong(song)"
        class="group relative p-4 rounded-xl text-left transition-all duration-300 border"
        :class="[
          store.selectedSong?.id === song.id
            ? 'bg-studio-rose-500/10 border-studio-rose-500/50 shadow-lg shadow-studio-rose-500/10'
            : 'bg-studio-charcoal/30 border-studio-graphite/40 hover:bg-studio-charcoal/50 hover:border-studio-rose-500/20'
        ]"
        :style="{
          opacity: mounted ? 1 : 0,
          transform: mounted ? 'translateY(0)' : 'translateY(10px)',
          transition: `all 0.3s ease-out ${index * 0.05}s`
        }"
      >
        <!-- Selection Indicator -->
        <div
          v-if="store.selectedSong?.id === song.id"
          class="absolute top-3 right-3"
        >
          <div class="led-indicator green"></div>
        </div>

        <div class="flex items-center gap-4">
          <!-- Album Art / Icon -->
          <div
            class="w-14 h-14 rounded-xl flex items-center justify-center transition-all duration-300"
            :class="[
              store.selectedSong?.id === song.id
                ? 'bg-studio-rose-500/20'
                : 'bg-studio-graphite/50 group-hover:bg-studio-rose-500/10'
            ]"
          >
            <svg
              class="w-7 h-7 transition-colors"
              :class="[
                store.selectedSong?.id === song.id
                  ? 'text-studio-rose-400'
                  : 'text-studio-sand group-hover:text-studio-rose-400'
              ]"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
            </svg>
          </div>

          <!-- Song Info -->
          <div class="flex-1 min-w-0">
            <h3
              class="font-medium truncate transition-colors"
              :class="[
                store.selectedSong?.id === song.id
                  ? 'text-studio-rose-400'
                  : 'text-studio-cream group-hover:text-studio-rose-400'
              ]"
            >
              {{ song.title }}
            </h3>
            <div class="flex items-center gap-3 mt-1">
              <span class="text-xs text-studio-stone uppercase tracking-wider">{{ song.genre }}</span>
              <span class="text-studio-graphite">•</span>
              <span class="text-xs text-studio-slate font-mono">{{ formatDuration(song.duration) }}</span>
            </div>
          </div>

          <!-- Waveform Preview (decorative) -->
          <div class="hidden sm:flex items-end gap-0.5 h-8 opacity-50 group-hover:opacity-100 transition-opacity">
            <div v-for="i in 5" :key="i"
              class="w-1 rounded-full bg-studio-rose-500/50"
              :style="{ height: `${Math.random() * 24 + 8}px` }"
            ></div>
          </div>
        </div>

        <!-- VU Meter Style Selection Indicator -->
        <div
          v-if="store.selectedSong?.id === song.id"
          class="mt-3 flex items-center gap-1"
        >
          <div v-for="i in 10" :key="i"
            class="flex-1 h-1 rounded-sm"
            :class="[
              i <= 7 ? 'bg-studio-vu-green' : i <= 9 ? 'bg-studio-vu-yellow' : 'bg-studio-vu-red'
            ]"
          ></div>
        </div>
      </button>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-16">
      <div class="w-20 h-20 mx-auto mb-4 rounded-2xl bg-studio-charcoal/50 flex items-center justify-center">
        <svg class="w-10 h-10 text-studio-slate" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
        </svg>
      </div>
      <h4 class="text-lg font-display font-medium text-studio-cream mb-2">No Tracks Found</h4>
      <p class="text-studio-stone text-sm">
        {{ filter ? 'No songs match your search' : 'Download songs from Suno first' }}
      </p>
    </div>

    <!-- Selected Song Info Card -->
    <div
      v-if="store.selectedSong"
      class="stat-card rose"
      :style="{
        opacity: mounted ? 1 : 0,
        transform: mounted ? 'translateY(0)' : 'translateY(10px)',
        transition: 'all 0.4s ease-out 0.2s'
      }"
    >
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 rounded-xl bg-studio-rose-500/20 flex items-center justify-center">
          <svg class="w-6 h-6 text-studio-rose-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <div class="flex-1">
          <p class="text-xs font-condensed text-studio-stone uppercase tracking-wider">Selected Track</p>
          <p class="text-lg font-display font-semibold text-studio-cream">{{ store.selectedSong.title }}</p>
          <p class="text-sm text-studio-sand">{{ store.selectedSong.genre }} • {{ formatDuration(store.selectedSong.duration) }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
