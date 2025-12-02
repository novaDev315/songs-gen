import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { api } from '@/api/client'

interface Song {
  id: string
  title: string
  genre: string
  lyrics: string
  style_prompt: string
  status: string
}

interface CoverSettings {
  type: 'template' | 'ai' | 'upload' | 'skip' | null
  path: string | null
  templateId: string | null
  aiPrompt: string | null
}

interface VideoSettings {
  style: 'lyric' | 'waveform' | 'static' | 'text_overlay'
  lyricStyle: 'fade' | 'karaoke' | 'scroll' | 'word_karaoke' | 'word_appear'
  backgroundColor: string
  textColor: string
  highlightColor: string
  highlightEffect: 'color' | 'glow' | 'bounce' | 'underline'
}

interface VideoUISettings {
  visualStyle: string
  colorTheme: string
  showTitle: boolean
  showArtist: boolean
  highQuality: boolean
  customColors: {
    primary: string
    secondary: string
    accent: string
  }
}

interface MetadataSettings {
  title: string
  description: string
  tags: string[]
  privacy: 'public' | 'unlisted' | 'private'
}

interface LyricLine {
  text: string
  start_time: number
  end_time: number
  is_emphasized: boolean
}

interface SavedState {
  projectId: string
  currentStep: number
}

const STORAGE_KEY = 'studio_project'

export const useStudioStore = defineStore('studio', () => {
  // State
  const projectId = ref<string | null>(null)
  const selectedSong = ref<Song | null>(null)
  const currentStep = ref(0)

  const cover = ref<CoverSettings>({
    type: null,
    path: null,
    templateId: null,
    aiPrompt: null,
  })

  const video = ref<VideoSettings>({
    style: 'lyric',
    lyricStyle: 'fade',
    backgroundColor: '#000000',
    textColor: '#ffffff',
    highlightColor: '#ffd700',
    highlightEffect: 'color',
  })

  const videoSettings = ref<VideoUISettings>({
    visualStyle: 'lyric',  // Default to lyric video so lyrics show
    colorTheme: 'genre_based',
    showTitle: true,
    showArtist: true,
    highQuality: true,
    customColors: {
      primary: '#f59e0b',
      secondary: '#ec4899',
      accent: '#8b5cf6',
    },
  })

  const metadata = ref<MetadataSettings>({
    title: '',
    description: '',
    tags: [],
    privacy: 'private',
  })

  const lyricTiming = ref<LyricLine[]>([])
  const previewUrl = ref<string | null>(null)
  const outputUrl = ref<string | null>(null)

  const isLoading = ref(false)
  const progress = ref(0)
  const error = ref<string | null>(null)

  // Getters
  const isProjectReady = computed(() => !!projectId.value && !!selectedSong.value)
  const canGeneratePreview = computed(() => isProjectReady.value && (cover.value.path || cover.value.type === 'skip'))
  const hasSavedProject = computed(() => {
    const saved = localStorage.getItem(STORAGE_KEY)
    return saved !== null
  })

  // Persistence functions
  function saveToStorage() {
    if (projectId.value) {
      const state: SavedState = {
        projectId: projectId.value,
        currentStep: currentStep.value,
      }
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
    }
  }

  function clearStorage() {
    localStorage.removeItem(STORAGE_KEY)
  }

  // Watch for changes and auto-save
  watch([projectId, currentStep], () => {
    if (projectId.value) {
      saveToStorage()
    }
  })

  // Resume from saved state
  async function resumeProject(): Promise<boolean> {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (!saved) return false

    try {
      isLoading.value = true
      const state: SavedState = JSON.parse(saved)

      // Fetch project from backend
      const project = await api.get(`/studio/projects/${state.projectId}`)

      if (!project) {
        clearStorage()
        return false
      }

      // Restore project state
      projectId.value = project.id
      currentStep.value = state.currentStep

      // Fetch the song data
      if (project.song_id) {
        const song = await api.get(`/songs/${project.song_id}`)
        selectedSong.value = song
        metadata.value.title = song.title
      }

      // Restore cover
      if (project.cover_path) {
        cover.value = {
          type: project.cover_type || 'template',
          path: project.cover_path,
          templateId: null,
          aiPrompt: null,
        }
      }

      // Restore video settings
      if (project.video_style) {
        video.value.style = project.video_style
        // Also sync to videoSettings.visualStyle
        videoSettings.value.visualStyle = project.video_style
      }
      if (project.lyric_style) {
        video.value.lyricStyle = project.lyric_style
      }
      if (project.background_color) {
        video.value.backgroundColor = project.background_color
      }
      if (project.text_color) {
        video.value.textColor = project.text_color
      }
      if (project.highlight_color) {
        video.value.highlightColor = project.highlight_color
      }
      if (project.highlight_effect) {
        video.value.highlightEffect = project.highlight_effect
      }

      // Restore UI video settings from JSON
      if (project.video_settings_json) {
        try {
          const uiSettings = JSON.parse(project.video_settings_json)
          videoSettings.value = { ...videoSettings.value, ...uiSettings }
        } catch {
          // Ignore parse errors
        }
      }

      // Restore metadata
      if (project.custom_title) {
        metadata.value.title = project.custom_title
      }
      if (project.custom_description) {
        metadata.value.description = project.custom_description
      }
      if (project.custom_tags) {
        try {
          metadata.value.tags = JSON.parse(project.custom_tags)
        } catch {
          metadata.value.tags = []
        }
      }
      if (project.privacy) {
        metadata.value.privacy = project.privacy
      }

      // Restore preview/output URLs
      if (project.preview_path) {
        previewUrl.value = project.preview_path
      }
      if (project.output_path) {
        outputUrl.value = project.output_path
      }

      return true
    } catch (e: any) {
      console.error('Failed to resume project:', e)
      clearStorage()
      return false
    } finally {
      isLoading.value = false
    }
  }

  function setStep(step: number) {
    currentStep.value = step
  }

  // Actions
  async function selectSong(song: Song) {
    selectedSong.value = song
    metadata.value.title = song.title

    // Create project in backend
    try {
      isLoading.value = true
      const response = await api.post('/studio/projects', { song_id: song.id })
      projectId.value = response.id
      currentStep.value = 0
      saveToStorage()
    } catch (e: any) {
      error.value = e.message
    } finally {
      isLoading.value = false
    }
  }

  async function generateTemplateCover(templateId: string) {
    if (!projectId.value) return

    try {
      isLoading.value = true
      const response = await api.post(`/studio/projects/${projectId.value}/cover/template`, {
        template_id: templateId,
      })
      cover.value = {
        type: 'template',
        path: response.cover_path,
        templateId,
        aiPrompt: null,
      }
    } catch (e: any) {
      error.value = e.message
    } finally {
      isLoading.value = false
    }
  }

  async function generateAICover(prompt?: string) {
    if (!projectId.value) return

    try {
      isLoading.value = true
      const response = await api.post(`/studio/projects/${projectId.value}/cover/ai`, {
        prompt,
      })
      cover.value = {
        type: 'ai',
        path: response.cover_path,
        templateId: null,
        aiPrompt: prompt || null,
      }
    } catch (e: any) {
      error.value = e.message
    } finally {
      isLoading.value = false
    }
  }

  async function uploadCover(file: File) {
    if (!projectId.value) return

    try {
      isLoading.value = true
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch(`/api/v1/studio/projects/${projectId.value}/cover/upload`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: formData,
      })

      if (!response.ok) throw new Error('Upload failed')

      const data = await response.json()
      cover.value = {
        type: 'upload',
        path: data.cover_path,
        templateId: null,
        aiPrompt: null,
      }
    } catch (e: any) {
      error.value = e.message
    } finally {
      isLoading.value = false
    }
  }

  function updateVideoSettings(settings: Partial<VideoUISettings>) {
    videoSettings.value = { ...videoSettings.value, ...settings }
  }

  async function updateMetadata(newMetadata: Partial<MetadataSettings>) {
    metadata.value = { ...metadata.value, ...newMetadata }
    // Auto-save to backend
    await updateProject()
  }

  async function syncLyrics() {
    if (!projectId.value || !selectedSong.value) return

    try {
      isLoading.value = true
      const response = await api.post(`/studio/projects/${projectId.value}/lyrics/sync`)
      lyricTiming.value = response.timing
    } catch (e: any) {
      error.value = e.message
    } finally {
      isLoading.value = false
    }
  }

  async function updateProject() {
    if (!projectId.value) return

    try {
      await api.put(`/studio/projects/${projectId.value}`, {
        video_style: video.value.style,
        lyric_style: video.value.lyricStyle,
        background_color: video.value.backgroundColor,
        text_color: video.value.textColor,
        highlight_color: video.value.highlightColor,
        highlight_effect: video.value.highlightEffect,
        custom_title: metadata.value.title,
        custom_description: metadata.value.description,
        custom_tags: JSON.stringify(metadata.value.tags),
        privacy: metadata.value.privacy,
        // Save UI video settings as JSON
        video_settings_json: JSON.stringify(videoSettings.value),
      })
    } catch (e: any) {
      error.value = e.message
    }
  }

  async function generatePreview() {
    if (!projectId.value) return

    try {
      isLoading.value = true
      progress.value = 0

      // Start SSE connection for progress
      const eventSource = new EventSource(`/api/v1/studio/projects/${projectId.value}/status`)

      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data)
        progress.value = data.progress
        if (data.status === 'preview_ready') {
          previewUrl.value = data.preview_path
          eventSource.close()
          isLoading.value = false
        } else if (data.status === 'failed') {
          error.value = data.error_message
          eventSource.close()
          isLoading.value = false
        }
      }

      // Trigger preview generation
      await api.post(`/studio/projects/${projectId.value}/preview`)
    } catch (e: any) {
      error.value = e.message
      isLoading.value = false
    }
  }

  async function publish() {
    if (!projectId.value) return

    try {
      isLoading.value = true
      await api.post(`/studio/projects/${projectId.value}/publish`)
    } catch (e: any) {
      error.value = e.message
    } finally {
      isLoading.value = false
    }
  }

  async function getSuggestedMetadata() {
    if (!projectId.value) return

    try {
      const response = await api.get(`/studio/projects/${projectId.value}/metadata/suggest`)
      metadata.value.title = response.suggested_title || metadata.value.title
      metadata.value.description = response.description || ''
      metadata.value.tags = response.tags || []
    } catch (e: any) {
      error.value = e.message
    }
  }

  function reset() {
    projectId.value = null
    selectedSong.value = null
    currentStep.value = 0
    cover.value = { type: null, path: null, templateId: null, aiPrompt: null }
    video.value = { style: 'lyric', lyricStyle: 'fade', backgroundColor: '#000000', textColor: '#ffffff', highlightColor: '#ffd700', highlightEffect: 'color' }
    videoSettings.value = {
      visualStyle: 'lyric',  // Default to lyric video
      colorTheme: 'genre_based',
      showTitle: true,
      showArtist: true,
      highQuality: true,
      customColors: { primary: '#f59e0b', secondary: '#ec4899', accent: '#8b5cf6' },
    }
    metadata.value = { title: '', description: '', tags: [], privacy: 'private' }
    lyricTiming.value = []
    previewUrl.value = null
    outputUrl.value = null
    isLoading.value = false
    progress.value = 0
    error.value = null
    clearStorage()
  }

  return {
    // State
    projectId,
    selectedSong,
    currentStep,
    cover,
    video,
    videoSettings,
    metadata,
    lyricTiming,
    previewUrl,
    outputUrl,
    isLoading,
    progress,
    error,
    // Getters
    isProjectReady,
    canGeneratePreview,
    hasSavedProject,
    // Actions
    selectSong,
    generateTemplateCover,
    generateAICover,
    uploadCover,
    updateVideoSettings,
    updateMetadata,
    syncLyrics,
    updateProject,
    generatePreview,
    publish,
    getSuggestedMetadata,
    reset,
    setStep,
    resumeProject,
    clearStorage,
  }
})
