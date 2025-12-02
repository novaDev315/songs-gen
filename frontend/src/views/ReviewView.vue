<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { StatusBadge } from '@/components'
import { useSongsStore, type Song } from '@/stores/songs'
import { api } from '@/api/client'

const songsStore = useSongsStore()
const mounted = ref(false)

// Star rating state
const ratings = ref<Record<string, number>>({})
const notes = ref<Record<string, string>>({})
const submitting = ref<Record<string, boolean>>({})

// Computed filtered songs
const pendingSongs = computed(() => {
  return songsStore.songs.filter(
    (song) => song.status === 'downloaded' || song.status === 'pending'
  )
})

// Stats
const reviewStats = computed(() => ({
  total: pendingSongs.value.length,
  avgRating: calculateAvgRating(),
  reviewed: songsStore.songs.filter(s => s.status === 'evaluated' || s.status === 'uploaded').length
}))

function calculateAvgRating(): number {
  const ratedSongs = songsStore.songs.filter((s) => s.quality_score)
  if (ratedSongs.length === 0) return 0
  const sum = ratedSongs.reduce((acc, s) => acc + (s.quality_score || 0), 0)
  return Math.round((sum / ratedSongs.length) * 10) / 10
}

// Star rating handlers
function setRating(songId: string, rating: number) {
  ratings.value[songId] = rating
}

function getRating(songId: string): number {
  return ratings.value[songId] || 0
}

// Submit evaluation
async function approve(song: Song) {
  const rating = getRating(song.id)
  if (rating === 0) {
    alert('Please select a rating before approving')
    return
  }

  submitting.value[song.id] = true
  try {
    await api.submitEvaluation(song.id, {
      approved: true,
      rating,
      notes: notes.value[song.id] || ''
    })

    // Clear local state
    delete ratings.value[song.id]
    delete notes.value[song.id]

    // Refresh songs
    await songsStore.fetchSongs()
  } catch (error) {
    console.error('Failed to approve song:', error)
    alert('Failed to approve song. Please try again.')
  } finally {
    submitting.value[song.id] = false
  }
}

async function reject(song: Song) {
  const confirmReject = confirm(`Reject "${song.title}"? This action cannot be undone.`)
  if (!confirmReject) return

  submitting.value[song.id] = true
  try {
    await api.submitEvaluation(song.id, {
      approved: false,
      rating: getRating(song.id) || 1,
      notes: notes.value[song.id] || 'Rejected by reviewer'
    })

    // Clear local state
    delete ratings.value[song.id]
    delete notes.value[song.id]

    // Refresh songs
    await songsStore.fetchSongs()
  } catch (error) {
    console.error('Failed to reject song:', error)
    alert('Failed to reject song. Please try again.')
  } finally {
    submitting.value[song.id] = false
  }
}

// Truncate style prompt for preview
function truncateText(text: string | undefined, maxLength = 100): string {
  if (!text) return 'N/A'
  return text.length > maxLength ? text.slice(0, maxLength) + '...' : text
}

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
          <div class="w-1 h-8 rounded-full bg-gradient-to-b from-studio-gold to-amber-500"></div>
          <span class="text-xs font-condensed text-studio-stone uppercase tracking-[0.2em]">Quality Control</span>
        </div>
        <h1 class="font-display text-4xl lg:text-5xl font-semibold text-studio-cream tracking-tight">
          Review Songs
        </h1>
        <p class="text-studio-sand font-body mt-2 max-w-lg">
          Evaluate generated songs before publishing to YouTube.
        </p>
      </div>

</header>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-5">
      <!-- Pending Review -->
      <div
        class="stat-card amber group"
        :style="{
          opacity: mounted ? 1 : 0,
          transform: mounted ? 'translateY(0)' : 'translateY(20px)',
          transition: 'all 0.5s ease-out 0.1s'
        }"
      >
        <div class="flex items-start justify-between">
          <div>
            <p class="text-xs font-condensed text-studio-stone uppercase tracking-wider mb-2">Pending Review</p>
            <p class="text-4xl font-display font-semibold text-studio-cream">
              {{ reviewStats.total }}
            </p>
            <p class="text-xs text-studio-stone mt-2">
              Songs awaiting evaluation
            </p>
          </div>
          <div class="w-14 h-14 rounded-2xl bg-studio-graphite/50 flex items-center justify-center group-hover:bg-amber-500/10 transition-all duration-300">
            <svg class="w-7 h-7 text-amber-400 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
      </div>

      <!-- Average Rating -->
      <div
        class="stat-card gold group"
        :style="{
          opacity: mounted ? 1 : 0,
          transform: mounted ? 'translateY(0)' : 'translateY(20px)',
          transition: 'all 0.5s ease-out 0.15s'
        }"
      >
        <div class="flex items-start justify-between">
          <div>
            <p class="text-xs font-condensed text-studio-stone uppercase tracking-wider mb-2">Average Rating</p>
            <p class="text-4xl font-display font-semibold text-studio-cream">
              {{ reviewStats.avgRating }}
            </p>
            <p class="text-xs text-studio-stone mt-2 flex items-center gap-1">
              <svg class="w-3 h-3 text-studio-gold" fill="currentColor" viewBox="0 0 24 24">
                <path d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
              </svg>
              Out of 5 stars
            </p>
          </div>
          <div class="w-14 h-14 rounded-2xl bg-studio-graphite/50 flex items-center justify-center group-hover:bg-studio-gold/10 transition-all duration-300">
            <svg class="w-7 h-7 text-studio-gold group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
            </svg>
          </div>
        </div>
      </div>

      <!-- Total Reviewed -->
      <div
        class="stat-card rose group"
        :style="{
          opacity: mounted ? 1 : 0,
          transform: mounted ? 'translateY(0)' : 'translateY(20px)',
          transition: 'all 0.5s ease-out 0.2s'
        }"
      >
        <div class="flex items-start justify-between">
          <div>
            <p class="text-xs font-condensed text-studio-stone uppercase tracking-wider mb-2">Total Reviewed</p>
            <p class="text-4xl font-display font-semibold text-studio-cream">
              {{ reviewStats.reviewed }}
            </p>
            <p class="text-xs text-studio-stone mt-2 flex items-center gap-1">
              <svg class="w-3 h-3 text-studio-success" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
              Evaluated or published
            </p>
          </div>
          <div class="w-14 h-14 rounded-2xl bg-studio-graphite/50 flex items-center justify-center group-hover:bg-studio-rose-500/10 transition-all duration-300">
            <svg class="w-7 h-7 text-studio-rose-400 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div
      v-if="songsStore.loading"
      class="flex flex-col items-center justify-center py-20"
      :style="{
        opacity: mounted ? 1 : 0,
        transition: 'opacity 0.5s ease-out 0.1s'
      }"
    >
      <div class="relative w-20 h-20 mb-6">
        <div class="absolute inset-0 rounded-full border-4 border-studio-graphite/30"></div>
        <div class="absolute inset-0 rounded-full border-4 border-studio-gold border-t-transparent animate-spin"></div>
      </div>
      <p class="text-studio-sand animate-pulse-soft">Loading songs...</p>
    </div>

    <!-- Error State -->
    <div
      v-else-if="songsStore.error"
      class="card-static border-studio-error/30 bg-studio-error/5 text-center py-12"
      :style="{
        opacity: mounted ? 1 : 0,
        transform: mounted ? 'translateY(0)' : 'translateY(20px)',
        transition: 'all 0.5s ease-out 0.1s'
      }"
    >
      <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-studio-error/10 flex items-center justify-center">
        <svg class="w-8 h-8 text-studio-error" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      </div>
      <p class="text-studio-error font-semibold mb-4">{{ songsStore.error }}</p>
      <button @click="songsStore.fetchSongs()" class="btn btn-primary">Retry</button>
    </div>

    <!-- Empty State -->
    <div
      v-else-if="pendingSongs.length === 0"
      class="text-center py-20"
      :style="{
        opacity: mounted ? 1 : 0,
        transform: mounted ? 'translateY(0)' : 'translateY(20px)',
        transition: 'all 0.5s ease-out 0.1s'
      }"
    >
      <div class="w-24 h-24 mx-auto mb-6 rounded-full bg-studio-success/10 flex items-center justify-center">
        <svg class="w-12 h-12 text-studio-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <h3 class="text-2xl font-display font-semibold text-studio-cream mb-2">All Caught Up!</h3>
      <p class="text-studio-sand max-w-md mx-auto">No songs pending review at the moment. New songs will appear here once they've been generated.</p>
    </div>

    <!-- Song Cards Grid -->
    <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div
        v-for="(song, index) in pendingSongs"
        :key="song.id"
        class="card group"
        :class="{ 'opacity-50 pointer-events-none': submitting[song.id] }"
        :style="{
          opacity: mounted ? 1 : 0,
          transform: mounted ? 'translateY(0)' : 'translateY(20px)',
          transition: `all 0.5s ease-out ${0.1 + index * 0.08}s`
        }"
      >
        <!-- Header -->
        <div class="flex items-start justify-between mb-4">
          <div class="flex-1">
            <h3 class="text-xl font-display font-bold text-studio-cream mb-2 group-hover:text-studio-gold transition-colors">
              {{ song.title }}
            </h3>
            <div class="flex items-center gap-3 text-sm">
              <span class="px-3 py-1 rounded-lg bg-studio-bronze/20 text-studio-bronze font-semibold text-xs uppercase tracking-wider">
                {{ song.genre }}
              </span>
              <StatusBadge :status="song.status" />
            </div>
          </div>
        </div>

        <!-- Waveform Visualization -->
        <div class="mb-4 p-4 rounded-xl bg-studio-charcoal/30 border border-studio-charcoal/50">
          <div class="flex items-end justify-between gap-1 h-16">
            <div
              v-for="i in 24"
              :key="i"
              class="flex-1 rounded-sm bg-gradient-to-t from-studio-gold/40 to-studio-amber/60"
              :style="{
                height: `${20 + (i * 3) % 60 + 20}%`,
                opacity: 0.5 + ((i * 7) % 50) / 100
              }"
            />
          </div>
        </div>

        <!-- Style Prompt Preview -->
        <div class="mb-4">
          <label class="input-label mb-2">Style Prompt</label>
          <p class="text-sm text-studio-sand bg-studio-charcoal/30 border border-studio-charcoal/50 rounded-xl p-4">
            {{ truncateText(song.style_prompt) }}
          </p>
        </div>

        <!-- Star Rating -->
        <div class="mb-4">
          <label class="input-label mb-2">Quality Rating</label>
          <div class="flex items-center gap-1">
            <button
              v-for="star in 5"
              :key="star"
              @click="setRating(song.id, star)"
              class="text-3xl transition-all duration-200 hover:scale-110 focus:outline-none"
              :class="getRating(song.id) >= star ? 'text-studio-gold' : 'text-studio-slate/30 hover:text-studio-gold/50'"
            >
              <svg class="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
                <path d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
              </svg>
            </button>
            <span class="ml-3 text-sm text-studio-sand font-mono bg-studio-charcoal/50 px-3 py-1 rounded-lg">
              {{ getRating(song.id) }}/5
            </span>
          </div>
        </div>

        <!-- Notes (Optional) -->
        <div class="mb-6">
          <label class="input-label mb-2">Notes (Optional)</label>
          <textarea
            v-model="notes[song.id]"
            placeholder="Add review notes..."
            class="input-field resize-none h-20"
          />
        </div>

        <!-- Action Buttons -->
        <div class="flex gap-3">
          <button
            @click="approve(song)"
            class="btn-primary flex-1 flex items-center justify-center gap-2"
            :disabled="submitting[song.id]"
          >
            <span v-if="submitting[song.id]">Submitting...</span>
            <template v-else>
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              Approve
            </template>
          </button>
          <button
            @click="reject(song)"
            class="btn-danger flex-1 flex items-center justify-center gap-2"
            :disabled="submitting[song.id]"
          >
            <span v-if="submitting[song.id]">Submitting...</span>
            <template v-else>
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
              Reject
            </template>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
