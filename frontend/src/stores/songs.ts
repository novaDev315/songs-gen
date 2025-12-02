import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/api/client'

export interface Song {
  id: string
  title: string
  genre: string
  status: string
  quality_score: number | null
  created_at: string
  source_file: string
  style_prompt?: string
  lyrics?: string
}

export interface Task {
  id: string
  song_id: string
  task_type: string
  status: string
  priority: number
  retry_count: number
  created_at: string
  error_message?: string
}

export interface SystemStatus {
  songs: {
    total: number
    by_status: Record<string, number>
  }
  tasks: {
    total: number
    by_status: Record<string, number>
  }
}

export const useSongsStore = defineStore('songs', () => {
  const songs = ref<Song[]>([])
  const tasks = ref<Task[]>([])
  const systemStatus = ref<SystemStatus | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchSongs(limit = 50) {
    loading.value = true
    error.value = null
    try {
      songs.value = await api.getSongs(limit)
    } catch (e) {
      error.value = 'Failed to fetch songs'
      console.error(e)
    } finally {
      loading.value = false
    }
  }

  async function fetchTasks(status?: string, taskType?: string, limit = 50) {
    loading.value = true
    error.value = null
    try {
      tasks.value = await api.getTasks(status, taskType, limit)
    } catch (e) {
      error.value = 'Failed to fetch tasks'
      console.error(e)
    } finally {
      loading.value = false
    }
  }

  async function fetchSystemStatus() {
    try {
      systemStatus.value = await api.getSystemStatus()
    } catch (e) {
      console.error('Failed to fetch system status:', e)
    }
  }

  async function retryTask(taskId: string) {
    try {
      await api.retryTask(taskId)
      await fetchTasks()
    } catch (e) {
      console.error('Failed to retry task:', e)
    }
  }

  return {
    songs,
    tasks,
    systemStatus,
    loading,
    error,
    fetchSongs,
    fetchTasks,
    fetchSystemStatus,
    retryTask
  }
})
