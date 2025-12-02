<script setup lang="ts">
import { ref, computed } from 'vue'
import { api } from '@/api/client'

interface Variation {
  id: number
  variation_index: number
  status: string
  is_selected: boolean
  audio_path: string | null
  duration_seconds: number | null
  file_size_bytes: number | null
}

const props = defineProps<{
  songId: string
  songTitle: string
  variations: Variation[]
}>()

const emit = defineEmits<{
  (e: 'select', variationId: number, deleteOther: boolean): void
  (e: 'close'): void
}>()

// State
const deleteOther = ref(false)
const selecting = ref(false)
const playingVariationId = ref<number | null>(null)
const audioRefs = ref<Record<number, HTMLAudioElement | null>>({})

// Computed
const hasSelection = computed(() => props.variations.some(v => v.is_selected))

// Audio loading state per variation
const loadingAudio = ref<Record<number, boolean>>({})
const audioErrors = ref<Record<number, string>>({})
const audioBlobUrls = ref<Record<number, string | null>>({})

// Methods
function getAudioUrl(variation: Variation): string {
  return api.getVariationAudioUrl(props.songId, variation.id)
}

async function loadAudio(variation: Variation) {
  if (audioBlobUrls.value[variation.id]) return // Already loaded

  loadingAudio.value[variation.id] = true
  audioErrors.value[variation.id] = ''

  try {
    const token = localStorage.getItem('token')
    const response = await fetch(getAudioUrl(variation), {
      headers: token ? { Authorization: `Bearer ${token}` } : {}
    })

    if (!response.ok) {
      throw new Error(`Failed to load audio: ${response.status}`)
    }

    const blob = await response.blob()
    audioBlobUrls.value[variation.id] = URL.createObjectURL(blob)
  } catch (err: any) {
    console.error('Failed to load audio:', err)
    audioErrors.value[variation.id] = 'Failed to load audio'
  } finally {
    loadingAudio.value[variation.id] = false
  }
}

function formatFileSize(bytes: number | null): string {
  if (!bytes) return 'Unknown'
  const mb = bytes / (1024 * 1024)
  return `${mb.toFixed(1)} MB`
}

function formatDuration(seconds: number | null): string {
  if (!seconds) return 'Unknown'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

async function togglePlay(variation: Variation) {
  // Load audio if not loaded yet
  if (!audioBlobUrls.value[variation.id]) {
    await loadAudio(variation)
  }

  // Stop all other audio
  Object.entries(audioRefs.value).forEach(([id, audio]) => {
    if (audio && Number(id) !== variation.id) {
      audio.pause()
      audio.currentTime = 0
    }
  })

  const audio = audioRefs.value[variation.id]
  if (!audio) return

  if (playingVariationId.value === variation.id) {
    audio.pause()
    playingVariationId.value = null
  } else {
    audio.play()
    playingVariationId.value = variation.id
  }
}

async function selectVariation(variationId: number) {
  selecting.value = true
  try {
    emit('select', variationId, deleteOther.value)
  } finally {
    selecting.value = false
  }
}

// Cleanup blob URLs on unmount
function cleanup() {
  Object.values(audioBlobUrls.value).forEach(url => {
    if (url) URL.revokeObjectURL(url)
  })
}
</script>

<template>
  <div class="bg-studio-void/95 rounded-xl p-6 space-y-6 border border-studio-charcoal">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h3 class="font-display text-xl font-bold text-studio-cream">
        Compare Variations: {{ songTitle }}
      </h3>
      <button
        @click="emit('close')"
        class="text-studio-slate hover:text-studio-cream transition-colors p-1 rounded-lg hover:bg-studio-charcoal"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- Side-by-side variations -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div
        v-for="variation in variations"
        :key="variation.id"
        class="bg-studio-charcoal/50 rounded-xl p-5 border-2 transition-all"
        :class="[
          variation.is_selected
            ? 'border-emerald-500 ring-2 ring-emerald-500/30'
            : 'border-studio-charcoal hover:border-studio-slate/50'
        ]"
      >
        <!-- Variation Header -->
        <div class="flex items-center justify-between mb-4">
          <span class="font-display text-lg font-semibold text-studio-amber">
            Variation {{ variation.variation_index + 1 }}
          </span>
          <span
            v-if="variation.is_selected"
            class="px-3 py-1 bg-emerald-500/20 text-emerald-400 text-sm rounded-full font-medium"
          >
            Selected Winner
          </span>
        </div>

        <!-- Audio Player -->
        <div class="mb-4">
          <audio
            v-if="audioBlobUrls[variation.id]"
            :ref="el => audioRefs[variation.id] = el as HTMLAudioElement"
            :src="audioBlobUrls[variation.id]"
            @ended="playingVariationId = null"
            class="hidden"
          />

          <!-- Error State -->
          <div v-if="audioErrors[variation.id]" class="p-4 bg-red-500/10 rounded-lg text-center">
            <svg class="w-8 h-8 mx-auto mb-2 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
            </svg>
            <p class="text-red-400 text-sm">{{ audioErrors[variation.id] }}</p>
          </div>

          <!-- Audio Controls -->
          <div v-else class="flex items-center gap-4 p-4 bg-studio-void/50 rounded-lg">
            <button
              @click="togglePlay(variation)"
              :disabled="loadingAudio[variation.id]"
              class="w-12 h-12 rounded-full flex items-center justify-center transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
              :class="playingVariationId === variation.id
                ? 'bg-gradient-to-br from-amber-500 to-orange-500 text-white shadow-amber-500/30'
                : 'bg-studio-charcoal text-studio-cream hover:bg-studio-charcoal/80'"
            >
              <!-- Loading spinner -->
              <svg v-if="loadingAudio[variation.id]" class="w-6 h-6 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <!-- Play icon -->
              <svg v-else-if="playingVariationId !== variation.id" class="w-6 h-6 ml-1" fill="currentColor" viewBox="0 0 24 24">
                <path d="M8 5v14l11-7z"/>
              </svg>
              <!-- Pause icon -->
              <svg v-else class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z"/>
              </svg>
            </button>
            <div class="flex-1 space-y-1">
              <div class="text-sm text-studio-slate">
                Duration: <span class="text-studio-cream">{{ formatDuration(variation.duration_seconds) }}</span>
              </div>
              <div class="text-sm text-studio-slate">
                Size: <span class="text-studio-cream">{{ formatFileSize(variation.file_size_bytes) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Select Button -->
        <button
          v-if="!hasSelection && !audioErrors[variation.id]"
          @click="selectVariation(variation.id)"
          :disabled="selecting"
          class="w-full py-3 px-4 rounded-lg font-medium transition-all transform hover:scale-[1.02] disabled:hover:scale-100 shadow-lg"
          :class="selecting
            ? 'bg-studio-charcoal text-studio-slate cursor-not-allowed'
            : 'bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 text-white shadow-amber-500/30'"
        >
          {{ selecting ? 'Selecting...' : 'Select as Winner' }}
        </button>

        <!-- Already Selected -->
        <div v-else-if="variation.is_selected" class="w-full py-3 px-4 rounded-lg bg-emerald-500/20 text-emerald-400 text-center font-medium">
          Current Selection
        </div>
      </div>
    </div>

    <!-- Delete Other Option -->
    <div v-if="!hasSelection" class="flex items-center gap-3 p-4 bg-studio-charcoal/30 rounded-lg">
      <input
        type="checkbox"
        id="delete-other"
        v-model="deleteOther"
        class="w-4 h-4 rounded border-studio-charcoal bg-studio-void text-amber-500 focus:ring-amber-500 focus:ring-offset-0 cursor-pointer"
      />
      <label for="delete-other" class="text-sm text-studio-sand cursor-pointer select-none">
        Delete the other variation after selection (saves storage space)
      </label>
    </div>

    <!-- Info Note -->
    <div class="p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
      <div class="flex items-start gap-3">
        <svg class="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        <div>
          <p class="text-blue-300 text-sm font-medium mb-1">Comparison Tips</p>
          <p class="text-blue-400 text-sm">
            Listen to both variations carefully. Consider vocal quality, pacing, and overall production.
            The selected variation will be used for video generation and YouTube upload.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Custom checkbox styling */
input[type="checkbox"] {
  @apply appearance-none checked:bg-amber-500 checked:border-amber-500;
}

input[type="checkbox"]:checked {
  background-image: url("data:image/svg+xml,%3csvg viewBox='0 0 16 16' fill='white' xmlns='http://www.w3.org/2000/svg'%3e%3cpath d='M12.207 4.793a1 1 0 010 1.414l-5 5a1 1 0 01-1.414 0l-2-2a1 1 0 011.414-1.414L6.5 9.086l4.293-4.293a1 1 0 011.414 0z'/%3e%3c/svg%3e");
}
</style>
