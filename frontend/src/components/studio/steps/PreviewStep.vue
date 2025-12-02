<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useStudioStore } from '@/stores/studio'
import { api } from '@/api/client'

const store = useStudioStore()
const isGenerating = ref(false)
const generationProgress = ref(0)
const generationStatus = ref('')
const videoUrl = ref<string | null>(null)
const videoElement = ref<HTMLVideoElement | null>(null)
const isPlaying = ref(false)
const errorMessage = ref<string | null>(null)
const isCheckingStatus = ref(true)
const videoDuration = ref('--:--')
const videoFileSize = ref('Calculating...')
let statusInterval: number | null = null

const canGenerate = computed(() => {
  return store.projectId && store.selectedSong && (store.cover.path || store.cover.type === 'skip')
})

const progressSteps = [
  { threshold: 10, label: 'Loading audio' },
  { threshold: 30, label: 'Processing cover art' },
  { threshold: 50, label: 'Rendering visuals' },
  { threshold: 80, label: 'Encoding video' },
  { threshold: 100, label: 'Finalizing' },
]

onMounted(async () => {
  await checkProjectStatus()
})

onUnmounted(() => {
  if (statusInterval) {
    clearInterval(statusInterval)
  }
})

async function checkProjectStatus() {
  if (!store.projectId) {
    isCheckingStatus.value = false
    return
  }

  try {
    const response = await api.get(`/studio/projects/${store.projectId}`)

    if (response.preview_path) {
      const cacheBuster = response.updated_at ? new Date(response.updated_at).getTime() : Date.now()
      videoUrl.value = '/api/v1' + response.preview_path + '?t=' + cacheBuster
      store.previewUrl = response.preview_path
      isCheckingStatus.value = false
      return
    }

    if (response.status === 'generating' || response.status === 'processing' || response.status === 'rendering') {
      isGenerating.value = true
      generationProgress.value = response.progress || 10
      generationStatus.value = 'Resuming video generation...'
      trackProgress()
      isCheckingStatus.value = false
      return
    }

    if (response.status === 'failed') {
      errorMessage.value = response.error_message || 'Previous generation failed. Please try again.'
    }
  } catch (error: any) {
    console.error('Error checking project status:', error)
  }

  isCheckingStatus.value = false
}

async function generateVideo() {
  if (!canGenerate.value || !store.projectId) return

  isGenerating.value = true
  generationProgress.value = 0
  generationStatus.value = 'Starting video generation...'
  errorMessage.value = null

  try {
    await api.post(`/studio/projects/${store.projectId}/preview`)
    trackProgress()
  } catch (error: any) {
    console.error('Video generation failed:', error)
    generationStatus.value = 'Generation failed'
    errorMessage.value = error.message || 'Failed to start video generation'
    isGenerating.value = false
  }
}

async function trackProgress() {
  statusInterval = window.setInterval(async () => {
    try {
      const response = await api.get(`/studio/projects/${store.projectId}`)

      if (response.preview_path) {
        if (statusInterval) clearInterval(statusInterval)
        isGenerating.value = false
        generationProgress.value = 100
        generationStatus.value = 'Video ready!'
        const cacheBuster = response.updated_at ? new Date(response.updated_at).getTime() : Date.now()
        videoUrl.value = '/api/v1' + response.preview_path + '?t=' + cacheBuster
        store.previewUrl = response.preview_path
      } else if (response.status === 'generating' || response.status === 'processing' || response.status === 'rendering') {
        generationProgress.value = response.progress || Math.min(generationProgress.value + 5, 90)
        generationStatus.value = response.status_message || 'Generating video...'
      } else if (response.status === 'failed') {
        if (statusInterval) clearInterval(statusInterval)
        isGenerating.value = false
        generationStatus.value = 'Generation failed'
        errorMessage.value = response.error_message || 'Unknown error'
      }
    } catch (error: any) {
      console.error('Error checking status:', error)
    }
  }, 2000)

  setTimeout(() => {
    if (statusInterval && isGenerating.value) {
      clearInterval(statusInterval)
      isGenerating.value = false
      errorMessage.value = 'Generation timed out. Please try again.'
    }
  }, 300000)
}

function togglePlay() {
  if (!videoElement.value) return

  if (isPlaying.value) {
    videoElement.value.pause()
  } else {
    videoElement.value.play()
  }
  isPlaying.value = !isPlaying.value
}

function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

function onVideoLoaded() {
  if (videoElement.value) {
    videoDuration.value = formatDuration(videoElement.value.duration)
  }
  if (videoUrl.value) {
    fetch(videoUrl.value, { method: 'HEAD' })
      .then(response => {
        const size = response.headers.get('content-length')
        if (size) {
          const mb = (parseInt(size) / (1024 * 1024)).toFixed(2)
          videoFileSize.value = `${mb} MB`
        }
      })
      .catch(() => {
        videoFileSize.value = 'Unknown'
      })
  }
}

async function regenerate() {
  if (confirm('Are you sure you want to regenerate the video? This will replace the current version.')) {
    videoUrl.value = null
    store.previewUrl = null
    await generateVideo()
  }
}

async function downloadVideo() {
  if (!videoUrl.value) return

  const a = document.createElement('a')
  a.href = videoUrl.value
  a.download = `${store.selectedSong?.title || 'video'}.mp4`
  a.click()
}
</script>

<template>
  <div class="space-y-6">
    <!-- Step Header -->
    <div>
      <div class="flex items-center gap-2 mb-2">
        <div class="led-indicator violet"></div>
        <span class="text-xs font-condensed text-studio-stone uppercase tracking-widest">Video Preview</span>
      </div>
      <h2 class="text-xl font-display font-semibold text-studio-cream">Preview Video</h2>
      <p class="text-sm text-studio-sand mt-1">Generate and preview before publishing</p>
    </div>

    <!-- Video Settings Summary -->
    <div class="stat-card violet">
      <div class="flex items-center gap-2 mb-4">
        <div class="led-indicator amber"></div>
        <h3 class="text-sm font-condensed text-studio-sand uppercase tracking-wider">Configuration</h3>
      </div>
      <div class="grid gap-3 md:grid-cols-2 text-sm">
        <div class="flex items-center justify-between py-1.5">
          <span class="text-studio-stone">Song</span>
          <span class="text-studio-cream truncate ml-2">{{ store.selectedSong?.title }}</span>
        </div>
        <div class="flex items-center justify-between py-1.5">
          <span class="text-studio-stone">Visual Style</span>
          <span class="text-studio-cream capitalize">{{ store.videoSettings.visualStyle?.replace(/_/g, ' ') }}</span>
        </div>
        <div class="flex items-center justify-between py-1.5">
          <span class="text-studio-stone">Color Theme</span>
          <span class="text-studio-cream capitalize">{{ store.videoSettings.colorTheme?.replace(/_/g, ' ') }}</span>
        </div>
        <div class="flex items-center justify-between py-1.5">
          <span class="text-studio-stone">Quality</span>
          <span class="text-studio-cream">{{ store.videoSettings.highQuality ? '1080p' : '720p' }}</span>
        </div>
        <div class="flex items-center justify-between py-1.5">
          <span class="text-studio-stone">Cover Art</span>
          <span class="text-studio-cream capitalize">{{ store.cover.type === 'skip' ? 'Default' : store.cover.type }}</span>
        </div>
        <div class="flex items-center justify-between py-1.5">
          <span class="text-studio-stone">Title Overlay</span>
          <span class="text-studio-cream">{{ store.videoSettings.showTitle ? 'Yes' : 'No' }}</span>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isCheckingStatus" class="text-center py-12">
      <div class="relative w-16 h-16 mx-auto mb-4">
        <div class="absolute inset-0 rounded-full border-4 border-studio-graphite/30"></div>
        <div class="absolute inset-0 rounded-full border-4 border-studio-rose-500 border-t-transparent animate-spin"></div>
      </div>
      <p class="text-studio-sand">Checking video status...</p>
    </div>

    <!-- Error Message -->
    <div v-if="errorMessage && !isCheckingStatus" class="stat-card rose">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 rounded-xl bg-studio-error/20 flex items-center justify-center">
          <svg class="w-6 h-6 text-studio-error" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <div class="flex-1">
          <p class="font-medium text-studio-error">Error</p>
          <p class="text-sm text-studio-error/80">{{ errorMessage }}</p>
        </div>
        <button @click="errorMessage = null" class="btn-ghost p-2 text-studio-error hover:text-studio-cream">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Generate Button -->
    <div v-if="!videoUrl && !isGenerating && !isCheckingStatus" class="text-center py-8">
      <button
        @click="generateVideo"
        :disabled="!canGenerate"
        class="btn btn-primary btn-lg"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
        Generate Video
      </button>
      <p class="text-studio-stone text-sm mt-4">This may take 1-3 minutes depending on song length</p>
      <p v-if="!canGenerate" class="text-studio-warning text-sm mt-2">
        Please complete previous steps first (select song and cover)
      </p>
    </div>

    <!-- Generation Progress -->
    <div v-if="isGenerating && !isCheckingStatus" class="py-6 space-y-6">
      <div class="text-center">
        <div class="relative w-20 h-20 mx-auto mb-4">
          <div class="absolute inset-0 rounded-full border-4 border-studio-graphite/30"></div>
          <div class="absolute inset-0 rounded-full border-4 border-studio-rose-500 border-t-transparent animate-spin"></div>
          <div class="absolute inset-0 flex items-center justify-center">
            <span class="text-lg font-display font-semibold text-studio-cream">{{ generationProgress }}%</span>
          </div>
        </div>
        <h3 class="text-lg font-display font-semibold text-studio-cream">{{ generationStatus }}</h3>
      </div>

      <!-- VU Meter Progress -->
      <div class="vu-meter">
        <div class="vu-meter-fill" :style="{ width: generationProgress + '%' }"></div>
      </div>

      <!-- Step Indicators -->
      <div class="space-y-2">
        <div
          v-for="step in progressSteps"
          :key="step.threshold"
          class="flex items-center gap-3 text-sm"
          :class="generationProgress >= step.threshold ? 'text-studio-success' : 'text-studio-slate'"
        >
          <div class="w-5 h-5 rounded-full flex items-center justify-center"
            :class="generationProgress >= step.threshold ? 'bg-studio-success/20' : 'bg-studio-graphite/30'"
          >
            <svg v-if="generationProgress >= step.threshold" class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <div v-else class="w-1.5 h-1.5 rounded-full bg-studio-slate"></div>
          </div>
          <span>{{ step.label }}</span>
        </div>
      </div>

      <!-- Info Box -->
      <div class="p-4 rounded-xl bg-studio-info/10 border border-studio-info/30">
        <p class="text-studio-info text-sm flex items-center gap-2">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          You can navigate away. Video generation continues on the server.
        </p>
      </div>
    </div>

    <!-- Video Player -->
    <div v-if="videoUrl && !isCheckingStatus" class="space-y-6">
      <div class="relative rounded-xl overflow-hidden bg-studio-black border border-studio-graphite/40">
        <video
          ref="videoElement"
          :src="videoUrl"
          class="w-full"
          controls
          @play="isPlaying = true"
          @pause="isPlaying = false"
          @loadedmetadata="onVideoLoaded"
        ></video>
      </div>

      <!-- Video Actions -->
      <div class="flex flex-wrap gap-3">
        <button @click="togglePlay" class="btn btn-secondary">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path v-if="isPlaying" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
          </svg>
          {{ isPlaying ? 'Pause' : 'Play' }}
        </button>
        <button @click="downloadVideo" class="btn btn-secondary">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Download
        </button>
        <button @click="regenerate" class="btn btn-ghost">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Regenerate
        </button>
      </div>

      <!-- Video Info -->
      <div class="stat-card gold">
        <div class="flex items-center gap-2 mb-4">
          <div class="led-indicator green"></div>
          <h3 class="text-sm font-condensed text-studio-sand uppercase tracking-wider">Video Info</h3>
        </div>
        <div class="grid gap-2 md:grid-cols-2 text-sm">
          <div class="flex items-center justify-between py-1.5">
            <span class="text-studio-stone">Duration</span>
            <span class="text-studio-cream font-mono">{{ videoDuration }}</span>
          </div>
          <div class="flex items-center justify-between py-1.5">
            <span class="text-studio-stone">Resolution</span>
            <span class="text-studio-cream">{{ store.videoSettings.highQuality ? '1920x1080' : '1280x720' }}</span>
          </div>
          <div class="flex items-center justify-between py-1.5">
            <span class="text-studio-stone">Format</span>
            <span class="text-studio-cream">MP4 (H.264)</span>
          </div>
          <div class="flex items-center justify-between py-1.5">
            <span class="text-studio-stone">File Size</span>
            <span class="text-studio-cream">{{ videoFileSize }}</span>
          </div>
        </div>
      </div>

      <!-- Success Message -->
      <div class="stat-card gold">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-xl bg-studio-success/20 flex items-center justify-center">
            <svg class="w-6 h-6 text-studio-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <div>
            <p class="font-medium text-studio-success">Video Generated Successfully!</p>
            <p class="text-sm text-studio-success/80">Ready to publish to YouTube</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
