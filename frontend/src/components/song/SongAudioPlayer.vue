<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'

const props = defineProps<{
  audioUrl: string
  title?: string
}>()

const audioElement = ref<HTMLAudioElement | null>(null)
const canvasElement = ref<HTMLCanvasElement | null>(null)
const isPlaying = ref(false)
const isLoading = ref(true)
const hasError = ref(false)
const errorMessage = ref('')
const currentTime = ref(0)
const duration = ref(0)
const volume = ref(1)
const isMuted = ref(false)
const audioBlobUrl = ref<string | null>(null)

// Audio context and analyzer for visualizations
let audioContext: AudioContext | null = null
let analyser: AnalyserNode | null = null
let source: MediaElementAudioSourceNode | null = null
let animationId: number | null = null

// Equalizer bars
const equalizerBars = ref<number[]>(Array(16).fill(5))

const formattedCurrentTime = computed(() => formatTime(currentTime.value))
const formattedDuration = computed(() => formatTime(duration.value))
const progress = computed(() => duration.value ? (currentTime.value / duration.value) * 100 : 0)

// Fetch audio with auth token
async function loadAudio() {
  isLoading.value = true
  hasError.value = false
  errorMessage.value = ''

  // Revoke previous blob URL
  if (audioBlobUrl.value) {
    URL.revokeObjectURL(audioBlobUrl.value)
    audioBlobUrl.value = null
  }

  try {
    const token = localStorage.getItem('token')
    const response = await fetch(props.audioUrl, {
      headers: token ? { Authorization: `Bearer ${token}` } : {}
    })

    if (!response.ok) {
      throw new Error(`Failed to load audio: ${response.status}`)
    }

    const blob = await response.blob()
    audioBlobUrl.value = URL.createObjectURL(blob)
  } catch (err: any) {
    console.error('Failed to load audio:', err)
    hasError.value = true
    errorMessage.value = 'Audio file not available'
    isLoading.value = false
  }
}

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

function setupAudioContext() {
  if (!audioElement.value || audioContext) return

  audioContext = new AudioContext()
  analyser = audioContext.createAnalyser()
  analyser.fftSize = 64
  source = audioContext.createMediaElementSource(audioElement.value)
  source.connect(analyser)
  analyser.connect(audioContext.destination)
}

function drawVisualizations() {
  if (!analyser || !canvasElement.value) return

  const canvas = canvasElement.value
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const bufferLength = analyser.frequencyBinCount
  const dataArray = new Uint8Array(bufferLength)
  analyser.getByteFrequencyData(dataArray)

  // Clear canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height)

  // Draw waveform bars
  const barWidth = canvas.width / bufferLength
  const barSpacing = 2

  for (let i = 0; i < bufferLength; i++) {
    const barHeight = (dataArray[i] / 255) * canvas.height * 0.9
    const x = i * (barWidth + barSpacing)

    // Gradient color based on height
    const gradient = ctx.createLinearGradient(0, canvas.height - barHeight, 0, canvas.height)
    gradient.addColorStop(0, '#f59e0b') // amber
    gradient.addColorStop(1, '#ea580c') // orange

    ctx.fillStyle = gradient
    ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight)
  }

  // Update equalizer bars
  const step = Math.floor(bufferLength / 16)
  for (let i = 0; i < 16; i++) {
    const value = dataArray[i * step] || 0
    equalizerBars.value[i] = Math.max(5, (value / 255) * 100)
  }

  animationId = requestAnimationFrame(drawVisualizations)
}

function stopVisualization() {
  if (animationId) {
    cancelAnimationFrame(animationId)
    animationId = null
  }
  // Reset equalizer bars
  equalizerBars.value = Array(16).fill(5)
}

async function togglePlay() {
  if (!audioElement.value || hasError.value) return

  if (isPlaying.value) {
    audioElement.value.pause()
    stopVisualization()
  } else {
    // Setup audio context on first play (required for browsers)
    if (!audioContext) {
      setupAudioContext()
    }
    if (audioContext?.state === 'suspended') {
      await audioContext.resume()
    }
    await audioElement.value.play()
    drawVisualizations()
  }
  isPlaying.value = !isPlaying.value
}

function seek(event: MouseEvent) {
  if (!audioElement.value || !duration.value) return

  const rect = (event.currentTarget as HTMLElement).getBoundingClientRect()
  const x = event.clientX - rect.left
  const percentage = x / rect.width
  audioElement.value.currentTime = percentage * duration.value
}

function toggleMute() {
  if (!audioElement.value) return
  isMuted.value = !isMuted.value
  audioElement.value.muted = isMuted.value
}

function setVolume(event: Event) {
  if (!audioElement.value) return
  const value = parseFloat((event.target as HTMLInputElement).value)
  volume.value = value
  audioElement.value.volume = value
  if (value === 0) {
    isMuted.value = true
  } else if (isMuted.value) {
    isMuted.value = false
    audioElement.value.muted = false
  }
}

function onTimeUpdate() {
  if (audioElement.value) {
    currentTime.value = audioElement.value.currentTime
  }
}

function onLoadedMetadata() {
  if (audioElement.value) {
    duration.value = audioElement.value.duration
    isLoading.value = false
    hasError.value = false
  }
}

function onCanPlay() {
  isLoading.value = false
  hasError.value = false
}

function onError() {
  isLoading.value = false
  hasError.value = true
  errorMessage.value = 'Audio file not available'
}

function onEnded() {
  isPlaying.value = false
  stopVisualization()
}

watch(() => props.audioUrl, () => {
  isPlaying.value = false
  currentTime.value = 0
  duration.value = 0
  stopVisualization()
  loadAudio()
})

onMounted(() => {
  if (canvasElement.value) {
    // Set canvas size
    const rect = canvasElement.value.getBoundingClientRect()
    canvasElement.value.width = rect.width
    canvasElement.value.height = rect.height
  }
  // Load audio with auth
  loadAudio()
})

onUnmounted(() => {
  stopVisualization()
  if (audioContext) {
    audioContext.close()
    audioContext = null
  }
  // Revoke blob URL
  if (audioBlobUrl.value) {
    URL.revokeObjectURL(audioBlobUrl.value)
  }
})
</script>

<template>
  <div class="audio-player">
    <!-- Hidden audio element with blob URL -->
    <audio
      v-if="audioBlobUrl"
      ref="audioElement"
      :src="audioBlobUrl"
      preload="metadata"
      @timeupdate="onTimeUpdate"
      @loadedmetadata="onLoadedMetadata"
      @canplay="onCanPlay"
      @error="onError"
      @ended="onEnded"
    ></audio>

    <!-- Error State -->
    <div v-if="hasError" class="text-center py-8">
      <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-red-500/10 flex items-center justify-center">
        <svg class="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
        </svg>
      </div>
      <p class="text-red-400 text-sm">{{ errorMessage }}</p>
    </div>

    <!-- Player Content -->
    <template v-else>
      <!-- Waveform visualization -->
      <div class="relative h-24 bg-studio-void/50 rounded-lg overflow-hidden mb-4">
        <canvas ref="canvasElement" class="w-full h-full"></canvas>

        <!-- Static waveform placeholder when not playing -->
        <div
          v-if="!isPlaying"
          class="absolute inset-0 flex items-end justify-center gap-1 pb-2"
        >
          <div
            v-for="i in 32"
            :key="i"
            class="w-1.5 bg-gradient-to-t from-amber-600/50 to-amber-500/30 rounded-full transition-all"
            :style="{ height: `${20 + Math.sin(i * 0.5) * 30 + Math.random() * 20}%` }"
          ></div>
        </div>
      </div>

      <!-- Equalizer bars (animated during playback) -->
      <div class="flex items-end justify-center gap-1 h-12 mb-4">
        <div
          v-for="(height, i) in equalizerBars"
          :key="i"
          class="w-2 rounded-full transition-all duration-75"
          :class="isPlaying ? 'bg-gradient-to-t from-amber-600 to-amber-400' : 'bg-studio-charcoal'"
          :style="{ height: `${height}%` }"
        ></div>
      </div>

      <!-- Progress bar -->
      <div
        class="h-2 bg-studio-charcoal rounded-full cursor-pointer overflow-hidden mb-3"
        @click="seek"
      >
        <div
          class="h-full bg-gradient-to-r from-amber-500 to-orange-500 transition-all duration-100"
          :style="{ width: `${progress}%` }"
        ></div>
      </div>

      <!-- Time display -->
      <div class="flex justify-between text-xs text-studio-slate mb-4">
        <span>{{ formattedCurrentTime }}</span>
        <span>{{ formattedDuration }}</span>
      </div>

      <!-- Controls -->
      <div class="flex items-center justify-between">
        <!-- Play/Pause button -->
        <button
          @click="togglePlay"
          :disabled="isLoading"
          class="w-14 h-14 rounded-full bg-gradient-to-br from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 text-white flex items-center justify-center transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-amber-500/30"
        >
          <svg v-if="isLoading" class="w-6 h-6 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <svg v-else-if="isPlaying" class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
            <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z"/>
          </svg>
          <svg v-else class="w-6 h-6 ml-1" fill="currentColor" viewBox="0 0 24 24">
            <path d="M8 5v14l11-7z"/>
          </svg>
        </button>

        <!-- Volume control -->
        <div class="flex items-center gap-3">
          <button
            @click="toggleMute"
            class="text-studio-slate hover:text-studio-cream transition-colors"
          >
            <svg v-if="isMuted || volume === 0" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2"/>
            </svg>
            <svg v-else-if="volume < 0.5" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072"/>
            </svg>
            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072M18.364 5.636a9 9 0 010 12.728"/>
            </svg>
          </button>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            :value="volume"
            @input="setVolume"
            class="w-24 h-1 bg-studio-charcoal rounded-full appearance-none cursor-pointer accent-amber-500"
          />
        </div>
      </div>

      <!-- Song title -->
      <div v-if="title" class="mt-4 text-center">
        <p class="text-studio-cream font-medium truncate">{{ title }}</p>
      </div>
    </template>
  </div>
</template>

<style scoped>
.audio-player {
  @apply bg-studio-charcoal/30 rounded-xl p-6;
}

input[type="range"]::-webkit-slider-thumb {
  @apply appearance-none w-3 h-3 rounded-full bg-amber-500 cursor-pointer;
}

input[type="range"]::-moz-range-thumb {
  @apply w-3 h-3 rounded-full bg-amber-500 cursor-pointer border-0;
}
</style>
