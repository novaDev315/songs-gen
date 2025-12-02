<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps<{
  songId: string
  audioUrl?: string | null
  videoUrl?: string | null
  youtubeUrl?: string | null
  title: string
}>()

const emit = defineEmits<{
  (e: 'regenerate'): void
}>()

const router = useRouter()
const isRegenerating = ref(false)

async function downloadAudio() {
  if (!props.audioUrl) return

  const a = document.createElement('a')
  a.href = props.audioUrl
  a.download = `${props.title}.mp3`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}

async function downloadVideo() {
  if (!props.videoUrl) return

  const a = document.createElement('a')
  a.href = props.videoUrl
  a.download = `${props.title}.mp4`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}

function openYouTube() {
  if (props.youtubeUrl) {
    window.open(props.youtubeUrl, '_blank')
  }
}

async function regenerateVideo() {
  isRegenerating.value = true
  emit('regenerate')
  // Parent component handles the regeneration
}

function editInStudio() {
  // Navigate to studio with this song preloaded
  router.push({
    name: 'studio',
    query: { songId: props.songId }
  })
}
</script>

<template>
  <div class="actions-container">
    <h3 class="text-sm font-semibold text-studio-slate uppercase tracking-wider mb-4">Actions</h3>

    <div class="grid grid-cols-2 gap-3">
      <!-- Download Audio -->
      <button
        @click="downloadAudio"
        :disabled="!audioUrl"
        class="action-button"
        :class="audioUrl ? 'action-button-primary' : 'action-button-disabled'"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
        </svg>
        <span>Audio</span>
      </button>

      <!-- Download Video -->
      <button
        @click="downloadVideo"
        :disabled="!videoUrl"
        class="action-button"
        :class="videoUrl ? 'action-button-primary' : 'action-button-disabled'"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/>
        </svg>
        <span>Video</span>
      </button>

      <!-- View on YouTube -->
      <button
        @click="openYouTube"
        :disabled="!youtubeUrl"
        class="action-button"
        :class="youtubeUrl ? 'action-button-youtube' : 'action-button-disabled'"
      >
        <svg class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
          <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
        </svg>
        <span>YouTube</span>
      </button>

      <!-- Regenerate Video -->
      <button
        @click="regenerateVideo"
        :disabled="!audioUrl || isRegenerating"
        class="action-button"
        :class="audioUrl && !isRegenerating ? 'action-button-warning' : 'action-button-disabled'"
      >
        <svg v-if="isRegenerating" class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
        </svg>
        <span>{{ isRegenerating ? 'Regenerating...' : 'Regenerate' }}</span>
      </button>
    </div>

    <!-- Edit in Studio (full width) -->
    <button
      @click="editInStudio"
      class="action-button action-button-studio w-full mt-3"
    >
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
      </svg>
      <span>Edit in Studio</span>
    </button>
  </div>
</template>

<style scoped>
.actions-container {
  @apply bg-studio-charcoal/30 rounded-xl p-6;
}

.action-button {
  @apply flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-medium transition-all duration-200;
}

.action-button-primary {
  @apply bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/20;
}

.action-button-youtube {
  @apply bg-red-600 hover:bg-red-500 text-white shadow-lg shadow-red-600/20;
}

.action-button-warning {
  @apply bg-amber-600 hover:bg-amber-500 text-white shadow-lg shadow-amber-600/20;
}

.action-button-studio {
  @apply bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white shadow-lg shadow-purple-600/20;
}

.action-button-disabled {
  @apply bg-studio-charcoal text-studio-slate cursor-not-allowed opacity-50;
}
</style>
