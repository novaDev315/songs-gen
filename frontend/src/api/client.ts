// Type definitions
export interface Song {
  id: string
  title: string
  genre: string
  style_prompt?: string
  lyrics?: string
  file_path?: string
  status: string
  effective_status?: string
  metadata_json?: Record<string, any>
  audio_path?: string
  youtube_url?: string
  created_at: string
  updated_at: string
}

export interface SongCreate {
  title: string
  genre?: string
  style_prompt?: string
  lyrics?: string
  file_path?: string
  metadata_json?: Record<string, any>
}

export interface SongUpdate {
  title?: string
  genre?: string
  style_prompt?: string
  lyrics?: string
  status?: string
  metadata_json?: Record<string, any>
}

export interface SongList {
  items: Song[]
  meta: {
    total: number
    skip: number
    limit: number
    has_more: boolean
  }
}

export interface VideoProject {
  id: number
  song_id: string
  cover_type?: string
  cover_path?: string
  video_style?: string
  lyric_style?: string
  preview_path?: string
  output_path?: string
  youtube_url?: string
  youtube_video_id?: string
  status: string
  progress?: number
  error_message?: string
  created_at: string
  updated_at: string
}

export interface StudioProject {
  id: string
  song_id: string
  status: string
  cover_path?: string
  lyric_timing?: any
  video_settings?: any
  metadata?: any
  created_at: string
  updated_at: string
}

export interface Template {
  id: string
  name: string
  category: string
  preview_url?: string
}

export interface User {
  id: number
  username: string
  email: string
  is_admin: boolean
  is_active: boolean
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

const API_BASE = '/api/v1'

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = localStorage.getItem('token')

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers
  })

  if (!response.ok) {
    if (response.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    throw new Error(`API Error: ${response.status}`)
  }

  return response.json()
}

export const api = {
  // Generic methods
  async get<T = any>(endpoint: string): Promise<T> {
    return request<T>(endpoint)
  },

  async post<T = any>(endpoint: string, data?: any): Promise<T> {
    return request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined
    })
  },

  async put<T = any>(endpoint: string, data?: any): Promise<T> {
    return request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined
    })
  },

  async delete<T = any>(endpoint: string): Promise<T> {
    return request<T>(endpoint, { method: 'DELETE' })
  },

  // Auth
  async login(username: string, password: string) {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Login failed' }))
      throw new Error(error.detail || 'Login failed')
    }
    return response.json()
  },

  // Health
  async checkHealth() {
    return request<{ status: string }>('/health')
  },

  // System Status
  async getSystemStatus() {
    return request<{
      songs: { total: number; by_status: Record<string, number> }
      tasks: { total: number; by_status: Record<string, number> }
    }>('/system/status')
  },

  // Songs
  async getSongs(limit = 50, status?: string) {
    const params = new URLSearchParams()
    params.append('limit', String(limit))
    if (status) params.append('status_filter', status)
    const response = await request<{ items: any[]; meta: any }>(`/songs?${params}`)
    return response.items || []
  },

  async getSong(id: string) {
    return request<any>(`/songs/${id}`)
  },

  async getSongsForReview(limit = 50) {
    const params = new URLSearchParams()
    params.append('limit', String(limit))
    const response = await request<{ items: any[]; meta: any }>(`/songs?${params}`)
    const items = response.items || []
    return items.filter((s: any) => s.status === 'downloaded' || s.status === 'pending' || s.status === 'evaluated')
  },

  // Tasks
  async getTasks(status?: string, taskType?: string, limit = 50) {
    const params = new URLSearchParams()
    if (status) params.append('status_filter', status)
    if (taskType) params.append('task_type', taskType)
    params.append('limit', String(limit))
    const response = await request<{ items: any[]; meta: any }>(`/queue/tasks?${params}`)
    return response.items || []
  },

  async getQueueStats() {
    return request<{
      pending_count: number
      running_count: number
      completed_count: number
      failed_count: number
      total_count: number
    }>('/queue/stats')
  },

  async retryTask(taskId: string) {
    return request<any>(`/queue/tasks/${taskId}/retry`, { method: 'POST' })
  },

  async cancelTask(taskId: string) {
    return request<any>(`/queue/tasks/${taskId}`, { method: 'DELETE' })
  },

  // Evaluations
  async submitEvaluation(songId: string, data: { approved: boolean; rating?: number; notes?: string }) {
    return request<any>(`/evaluations`, {
      method: 'POST',
      body: JSON.stringify({ song_id: songId, ...data })
    })
  },

  // Analytics
  async getAnalytics() {
    return request<any>('/analytics/dashboard')
  },

  // YouTube uploads
  async getYouTubeUploads(limit = 50) {
    const response = await request<{ items: any[]; meta: any }>(`/youtube/uploads?limit=${limit}`)
    return response.items || []
  },

  // ============================================
  // Studio API Methods
  // ============================================

  // Projects
  async createStudioProject(songId: string) {
    return request<any>('/studio/projects', {
      method: 'POST',
      body: JSON.stringify({ song_id: songId })
    })
  },

  async getStudioProjects(status?: string, limit = 50) {
    const params = new URLSearchParams()
    if (status) params.append('status_filter', status)
    params.append('limit', String(limit))
    const response = await request<{ items: any[]; meta: any }>(`/studio/projects?${params}`)
    return response.items || []
  },

  async getStudioProject(projectId: string) {
    return request<any>(`/studio/projects/${projectId}`)
  },

  async updateStudioProject(projectId: string, data: any) {
    return request<any>(`/studio/projects/${projectId}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    })
  },

  async deleteStudioProject(projectId: string) {
    return request<any>(`/studio/projects/${projectId}`, { method: 'DELETE' })
  },

  // Cover Generation
  async generateTemplateCover(projectId: string, templateId: string) {
    return request<any>(`/studio/projects/${projectId}/cover/template`, {
      method: 'POST',
      body: JSON.stringify({ template_id: templateId })
    })
  },

  async generateAICover(projectId: string, prompt?: string) {
    return request<any>(`/studio/projects/${projectId}/cover/ai`, {
      method: 'POST',
      body: JSON.stringify({ prompt })
    })
  },

  async uploadCover(projectId: string, file: File) {
    const token = localStorage.getItem('token')
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch(`${API_BASE}/studio/projects/${projectId}/cover/upload`, {
      method: 'POST',
      headers: {
        ...(token && { Authorization: `Bearer ${token}` })
      },
      body: formData
    })

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status}`)
    }
    return response.json()
  },

  async getCoverTemplates() {
    return request<{ templates: Record<string, string[]> }>('/studio/templates/covers')
  },

  // Lyric Timing
  async syncLyrics(projectId: string, mode = 'beat_synced') {
    return request<any>(`/studio/projects/${projectId}/lyrics/sync`, {
      method: 'POST',
      body: JSON.stringify({ mode })
    })
  },

  // Video Generation
  async generatePreview(projectId: string) {
    return request<any>(`/studio/projects/${projectId}/preview`, { method: 'POST' })
  },

  async publishProject(projectId: string) {
    return request<any>(`/studio/projects/${projectId}/publish`, { method: 'POST' })
  },

  // Metadata
  async suggestMetadata(projectId: string) {
    return request<any>(`/studio/projects/${projectId}/metadata/suggest`)
  },

  // SSE Status Stream
  createStatusStream(projectId: string): EventSource {
    const url = `${API_BASE}/studio/projects/${projectId}/status`
    return new EventSource(url)
  }
}
