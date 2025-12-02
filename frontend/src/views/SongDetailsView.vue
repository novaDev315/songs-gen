<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/api/client'
import SongLyricsDisplay from '@/components/song/SongLyricsDisplay.vue'
import SongPipelineStatus from '@/components/song/SongPipelineStatus.vue'
import SongAudioPlayer from '@/components/song/SongAudioPlayer.vue'
import SongActions from '@/components/song/SongActions.vue'

const route = useRoute()
const router = useRouter()

const song = ref<any>(null)
const videoProject = ref<any>(null)
const isLoading = ref(true)
const error = ref<string | null>(null)
const isRegenerating = ref(false)

const songId = computed(() => route.params.id as string)

const hasAudio = computed(() => !!song.value?.audio_path)
const hasVideo = computed(() => !!videoProject.value?.output_path || !!videoProject.value?.preview_path)
const youtubeUrl = computed(() => videoProject.value?.youtube_url || null)

const audioUrl = computed(() => {
  if (!song.value?.audio_path) return null
  return `/api/v1/songs/${song.value.id}/audio`
})

const videoUrl = computed(() => {
  if (!videoProject.value) return null
  const path = videoProject.value.output_path || videoProject.value.preview_path
  if (!path) return null
  return `/api/v1${path}`
})

onMounted(async () => {
  await loadSongDetails()
})

async function loadSongDetails() {
  isLoading.value = true
  error.value = null

  try {
    // Load song and video project in parallel
    const [songData, projectData] = await Promise.all([
      api.getSong(songId.value),
      api.getSongVideoProject(songId.value)
    ])

    song.value = songData
    videoProject.value = projectData.video_project
  } catch (err: any) {
    console.error('Failed to load song details:', err)
    error.value = err.message || 'Failed to load song details'
  } finally {
    isLoading.value = false
  }
}

async function handleRegenerate() {
  if (!song.value || isRegenerating.value) return

  isRegenerating.value = true
  try {
    const result = await api.regenerateSongVideo(songId.value)
    // Refresh video project data
    const projectData = await api.getSongVideoProject(songId.value)
    videoProject.value = projectData.video_project
  } catch (err: any) {
    console.error('Failed to regenerate video:', err)
    error.value = err.message || 'Failed to start video regeneration'
  } finally {
    isRegenerating.value = false
  }
}

function goBack() {
  router.back()
}
</script>

<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="flex items-center gap-4">
      <button
        @click="goBack"
        class="p-2 rounded-lg bg-studio-charcoal hover:bg-studio-charcoal/80 text-studio-slate hover:text-studio-cream transition-colors"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
        </svg>
      </button>
      <div>
        <h1 class="font-display text-3xl font-bold text-studio-cream">
          {{ isLoading ? 'Loading...' : song?.title || 'Song Details' }}
        </h1>
        <p v-if="song?.genre" class="text-studio-sand font-body">{{ song.genre }}</p>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex items-center justify-center py-20">
      <div class="text-center">
        <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-studio-charcoal flex items-center justify-center">
          <div class="animate-spin w-8 h-8 border-3 border-studio-amber border-t-transparent rounded-full"></div>
        </div>
        <p class="text-studio-sand">Loading song details...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="card-static text-center py-16">
      <div class="w-20 h-20 mx-auto mb-4 rounded-full bg-red-500/10 flex items-center justify-center">
        <svg class="w-10 h-10 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
        </svg>
      </div>
      <p class="text-red-400 font-medium mb-2">Error Loading Song</p>
      <p class="text-sm text-studio-slate mb-4">{{ error }}</p>
      <button
        @click="loadSongDetails"
        class="px-4 py-2 bg-studio-amber text-studio-void rounded-lg hover:bg-studio-amber/90 transition-colors"
      >
        Retry
      </button>
    </div>

    <!-- Content -->
    <template v-else-if="song">
      <!-- Pipeline Status -->
      <SongPipelineStatus
        :status="song.status"
        :has-audio="hasAudio"
        :has-video="hasVideo"
        :youtube-url="youtubeUrl"
      />

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Left Column: Audio Player & Actions -->
        <div class="lg:col-span-1 space-y-6">
          <!-- Audio Player -->
          <div v-if="hasAudio && audioUrl">
            <h3 class="text-sm font-semibold text-studio-slate uppercase tracking-wider mb-3">Audio</h3>
            <SongAudioPlayer
              :audio-url="audioUrl"
              :title="song.title"
            />
          </div>

          <!-- No Audio State -->
          <div v-else class="bg-studio-charcoal/30 rounded-xl p-6 text-center">
            <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-studio-charcoal flex items-center justify-center">
              <svg class="w-8 h-8 text-studio-slate" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"/>
              </svg>
            </div>
            <p class="text-studio-slate text-sm">No audio available</p>
          </div>

          <!-- Actions -->
          <SongActions
            :song-id="song.id"
            :audio-url="audioUrl"
            :video-url="videoUrl"
            :youtube-url="youtubeUrl"
            :title="song.title"
            @regenerate="handleRegenerate"
          />
        </div>

        <!-- Right Column: Lyrics & Style -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Lyrics -->
          <div>
            <h3 class="text-sm font-semibold text-studio-slate uppercase tracking-wider mb-3">Lyrics</h3>
            <SongLyricsDisplay :lyrics="song.lyrics || ''" />
          </div>

          <!-- Style Prompt -->
          <div v-if="song.style_prompt" class="bg-studio-charcoal/30 rounded-xl p-6">
            <h3 class="text-sm font-semibold text-studio-slate uppercase tracking-wider mb-3">Style Prompt</h3>
            <p class="text-studio-cream leading-relaxed">{{ song.style_prompt }}</p>
          </div>

          <!-- Song Metadata -->
          <div class="bg-studio-charcoal/30 rounded-xl p-6">
            <h3 class="text-sm font-semibold text-studio-slate uppercase tracking-wider mb-4">Details</h3>
            <div class="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span class="text-studio-slate">Status</span>
                <p class="text-studio-cream capitalize mt-1">{{ song.status }}</p>
              </div>
              <div>
                <span class="text-studio-slate">Genre</span>
                <p class="text-studio-cream mt-1">{{ song.genre || 'Not specified' }}</p>
              </div>
              <div>
                <span class="text-studio-slate">Created</span>
                <p class="text-studio-cream mt-1">{{ song.created_at?.slice(0, 10) || 'Unknown' }}</p>
              </div>
              <div>
                <span class="text-studio-slate">Quality Score</span>
                <p class="text-studio-amber font-mono mt-1">{{ song.quality_score || 'N/A' }}</p>
              </div>
              <div v-if="videoProject">
                <span class="text-studio-slate">Video Status</span>
                <p class="text-studio-cream capitalize mt-1">{{ videoProject.status }}</p>
              </div>
              <div v-if="youtubeUrl">
                <span class="text-studio-slate">YouTube</span>
                <a
                  :href="youtubeUrl"
                  target="_blank"
                  class="text-studio-amber hover:text-studio-gold transition-colors mt-1 block truncate"
                >
                  View Video
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
