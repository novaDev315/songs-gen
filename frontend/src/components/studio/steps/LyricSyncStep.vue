<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useStudioStore } from '@/stores/studio'
import { api } from '@/api/client'

const store = useStudioStore()
const isSyncing = ref(false)
const syncProgress = ref(0)
const syncStatus = ref('')
const syncError = ref<string | null>(null)
const syncMode = ref<'beat_synced' | 'uniform' | 'word_level'>('word_level')

const syncModes = [
  { id: 'word_level', name: 'Word Level', description: 'Individual word timing (best for karaoke)', icon: 'M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z' },
  { id: 'beat_synced', name: 'Beat Synced', description: 'Sync to music beats', icon: 'M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3' },
  { id: 'uniform', name: 'Uniform', description: 'Even distribution of lyrics', icon: 'M4 6h16M4 10h16M4 14h16M4 18h16' },
]

const hasWordTiming = computed(() => {
  return store.video.wordTiming && store.video.wordTiming.length > 0
})

const hasLineTiming = computed(() => {
  return store.lyricTiming && store.lyricTiming.length > 0
})

const hasTiming = computed(() => hasWordTiming.value || hasLineTiming.value)

const timingPreview = computed(() => {
  if (hasWordTiming.value) {
    return store.video.wordTiming?.slice(0, 20) || []
  }
  return store.lyricTiming?.slice(0, 10) || []
})

const lyrics = computed(() => store.selectedSong?.lyrics || '')
const lyricLines = computed(() => lyrics.value.split('\n').filter(l => l.trim()))

const progressSteps = [
  { threshold: 10, label: 'Loading audio' },
  { threshold: 25, label: 'Analyzing waveform' },
  { threshold: 40, label: 'Detecting beats' },
  { threshold: 55, label: 'Processing lyrics' },
  { threshold: 70, label: 'Calculating timing' },
  { threshold: 85, label: 'Generating timestamps' },
  { threshold: 100, label: 'Finalizing' },
]

async function syncLyrics() {
  if (!store.projectId || !store.selectedSong) return

  isSyncing.value = true
  syncProgress.value = 0
  syncStatus.value = 'Initializing...'
  syncError.value = null

  const animationSteps = [
    { progress: 10, status: 'Loading audio file...' },
    { progress: 25, status: 'Analyzing audio waveform...' },
    { progress: 40, status: 'Detecting beats and rhythm...' },
    { progress: 55, status: 'Processing lyrics...' },
    { progress: 70, status: 'Calculating timing...' },
    { progress: 85, status: 'Generating timestamps...' },
  ]

  let stepIndex = 0
  const progressInterval = setInterval(() => {
    if (stepIndex < animationSteps.length) {
      syncProgress.value = animationSteps[stepIndex].progress
      syncStatus.value = animationSteps[stepIndex].status
      stepIndex++
    }
  }, 800)

  try {
    const response = await api.post(`/studio/projects/${store.projectId}/lyrics/sync`, {
      mode: syncMode.value
    })

    clearInterval(progressInterval)
    syncProgress.value = 100
    syncStatus.value = 'Complete!'

    if (response.word_timing) {
      store.video.wordTiming = response.word_timing
    }
    if (response.timing) {
      store.lyricTiming = response.timing
    }

    await store.updateProject()

    setTimeout(() => {
      isSyncing.value = false
    }, 1000)
  } catch (e: any) {
    clearInterval(progressInterval)
    console.error('Sync failed:', e)
    syncError.value = e.message || 'Failed to sync lyrics'
    isSyncing.value = false
  }
}

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = (seconds % 60).toFixed(2)
  return `${mins}:${secs.padStart(5, '0')}`
}
</script>

<template>
  <div class="space-y-6">
    <!-- Step Header -->
    <div>
      <div class="flex items-center gap-2 mb-2">
        <div class="led-indicator amber"></div>
        <span class="text-xs font-condensed text-studio-stone uppercase tracking-widest">Audio Sync</span>
      </div>
      <h2 class="text-xl font-display font-semibold text-studio-cream">Lyric Synchronization</h2>
      <p class="text-sm text-studio-sand mt-1">Sync lyrics to audio for karaoke-style videos</p>
    </div>

    <!-- Song Info Card -->
    <div class="stat-card amber">
      <div class="flex items-center gap-4">
        <div class="w-14 h-14 rounded-xl bg-studio-amber/20 flex items-center justify-center">
          <svg class="w-7 h-7 text-studio-amber" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
          </svg>
        </div>
        <div class="flex-1">
          <p class="text-xs font-condensed text-studio-stone uppercase tracking-wider">Selected Track</p>
          <p class="text-lg font-display font-semibold text-studio-cream">{{ store.selectedSong?.title }}</p>
          <p class="text-sm text-studio-sand">{{ lyricLines.length }} lines of lyrics</p>
        </div>
      </div>
    </div>

    <!-- Sync Mode Selection -->
    <div class="space-y-4">
      <div class="flex items-center gap-2">
        <div class="w-1.5 h-1.5 rounded-full bg-studio-rose-500"></div>
        <h3 class="text-sm font-condensed text-studio-sand uppercase tracking-wider">Sync Mode</h3>
      </div>

      <div class="grid gap-3 md:grid-cols-3">
        <button
          v-for="mode in syncModes"
          :key="mode.id"
          @click="syncMode = mode.id as any"
          :disabled="isSyncing"
          class="group relative p-4 rounded-xl text-left transition-all duration-300 border disabled:opacity-50 disabled:cursor-not-allowed"
          :class="[
            syncMode === mode.id
              ? 'bg-studio-rose-500/10 border-studio-rose-500/50'
              : 'bg-studio-charcoal/30 border-studio-graphite/40 hover:bg-studio-charcoal/50 hover:border-studio-rose-500/20'
          ]"
        >
          <div v-if="syncMode === mode.id" class="absolute top-2 right-2">
            <div class="led-indicator rose"></div>
          </div>

          <div class="w-10 h-10 rounded-lg mb-3 flex items-center justify-center"
            :class="[
              syncMode === mode.id
                ? 'bg-studio-rose-500/20'
                : 'bg-studio-graphite/50'
            ]"
          >
            <svg class="w-5 h-5" :class="syncMode === mode.id ? 'text-studio-rose-400' : 'text-studio-slate'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" :d="mode.icon" />
            </svg>
          </div>
          <div class="font-medium text-studio-cream text-sm">{{ mode.name }}</div>
          <div class="text-xs text-studio-stone mt-0.5">{{ mode.description }}</div>
        </button>
      </div>
    </div>

    <!-- Sync Button -->
    <button
      @click="syncLyrics"
      :disabled="isSyncing || !store.projectId"
      class="btn btn-primary w-full btn-lg"
      :class="{ 'opacity-75 cursor-wait': isSyncing }"
    >
      <svg v-if="isSyncing" class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
      {{ isSyncing ? 'Synchronizing...' : (hasTiming ? 'Re-sync Lyrics' : 'Sync Lyrics to Audio') }}
    </button>

    <!-- Progress Visualization -->
    <div v-if="isSyncing" class="space-y-4">
      <div class="flex justify-between items-center text-sm">
        <span class="text-studio-sand">{{ syncStatus }}</span>
        <span class="text-studio-rose-400 font-mono font-medium">{{ syncProgress }}%</span>
      </div>

      <!-- VU Meter Progress -->
      <div class="vu-meter">
        <div class="vu-meter-fill" :style="{ width: syncProgress + '%' }"></div>
      </div>

      <!-- Step Indicators -->
      <div class="space-y-2">
        <div
          v-for="step in progressSteps"
          :key="step.threshold"
          class="flex items-center gap-3 text-sm"
          :class="syncProgress >= step.threshold ? 'text-studio-success' : 'text-studio-slate'"
        >
          <div class="w-5 h-5 rounded-full flex items-center justify-center"
            :class="syncProgress >= step.threshold ? 'bg-studio-success/20' : 'bg-studio-graphite/30'"
          >
            <svg v-if="syncProgress >= step.threshold" class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <div v-else class="w-1.5 h-1.5 rounded-full bg-studio-slate"></div>
          </div>
          <span>{{ step.label }}</span>
        </div>
      </div>
    </div>

    <!-- Info text when not syncing -->
    <p v-if="!isSyncing && !hasTiming" class="text-center text-studio-stone text-sm">
      This analyzes your audio and generates timestamps for each {{ syncMode === 'word_level' ? 'word' : 'line' }}
    </p>

    <!-- Error Alert -->
    <div v-if="syncError" class="stat-card rose">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 rounded-xl bg-studio-error/20 flex items-center justify-center">
          <svg class="w-6 h-6 text-studio-error" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <div class="flex-1">
          <p class="font-medium text-studio-error">Sync Failed</p>
          <p class="text-sm text-studio-error/80">{{ syncError }}</p>
        </div>
        <button @click="syncError = null" class="btn-ghost p-2 text-studio-error hover:text-studio-cream">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Timing Preview -->
    <div v-if="hasTiming && !isSyncing" class="space-y-4">
      <div class="flex items-center gap-2">
        <div class="w-1.5 h-1.5 rounded-full bg-studio-success"></div>
        <h3 class="text-sm font-condensed text-studio-sand uppercase tracking-wider">Timing Preview</h3>
      </div>

      <div class="card-static max-h-64 overflow-y-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="text-studio-stone text-left border-b border-studio-graphite/50">
              <th class="pb-3 pr-4 font-condensed uppercase tracking-wider text-xs">{{ hasWordTiming ? 'Word' : 'Line' }}</th>
              <th class="pb-3 pr-4 font-condensed uppercase tracking-wider text-xs">Start</th>
              <th class="pb-3 font-condensed uppercase tracking-wider text-xs">End</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(item, idx) in timingPreview"
              :key="idx"
              class="border-b border-studio-graphite/30 last:border-0"
            >
              <td class="py-2.5 pr-4 text-studio-cream">
                {{ (item as any).word || (item as any).text || 'N/A' }}
              </td>
              <td class="py-2.5 pr-4 text-studio-success font-mono text-xs">
                {{ formatTime((item as any).start_time || (item as any).start || 0) }}
              </td>
              <td class="py-2.5 text-studio-amber font-mono text-xs">
                {{ formatTime((item as any).end_time || (item as any).end || 0) }}
              </td>
            </tr>
          </tbody>
        </table>
        <p v-if="timingPreview.length >= 10" class="text-studio-slate text-xs mt-3 text-center">
          Showing first {{ timingPreview.length }} items...
        </p>
      </div>
    </div>

    <!-- Success Message -->
    <div v-if="hasTiming && !isSyncing" class="stat-card gold">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 rounded-xl bg-studio-success/20 flex items-center justify-center">
          <svg class="w-6 h-6 text-studio-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <div>
          <p class="font-medium text-studio-success">Lyrics Synchronized!</p>
          <p class="text-sm text-studio-success/80">
            {{ hasWordTiming ? `${store.video.wordTiming?.length || 0} words` : `${store.lyricTiming?.length || 0} lines` }} timed to audio
          </p>
        </div>
      </div>
    </div>

    <!-- Tip -->
    <div v-if="!hasTiming && !isSyncing" class="text-center">
      <p class="text-studio-stone text-xs">
        Tip: For best karaoke results, select "Word Level" mode before syncing
      </p>
    </div>
  </div>
</template>
