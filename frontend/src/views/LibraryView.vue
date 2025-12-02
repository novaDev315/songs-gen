<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useSongsStore } from '@/stores/songs'
import { RouterLink } from 'vue-router'

const songsStore = useSongsStore()
const mounted = ref(false)

// View mode and filters
const viewMode = ref<'grid' | 'list'>('grid')
const searchQuery = ref('')
const statusFilter = ref<string>('all')
const genreFilter = ref<string>('all')

// Pagination
const currentPage = ref(1)
const itemsPerPage = 12

// Unique values for filters
const uniqueStatuses = computed(() => {
  const statuses = new Set(songsStore.songs.map((s) => s.status))
  return ['all', ...Array.from(statuses)]
})

const uniqueGenres = computed(() => {
  const genres = new Set(songsStore.songs.map((s) => s.genre))
  return ['all', ...Array.from(genres)]
})

// Filtered songs
const filteredSongs = computed(() => {
  let songs = songsStore.songs

  // Search filter
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    songs = songs.filter(
      (song) =>
        song.title.toLowerCase().includes(query) ||
        song.genre.toLowerCase().includes(query) ||
        song.id.toLowerCase().includes(query)
    )
  }

  // Status filter
  if (statusFilter.value !== 'all') {
    songs = songs.filter((song) => song.status === statusFilter.value)
  }

  // Genre filter
  if (genreFilter.value !== 'all') {
    songs = songs.filter((song) => song.genre === genreFilter.value)
  }

  return songs
})

// Paginated songs
const paginatedSongs = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredSongs.value.slice(start, end)
})

// Pagination info
const totalPages = computed(() => {
  return Math.ceil(filteredSongs.value.length / itemsPerPage)
})

const paginationInfo = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage + 1
  const end = Math.min(currentPage.value * itemsPerPage, filteredSongs.value.length)
  return `${start}-${end} of ${filteredSongs.value.length}`
})

// Pagination handlers
function goToPage(page: number) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

function nextPage() {
  goToPage(currentPage.value + 1)
}

function prevPage() {
  goToPage(currentPage.value - 1)
}

// Format date
function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  }).format(date)
}

// Format quality score
function formatQualityScore(score: number | null): string {
  if (score === null) return '—'
  return score.toFixed(1)
}

// Status badge classes
const statusMap: Record<string, string> = {
  pending: 'status-pending',
  generating: 'status-generating',
  downloaded: 'status-downloaded',
  evaluated: 'status-evaluated',
  uploaded: 'status-uploaded',
  failed: 'status-failed',
}

// Reset filters
function resetFilters() {
  searchQuery.value = ''
  statusFilter.value = 'all'
  genreFilter.value = 'all'
  currentPage.value = 1
}

// Watch filters and reset pagination
watch([searchQuery, statusFilter, genreFilter], () => {
  currentPage.value = 1
})

onMounted(async () => {
  await songsStore.fetchSongs()
  setTimeout(() => {
    mounted.value = true
  }, 100)
})
</script>

<template>
  <div class="space-y-8">
    <!-- Header -->
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
          <div class="w-1 h-8 rounded-full bg-gradient-to-b from-studio-violet-500 to-studio-rose-500"></div>
          <span class="text-xs font-condensed text-studio-stone uppercase tracking-[0.2em]">Collection</span>
        </div>
        <h1 class="font-display text-4xl lg:text-5xl font-semibold text-studio-cream tracking-tight">
          Song Library
        </h1>
        <p class="text-studio-sand font-body mt-2 max-w-lg">
          Browse, search, and manage all your generated songs in one place.
        </p>
      </div>

      <!-- Quick stats -->
      <div class="flex items-center gap-4">
        <div class="px-4 py-2 rounded-xl bg-studio-black/60 border border-studio-graphite/40">
          <span class="text-2xl font-display font-semibold text-studio-cream">{{ songsStore.songs.length }}</span>
          <span class="text-xs text-studio-stone ml-2 uppercase tracking-wider">Total Songs</span>
        </div>
      </div>
    </header>

    <!-- Filters and Controls -->
    <div
      class="card-static"
      :style="{
        opacity: mounted ? 1 : 0,
        transform: mounted ? 'translateY(0)' : 'translateY(20px)',
        transition: 'all 0.5s ease-out 0.1s'
      }"
    >
      <div class="grid grid-cols-1 md:grid-cols-12 gap-4 mb-6">
        <!-- Search Input -->
        <div class="md:col-span-5">
          <label class="input-label">Search</label>
          <div class="input-group">
            <svg class="input-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search by title, genre, or ID..."
              class="input-field with-icon"
            />
          </div>
        </div>

        <!-- Status Filter -->
        <div class="md:col-span-3">
          <label class="input-label">Status</label>
          <select v-model="statusFilter" class="input-field">
            <option v-for="status in uniqueStatuses" :key="status" :value="status">
              {{ status === 'all' ? 'All Statuses' : status.charAt(0).toUpperCase() + status.slice(1) }}
            </option>
          </select>
        </div>

        <!-- Genre Filter -->
        <div class="md:col-span-3">
          <label class="input-label">Genre</label>
          <select v-model="genreFilter" class="input-field">
            <option v-for="genre in uniqueGenres" :key="genre" :value="genre">
              {{ genre === 'all' ? 'All Genres' : genre.charAt(0).toUpperCase() + genre.slice(1) }}
            </option>
          </select>
        </div>

        <!-- Reset Button -->
        <div class="md:col-span-1 flex items-end">
          <button
            @click="resetFilters"
            class="w-full btn btn-ghost h-[50px]"
            title="Reset filters"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
      </div>

      <!-- View Controls -->
      <div class="flex items-center justify-between pt-4 border-t border-studio-graphite/30">
        <div class="flex items-center gap-3">
          <span class="text-sm text-studio-stone">
            <span class="text-studio-rose-400 font-medium">{{ filteredSongs.length }}</span> songs found
          </span>
        </div>

        <!-- View Mode Toggle -->
        <div class="flex items-center gap-1 p-1 rounded-xl bg-studio-charcoal/50 border border-studio-graphite/30">
          <button
            @click="viewMode = 'grid'"
            :class="[
              'p-2.5 rounded-lg transition-all duration-300',
              viewMode === 'grid'
                ? 'bg-studio-rose-500/20 text-studio-rose-400 shadow-glow-rose-sm'
                : 'text-studio-stone hover:text-studio-cream'
            ]"
            title="Grid view"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
            </svg>
          </button>
          <button
            @click="viewMode = 'list'"
            :class="[
              'p-2.5 rounded-lg transition-all duration-300',
              viewMode === 'list'
                ? 'bg-studio-rose-500/20 text-studio-rose-400 shadow-glow-rose-sm'
                : 'text-studio-stone hover:text-studio-cream'
            ]"
            title="List view"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="songsStore.loading" class="flex flex-col items-center justify-center py-20">
      <div class="relative w-20 h-20 mb-6">
        <div class="absolute inset-0 vinyl-disc animate-spin-slow">
          <div class="vinyl-label w-6 h-6"></div>
        </div>
      </div>
      <p class="text-studio-sand animate-pulse-soft">Loading library...</p>
    </div>

    <!-- Error State -->
    <div
      v-else-if="songsStore.error"
      class="card-static border-studio-error/30 bg-studio-error-dim/10 text-center py-12"
    >
      <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-studio-error/10 flex items-center justify-center">
        <svg class="w-8 h-8 text-studio-error" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      </div>
      <p class="text-studio-error font-medium mb-4">{{ songsStore.error }}</p>
      <button @click="songsStore.fetchSongs()" class="btn btn-primary">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        Retry
      </button>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredSongs.length === 0" class="text-center py-20">
      <div class="relative w-24 h-24 mx-auto mb-6">
        <div class="absolute inset-0 rounded-full bg-studio-graphite/20 animate-pulse"></div>
        <div class="absolute inset-3 rounded-full bg-studio-graphite/30 flex items-center justify-center">
          <svg class="w-10 h-10 text-studio-slate" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>
      <h3 class="text-xl font-display font-medium text-studio-cream mb-2">No Songs Found</h3>
      <p class="text-studio-stone mb-6 max-w-sm mx-auto">
        Try adjusting your filters or search query to find what you're looking for.
      </p>
      <button @click="resetFilters" class="btn btn-secondary">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M6 18L18 6M6 6l12 12" />
        </svg>
        Clear Filters
      </button>
    </div>

    <!-- Grid View -->
    <div
      v-else-if="viewMode === 'grid'"
      class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5"
    >
      <RouterLink
        v-for="(song, index) in paginatedSongs"
        :key="song.id"
        :to="`/library/${song.id}`"
        class="group card hover:scale-[1.02] active:scale-[0.98]"
        :style="{
          opacity: mounted ? 1 : 0,
          transform: mounted ? 'translateY(0)' : 'translateY(20px)',
          transition: `all 0.4s ease-out ${0.15 + index * 0.03}s`
        }"
      >
        <!-- Cover art placeholder with vinyl effect -->
        <div class="relative aspect-square mb-4 rounded-xl overflow-hidden bg-studio-charcoal/50">
          <div class="absolute inset-0 flex items-center justify-center">
            <div class="w-3/4 h-3/4 vinyl-disc group-hover:animate-spin-slow transition-all">
              <div class="vinyl-label w-1/3 h-1/3"></div>
            </div>
          </div>

          <!-- Gradient overlay -->
          <div class="absolute inset-0 bg-gradient-to-t from-studio-black/80 via-transparent to-transparent"></div>

          <!-- Play button on hover -->
          <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all duration-300">
            <div class="w-14 h-14 rounded-full bg-studio-rose-500/90 flex items-center justify-center shadow-glow-rose transform scale-90 group-hover:scale-100 transition-transform">
              <svg class="w-6 h-6 text-white ml-1" fill="currentColor" viewBox="0 0 20 20">
                <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z" />
              </svg>
            </div>
          </div>

          <!-- Status badge -->
          <div class="absolute top-3 right-3">
            <div :class="['status-badge text-2xs', statusMap[song.status] || 'status-pending']">
              <span class="dot"></span>
              {{ song.status }}
            </div>
          </div>
        </div>

        <!-- Song info -->
        <div>
          <h3 class="font-medium text-studio-cream group-hover:text-studio-rose-400 transition-colors line-clamp-1 mb-2">
            {{ song.title }}
          </h3>

          <div class="flex items-center justify-between">
            <span class="text-xs font-mono text-studio-stone px-2 py-1 rounded-lg bg-studio-graphite/50">
              {{ song.genre || 'Unknown' }}
            </span>

            <div class="flex items-center gap-1 text-studio-amber">
              <svg v-if="song.quality_score" class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
              </svg>
              <span class="text-sm font-mono">{{ formatQualityScore(song.quality_score) }}</span>
            </div>
          </div>

          <p class="text-xs text-studio-slate mt-2">{{ formatDate(song.created_at) }}</p>
        </div>
      </RouterLink>
    </div>

    <!-- List View -->
    <div
      v-else
      class="card-static overflow-hidden"
      :style="{
        opacity: mounted ? 1 : 0,
        transform: mounted ? 'translateY(0)' : 'translateY(20px)',
        transition: 'all 0.5s ease-out 0.15s'
      }"
    >
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-studio-graphite/50">
              <th class="text-left py-4 px-5 text-xs text-studio-stone uppercase tracking-wider font-condensed">
                Song
              </th>
              <th class="text-left py-4 px-5 text-xs text-studio-stone uppercase tracking-wider font-condensed">
                Genre
              </th>
              <th class="text-left py-4 px-5 text-xs text-studio-stone uppercase tracking-wider font-condensed">
                Status
              </th>
              <th class="text-left py-4 px-5 text-xs text-studio-stone uppercase tracking-wider font-condensed">
                Quality
              </th>
              <th class="text-left py-4 px-5 text-xs text-studio-stone uppercase tracking-wider font-condensed">
                Created
              </th>
            </tr>
          </thead>
          <tbody>
            <RouterLink
              v-for="(song, index) in paginatedSongs"
              :key="song.id"
              :to="`/library/${song.id}`"
              custom
              v-slot="{ navigate }"
            >
              <tr
                @click="navigate"
                class="border-b border-studio-graphite/30 hover:bg-studio-graphite/20 transition-all duration-200 cursor-pointer group"
                :style="{
                  opacity: mounted ? 1 : 0,
                  transform: mounted ? 'translateX(0)' : 'translateX(-20px)',
                  transition: `all 0.3s ease-out ${0.15 + index * 0.03}s`
                }"
              >
                <td class="py-4 px-5">
                  <div class="flex items-center gap-4">
                    <!-- Mini vinyl -->
                    <div class="w-10 h-10 vinyl-disc flex-shrink-0 group-hover:animate-spin-slow">
                      <div class="vinyl-label w-3 h-3"></div>
                    </div>
                    <div>
                      <p class="font-medium text-studio-cream group-hover:text-studio-rose-400 transition-colors">
                        {{ song.title }}
                      </p>
                      <p class="text-xs text-studio-slate font-mono">{{ song.id.slice(0, 8) }}...</p>
                    </div>
                  </div>
                </td>
                <td class="py-4 px-5">
                  <span class="text-xs font-mono text-studio-stone px-2 py-1 rounded-lg bg-studio-graphite/50">
                    {{ song.genre || 'Unknown' }}
                  </span>
                </td>
                <td class="py-4 px-5">
                  <div :class="['status-badge', statusMap[song.status] || 'status-pending']">
                    <span class="dot"></span>
                    {{ song.status }}
                  </div>
                </td>
                <td class="py-4 px-5">
                  <div class="flex items-center gap-1 text-studio-amber">
                    <svg v-if="song.quality_score" class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                    <span class="font-mono text-sm">{{ formatQualityScore(song.quality_score) }}</span>
                  </div>
                </td>
                <td class="py-4 px-5 text-studio-stone text-sm">
                  {{ formatDate(song.created_at) }}
                </td>
              </tr>
            </RouterLink>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Pagination -->
    <div
      v-if="totalPages > 1"
      class="flex flex-col sm:flex-row items-center justify-between gap-4"
      :style="{
        opacity: mounted ? 1 : 0,
        transition: 'opacity 0.5s ease-out 0.3s'
      }"
    >
      <p class="text-sm text-studio-stone">
        Showing <span class="text-studio-cream font-medium">{{ paginationInfo }}</span>
      </p>

      <div class="flex items-center gap-2">
        <!-- Previous button -->
        <button
          @click="prevPage"
          :disabled="currentPage === 1"
          class="btn btn-sm btn-ghost"
          :class="{ 'opacity-50 cursor-not-allowed': currentPage === 1 }"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          Prev
        </button>

        <!-- Page numbers -->
        <div class="flex items-center gap-1">
          <template v-for="page in totalPages" :key="page">
            <button
              v-if="page <= 3 || page > totalPages - 2 || Math.abs(page - currentPage) <= 1"
              @click="goToPage(page)"
              :class="[
                'w-10 h-10 rounded-xl text-sm font-medium transition-all duration-300',
                currentPage === page
                  ? 'bg-studio-rose-500/20 text-studio-rose-400 border border-studio-rose-500/30'
                  : 'text-studio-stone hover:text-studio-cream hover:bg-studio-graphite/50'
              ]"
            >
              {{ page }}
            </button>
            <span
              v-else-if="page === 4 || page === totalPages - 2"
              class="w-10 h-10 flex items-center justify-center text-studio-slate"
            >
              ...
            </span>
          </template>
        </div>

        <!-- Next button -->
        <button
          @click="nextPage"
          :disabled="currentPage === totalPages"
          class="btn btn-sm btn-ghost"
          :class="{ 'opacity-50 cursor-not-allowed': currentPage === totalPages }"
        >
          Next
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
