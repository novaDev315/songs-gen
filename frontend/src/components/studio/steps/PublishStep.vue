<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useStudioStore } from '@/stores/studio'
import { useRouter } from 'vue-router'
import { api } from '@/api/client'

const store = useStudioStore()
const router = useRouter()

const isPublishing = ref(false)
const publishProgress = ref(0)
const publishStatus = ref('')
const publishComplete = ref(false)
const publishError = ref<string | null>(null)
const youtubeUrl = ref<string | null>(null)
const outputPath = ref<string | null>(null)
let statusInterval: number | null = null

const canPublish = computed(() => {
  return (
    store.selectedSong &&
    store.metadata.title &&
    store.previewUrl &&
    !isPublishing.value
  )
})

const metadataComplete = computed(() => {
  return (
    store.metadata.title &&
    store.metadata.description &&
    store.metadata.tags.length > 0
  )
})

const videoGenerated = computed(() => {
  return !!store.previewUrl
})

const estimatedSize = computed(() => {
  const duration = store.selectedSong?.duration || 180
  const quality = store.videoSettings.highQuality ? 10 : 5
  const sizeMB = Math.round(duration / 60 * quality)
  return `~${sizeMB} MB`
})

const progressSteps = [
  { threshold: 5, label: 'Saving metadata' },
  { threshold: 10, label: 'Starting render' },
  { threshold: 40, label: 'Encoding video' },
  { threshold: 80, label: 'Finalizing' },
  { threshold: 100, label: 'Complete' },
]

onUnmounted(() => {
  if (statusInterval) {
    clearInterval(statusInterval)
  }
})

async function publishToYouTube() {
  if (!canPublish.value || !store.projectId) return

  isPublishing.value = true
  publishProgress.value = 0
  publishStatus.value = 'Preparing...'
  publishError.value = null

  try {
    publishProgress.value = 5
    publishStatus.value = 'Saving metadata...'
    await store.updateProject()

    publishProgress.value = 10
    publishStatus.value = 'Starting video render...'

    await api.post(`/studio/projects/${store.projectId}/publish`)

    trackPublishProgress()
  } catch (error: any) {
    console.error('Publishing failed:', error)
    publishError.value = error.message || 'Failed to start publishing'
    isPublishing.value = false
  }
}

async function trackPublishProgress() {
  statusInterval = window.setInterval(async () => {
    try {
      const response = await api.get(`/studio/projects/${store.projectId}`)

      if (response.status === 'rendering') {
        publishProgress.value = response.progress || Math.min(publishProgress.value + 5, 75)
        publishStatus.value = response.status_message || 'Rendering video...'
      } else if (response.status === 'publishing') {
        publishProgress.value = response.progress || 85
        publishStatus.value = response.status_message || 'Uploading to YouTube...'
      } else if (response.status === 'published') {
        if (statusInterval) clearInterval(statusInterval)
        publishProgress.value = 100
        publishStatus.value = 'Published to YouTube!'
        publishComplete.value = true
        youtubeUrl.value = response.youtube_url || null
        outputPath.value = response.output_path || null
        store.outputUrl = response.output_path || null
        isPublishing.value = false
      } else if (response.status === 'complete') {
        if (statusInterval) clearInterval(statusInterval)
        publishProgress.value = 100
        publishStatus.value = response.status_message || 'Video ready!'
        publishComplete.value = true
        youtubeUrl.value = response.youtube_url || null
        outputPath.value = response.output_path || null
        store.outputUrl = response.output_path || null
        isPublishing.value = false
      } else if (response.status === 'failed') {
        if (statusInterval) clearInterval(statusInterval)
        publishError.value = response.error_message || 'Publishing failed'
        isPublishing.value = false
      }
    } catch (error: any) {
      console.error('Error checking publish status:', error)
    }
  }, 3000)

  setTimeout(() => {
    if (statusInterval && isPublishing.value) {
      clearInterval(statusInterval)
      isPublishing.value = false
      publishError.value = 'Publishing timed out. Please check the status later.'
    }
  }, 600000)
}

function downloadVideo() {
  if (outputPath.value) {
    const a = document.createElement('a')
    a.href = '/api/v1' + outputPath.value
    a.download = `${store.selectedSong?.title || 'video'}_final.mp4`
    a.click()
  }
}

function openYouTube() {
  if (youtubeUrl.value) {
    window.open(youtubeUrl.value, '_blank')
  }
}

function createAnother() {
  store.reset()
  router.push('/studio')
}

function goToDashboard() {
  router.push('/dashboard')
}

function retry() {
  publishError.value = null
  publishComplete.value = false
  publishProgress.value = 0
}
</script>

<template>
  <div class="space-y-6">
    <!-- Step Header -->
    <div>
      <div class="flex items-center gap-2 mb-2">
        <div class="led-indicator green"></div>
        <span class="text-xs font-condensed text-studio-stone uppercase tracking-widest">Final Output</span>
      </div>
      <h2 class="text-xl font-display font-semibold text-studio-cream">Publish Video</h2>
      <p class="text-sm text-studio-sand mt-1">Render final video and optionally upload to YouTube</p>
    </div>

    <!-- Pre-publish Checklist -->
    <div class="stat-card amber">
      <div class="flex items-center gap-2 mb-4">
        <div class="led-indicator amber"></div>
        <h3 class="text-sm font-condensed text-studio-sand uppercase tracking-wider">Pre-Publish Checklist</h3>
      </div>
      <div class="space-y-3">
        <div class="flex items-center gap-3 text-sm"
          :class="metadataComplete ? 'text-studio-success' : 'text-studio-warning'"
        >
          <div class="w-5 h-5 rounded-full flex items-center justify-center"
            :class="metadataComplete ? 'bg-studio-success/20' : 'bg-studio-warning/20'"
          >
            <svg v-if="metadataComplete" class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <svg v-else class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <span>Video metadata (title, description, tags)</span>
        </div>
        <div class="flex items-center gap-3 text-sm"
          :class="videoGenerated ? 'text-studio-success' : 'text-studio-error'"
        >
          <div class="w-5 h-5 rounded-full flex items-center justify-center"
            :class="videoGenerated ? 'bg-studio-success/20' : 'bg-studio-error/20'"
          >
            <svg v-if="videoGenerated" class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <svg v-else class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <span>Preview video generated</span>
        </div>
        <div class="flex items-center gap-3 text-sm"
          :class="store.cover.path ? 'text-studio-success' : 'text-studio-slate'"
        >
          <div class="w-5 h-5 rounded-full flex items-center justify-center"
            :class="store.cover.path ? 'bg-studio-success/20' : 'bg-studio-graphite/30'"
          >
            <svg v-if="store.cover.path" class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <div v-else class="w-1.5 h-1.5 rounded-full bg-studio-slate"></div>
          </div>
          <span>Cover art / thumbnail</span>
        </div>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="publishError" class="stat-card rose">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 rounded-xl bg-studio-error/20 flex items-center justify-center">
          <svg class="w-6 h-6 text-studio-error" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <div class="flex-1">
          <p class="font-medium text-studio-error">Rendering Failed</p>
          <p class="text-sm text-studio-error/80">{{ publishError }}</p>
        </div>
        <button @click="retry" class="btn btn-sm btn-danger">
          Retry
        </button>
      </div>
    </div>

    <!-- Publishing Summary -->
    <div class="stat-card violet">
      <div class="flex items-center gap-2 mb-4">
        <div class="led-indicator violet"></div>
        <h3 class="text-sm font-condensed text-studio-sand uppercase tracking-wider">Video Summary</h3>
      </div>
      <div class="space-y-3">
        <div>
          <p class="text-xs text-studio-stone uppercase tracking-wider mb-1">Title</p>
          <p class="text-studio-cream font-medium">{{ store.metadata.title || '(No title set)' }}</p>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <p class="text-xs text-studio-stone uppercase tracking-wider mb-1">Privacy</p>
            <p class="text-studio-cream capitalize">{{ store.metadata.privacy }}</p>
          </div>
          <div>
            <p class="text-xs text-studio-stone uppercase tracking-wider mb-1">Estimated Size</p>
            <p class="text-studio-cream">{{ estimatedSize }}</p>
          </div>
        </div>
        <div>
          <p class="text-xs text-studio-stone uppercase tracking-wider mb-2">Tags</p>
          <div class="flex flex-wrap gap-1.5">
            <span
              v-for="tag in store.metadata.tags.slice(0, 5)"
              :key="tag"
              class="px-2 py-1 text-xs rounded-lg bg-studio-rose-500/20 text-studio-rose-400"
            >
              {{ tag }}
            </span>
            <span v-if="store.metadata.tags.length > 5" class="px-2 py-1 text-xs text-studio-slate">
              +{{ store.metadata.tags.length - 5 }} more
            </span>
            <span v-if="store.metadata.tags.length === 0" class="text-studio-slate text-xs">
              No tags set
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Publish Button -->
    <div v-if="!publishComplete && !isPublishing" class="text-center py-4">
      <button
        @click="publishToYouTube"
        :disabled="!canPublish"
        class="btn btn-primary btn-lg shadow-lg shadow-studio-rose-500/20"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
        Render Final Video
      </button>
      <p v-if="canPublish" class="text-studio-stone text-sm mt-4">
        This renders the full-quality video (may take 2-5 minutes)
      </p>
      <p v-else class="text-studio-warning text-sm mt-4">
        Please complete all required steps first
      </p>
    </div>

    <!-- Publishing Progress -->
    <div v-if="isPublishing" class="py-6 space-y-6">
      <div class="text-center">
        <div class="relative w-20 h-20 mx-auto mb-4">
          <div class="absolute inset-0 rounded-full border-4 border-studio-graphite/30"></div>
          <div class="absolute inset-0 rounded-full border-4 border-studio-rose-500 border-t-transparent animate-spin"></div>
          <div class="absolute inset-0 flex items-center justify-center">
            <span class="text-lg font-display font-semibold text-studio-cream">{{ publishProgress }}%</span>
          </div>
        </div>
        <h3 class="text-lg font-display font-semibold text-studio-cream">{{ publishStatus }}</h3>
      </div>

      <!-- VU Meter Progress -->
      <div class="vu-meter">
        <div class="vu-meter-fill" :style="{ width: publishProgress + '%' }"></div>
      </div>

      <!-- Step Indicators -->
      <div class="space-y-2">
        <div
          v-for="step in progressSteps"
          :key="step.threshold"
          class="flex items-center gap-3 text-sm"
          :class="publishProgress >= step.threshold ? 'text-studio-success' : 'text-studio-slate'"
        >
          <div class="w-5 h-5 rounded-full flex items-center justify-center"
            :class="publishProgress >= step.threshold ? 'bg-studio-success/20' : 'bg-studio-graphite/30'"
          >
            <svg v-if="publishProgress >= step.threshold" class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
          Please keep this page open. Video is being rendered on the server.
        </p>
      </div>
    </div>

    <!-- Success State -->
    <div v-if="publishComplete" class="space-y-6">
      <div class="p-6 rounded-2xl bg-studio-success/10 border border-studio-success/30 text-center">
        <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-studio-success/20 flex items-center justify-center">
          <svg class="w-8 h-8 text-studio-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h3 class="text-2xl font-display font-bold text-studio-success mb-2">Video Ready!</h3>
        <p class="text-studio-success/80 mb-6">Your final video has been rendered</p>

        <div class="flex flex-wrap justify-center gap-3">
          <button
            v-if="outputPath"
            @click="downloadVideo"
            class="btn btn-primary"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Download Video
          </button>
          <button
            v-if="youtubeUrl"
            @click="openYouTube"
            class="btn btn-secondary"
          >
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
            </svg>
            View on YouTube
          </button>
        </div>
      </div>

      <!-- YouTube Note -->
      <div v-if="!youtubeUrl" class="p-4 rounded-xl bg-studio-info/10 border border-studio-info/30">
        <div class="flex items-start gap-3">
          <svg class="w-5 h-5 text-studio-info mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <p class="font-medium text-studio-info">YouTube Upload</p>
            <p class="text-sm text-studio-info/80 mt-1">
              YouTube credentials not configured. Go to Settings to connect your YouTube account, or download the video and upload manually.
            </p>
          </div>
        </div>
      </div>

      <!-- Next Actions -->
      <div class="space-y-3">
        <h3 class="text-sm font-condensed text-studio-sand uppercase tracking-wider">What's Next?</h3>
        <div class="grid gap-3 md:grid-cols-2">
          <button
            @click="createAnother"
            class="group p-5 rounded-xl text-left transition-all duration-300 border bg-studio-charcoal/30 border-studio-graphite/40 hover:bg-studio-rose-500/10 hover:border-studio-rose-500/50"
          >
            <div class="w-12 h-12 mb-3 rounded-xl bg-studio-graphite/50 group-hover:bg-studio-rose-500/20 flex items-center justify-center transition-all">
              <svg class="w-6 h-6 text-studio-sand group-hover:text-studio-rose-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
            </div>
            <p class="font-medium text-studio-cream group-hover:text-studio-rose-400 transition-colors">Create Another Video</p>
            <p class="text-xs text-studio-stone mt-1">Start a new project</p>
          </button>
          <button
            @click="goToDashboard"
            class="group p-5 rounded-xl text-left transition-all duration-300 border bg-studio-charcoal/30 border-studio-graphite/40 hover:bg-studio-rose-500/10 hover:border-studio-rose-500/50"
          >
            <div class="w-12 h-12 mb-3 rounded-xl bg-studio-graphite/50 group-hover:bg-studio-rose-500/20 flex items-center justify-center transition-all">
              <svg class="w-6 h-6 text-studio-sand group-hover:text-studio-rose-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <p class="font-medium text-studio-cream group-hover:text-studio-rose-400 transition-colors">Go to Dashboard</p>
            <p class="text-xs text-studio-stone mt-1">View your projects</p>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
