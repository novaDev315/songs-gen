<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useSongsStore } from '@/stores/songs'
import { api } from '@/api/client'

const store = useSongsStore()
const ratings = ref<Record<string, number>>({})
const submitting = ref<string | null>(null)

onMounted(() => { store.fetchSongs() })

// Defensive: ensure songs is always an array
const safeSongs = computed(() => Array.isArray(store.songs) ? store.songs : [])
const pendingReview = computed(() => safeSongs.value.filter(s => s.status === 'downloaded' || s.status === 'pending'))

async function submitReview(songId: string, approved: boolean) {
  submitting.value = songId
  try {
    await api.submitEvaluation(songId, { approved, rating: ratings.value[songId] || 3 })
    await store.fetchSongs()
  } catch (e) {
    alert('Failed to submit review')
  } finally {
    submitting.value = null
  }
}
</script>

<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
      <div>
        <h1 class="font-display text-4xl font-bold text-studio-cream mb-2">Review</h1>
        <p class="text-studio-sand font-body">Review and approve generated songs before publishing</p>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
      <div class="stat-card amber">
        <p class="text-xs font-condensed text-studio-slate uppercase tracking-wider mb-1">Pending Review</p>
        <p class="text-3xl font-display font-bold text-studio-cream">{{ pendingReview.length }}</p>
      </div>
      <div class="stat-card gold">
        <p class="text-xs font-condensed text-studio-slate uppercase tracking-wider mb-1">Avg Rating</p>
        <p class="text-3xl font-display font-bold text-studio-cream">4.2</p>
      </div>
      <div class="stat-card bronze">
        <p class="text-xs font-condensed text-studio-slate uppercase tracking-wider mb-1">Reviewed Today</p>
        <p class="text-3xl font-display font-bold text-studio-cream">12</p>
      </div>
    </div>

    <!-- Review Cards -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div v-for="song in pendingReview" :key="song.id" class="card-static group">
        <!-- Header -->
        <div class="flex items-start justify-between mb-5">
          <div>
            <h3 class="font-display text-xl font-bold text-studio-cream group-hover:text-studio-amber transition-colors">{{ song.title }}</h3>
            <div class="flex items-center gap-2 mt-2">
              <span class="px-3 py-1 text-xs font-mono rounded-sm bg-studio-charcoal text-studio-sand">{{ song.genre }}</span>
              <div :class="['status-badge', `status-${song.status}`]">{{ song.status }}</div>
            </div>
          </div>
          <!-- Mini vinyl decoration -->
          <div class="w-16 h-16 rounded-full flex-shrink-0 group-hover:animate-spin-slow" style="background: repeating-radial-gradient(circle at center, #141210 0px, #141210 1px, #1c1917 1px, #1c1917 2px);">
            <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-5 h-5 rounded-full bg-studio-amber/60"></div>
          </div>
        </div>

        <!-- Waveform visualization -->
        <div class="h-20 flex items-end gap-0.5 mb-5 p-3 rounded-lg bg-studio-black/50">
          <div 
            v-for="i in 32" 
            :key="i" 
            class="flex-1 rounded-t-sm transition-all"
            :style="{ 
              height: Math.random() * 100 + '%',
              background: 'linear-gradient(to top, #d4a574, #c9a227)'
            }"
          />
        </div>

        <!-- Style prompt preview -->
        <p class="text-sm text-studio-slate mb-5 line-clamp-2 font-mono">{{ song.style_prompt || 'No style prompt available' }}</p>

        <!-- Rating -->
        <div class="mb-5">
          <label class="text-xs font-condensed text-studio-slate uppercase tracking-wider mb-3 block">Quality Rating</label>
          <div class="flex gap-2">
            <button 
              v-for="star in 5" 
              :key="star" 
              @click="ratings[song.id] = star"
              class="text-3xl transition-all duration-200 hover:scale-110"
              :class="(ratings[song.id] || 0) >= star ? 'text-studio-gold' : 'text-studio-charcoal hover:text-studio-gold/50'"
            >
              ★
            </button>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex gap-3">
          <button 
            @click="submitReview(song.id, true)" 
            :disabled="submitting === song.id"
            class="btn-primary flex-1 flex items-center justify-center gap-2"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            {{ submitting === song.id ? 'Processing...' : 'Approve' }}
          </button>
          <button 
            @click="submitReview(song.id, false)" 
            :disabled="submitting === song.id"
            class="btn-danger flex-1 flex items-center justify-center gap-2"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            Reject
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="!pendingReview.length" class="card-static text-center py-16">
      <div class="w-24 h-24 mx-auto mb-4 rounded-full bg-studio-charcoal/50 flex items-center justify-center">
        <svg class="w-12 h-12 text-studio-amber" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
        </svg>
      </div>
      <p class="text-studio-cream font-medium text-lg mb-2">All caught up!</p>
      <p class="text-studio-slate">No songs pending review at the moment</p>
    </div>
  </div>
</template>
