<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { StatusBadge } from '@/components'
import { useSongsStore, type Task } from '@/stores/songs'

const store = useSongsStore()
const mounted = ref(false)

// Filter state
const selectedStatus = ref<string>('')
const selectedTaskType = ref<string>('')

// Filter options
const statusOptions = [
  { value: '', label: 'All Statuses' },
  { value: 'pending', label: 'Pending' },
  { value: 'running', label: 'Running' },
  { value: 'completed', label: 'Completed' },
  { value: 'failed', label: 'Failed' }
]

const taskTypeOptions = [
  { value: '', label: 'All Types' },
  { value: 'suno_upload', label: 'Suno Upload' },
  { value: 'suno_download', label: 'Suno Download' },
  { value: 'evaluate', label: 'Evaluate' },
  { value: 'youtube_upload', label: 'YouTube Upload' }
]

// Task type icons SVG paths and labels
const taskTypeConfig: Record<string, { iconPath: string; label: string }> = {
  suno_upload: { iconPath: 'M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12', label: 'Suno Upload' },
  suno_download: { iconPath: 'M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4', label: 'Suno Download' },
  evaluate: { iconPath: 'M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z', label: 'Evaluate' },
  youtube_upload: { iconPath: 'M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z', label: 'YouTube Upload' }
}

// Filtered tasks
const filteredTasks = computed(() => {
  return store.tasks.filter(task => {
    const statusMatch = !selectedStatus.value || task.status === selectedStatus.value
    const typeMatch = !selectedTaskType.value || task.task_type === selectedTaskType.value
    return statusMatch && typeMatch
  })
})

// Stats
const queueStats = computed(() => ({
  total: store.tasks.length,
  pending: store.tasks.filter(t => t.status === 'pending').length,
  running: store.tasks.filter(t => t.status === 'running').length,
  failed: store.tasks.filter(t => t.status === 'failed').length
}))

// Apply filters
const applyFilters = async () => {
  await store.fetchTasks(
    selectedStatus.value || undefined,
    selectedTaskType.value || undefined
  )
}

// Retry single task
const handleRetryTask = async (taskId: string) => {
  await store.retryTask(taskId)
}

// Retry all failed tasks
const handleRetryAllFailed = async () => {
  const failedTasks = store.tasks.filter(t => t.status === 'failed')
  for (const task of failedTasks) {
    await store.retryTask(task.id)
  }
}

// Get task type display info
const getTaskTypeInfo = (taskType: string) => {
  return taskTypeConfig[taskType] || { iconPath: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2', label: taskType }
}

onMounted(async () => {
  await store.fetchTasks()
  setTimeout(() => {
    mounted.value = true
  }, 100)
})
</script>

<template>
  <div class="space-y-8">
    <!-- Header -->
    <header
      class="flex flex-col lg:flex-row lg:items-end justify-between gap-6"
      :style="{
        opacity: mounted ? 1 : 0,
        transform: mounted ? 'translateY(0)' : 'translateY(-20px)',
        transition: 'all 0.6s ease-out'
      }"
    >
      <div>
        <div class="flex items-center gap-3 mb-3">
          <div class="w-1 h-8 rounded-full bg-gradient-to-b from-amber-500 to-studio-rose-500"></div>
          <span class="text-xs font-condensed text-studio-stone uppercase tracking-[0.2em]">Automation</span>
        </div>
        <h1 class="font-display text-4xl lg:text-5xl font-semibold text-studio-cream tracking-tight">
          Task Queue
        </h1>
        <p class="text-studio-sand font-body mt-2 max-w-lg">
          Monitor and manage automation tasks in the pipeline.
        </p>
      </div>

      <!-- Quick stats -->
      <div class="flex items-center gap-3 self-start lg:self-auto">
        <div class="px-4 py-2 rounded-xl bg-studio-black/60 border border-studio-graphite/40">
          <span class="text-2xl font-display font-semibold text-studio-cream">{{ queueStats.total }}</span>
          <span class="text-xs text-studio-stone ml-2 uppercase tracking-wider">Total</span>
        </div>
        <div v-if="queueStats.running > 0" class="px-4 py-2 rounded-xl bg-studio-violet-500/10 border border-studio-violet-500/30">
          <span class="text-2xl font-display font-semibold text-studio-violet-400">{{ queueStats.running }}</span>
          <span class="text-xs text-studio-violet-400/70 ml-2 uppercase tracking-wider">Running</span>
        </div>
        <div v-if="queueStats.failed > 0" class="px-4 py-2 rounded-xl bg-studio-error/10 border border-studio-error/30">
          <span class="text-2xl font-display font-semibold text-studio-error">{{ queueStats.failed }}</span>
          <span class="text-xs text-studio-error/70 ml-2 uppercase tracking-wider">Failed</span>
        </div>
      </div>
    </header>

    <!-- Filters and Actions -->
    <div
      class="card-static"
      :style="{
        opacity: mounted ? 1 : 0,
        transform: mounted ? 'translateY(0)' : 'translateY(20px)',
        transition: 'all 0.5s ease-out 0.1s'
      }"
    >
      <div class="flex flex-col lg:flex-row gap-4 items-start lg:items-end justify-between">
        <!-- Filters -->
        <div class="flex flex-col sm:flex-row gap-4 flex-1">
          <div class="flex-1">
            <label class="input-label">Status</label>
            <select
              v-model="selectedStatus"
              class="input-field"
              @change="applyFilters"
            >
              <option
                v-for="option in statusOptions"
                :key="option.value"
                :value="option.value"
              >
                {{ option.label }}
              </option>
            </select>
          </div>

          <div class="flex-1">
            <label class="input-label">Task Type</label>
            <select
              v-model="selectedTaskType"
              class="input-field"
              @change="applyFilters"
            >
              <option
                v-for="option in taskTypeOptions"
                :key="option.value"
                :value="option.value"
              >
                {{ option.label }}
              </option>
            </select>
          </div>
        </div>

        <!-- Bulk Actions -->
        <div class="flex items-end">
          <button
            v-if="queueStats.failed > 0"
            class="btn-danger flex items-center gap-2"
            @click="handleRetryAllFailed"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Retry All Failed ({{ queueStats.failed }})
          </button>
        </div>
      </div>
    </div>

    <!-- Task List -->
    <section
      class="card-static"
      :style="{
        opacity: mounted ? 1 : 0,
        transform: mounted ? 'translateY(0)' : 'translateY(20px)',
        transition: 'all 0.5s ease-out 0.2s'
      }"
    >
      <div class="flex items-center gap-3 mb-6">
        <div class="w-2 h-2 rounded-full bg-amber-500" style="box-shadow: 0 0 8px rgba(245, 158, 11, 0.5);"></div>
        <h3 class="text-sm font-condensed text-studio-sand uppercase tracking-widest">Tasks</h3>
        <span class="text-xs text-studio-slate ml-2">
          ({{ filteredTasks.length }} total)
        </span>
      </div>

      <div v-if="store.loading" class="flex flex-col items-center justify-center py-16">
        <div class="relative w-16 h-16 mb-4">
          <div class="absolute inset-0 rounded-full border-4 border-studio-graphite/30"></div>
          <div class="absolute inset-0 rounded-full border-4 border-amber-500 border-t-transparent animate-spin"></div>
        </div>
        <p class="text-studio-sand">Loading tasks...</p>
      </div>

      <div v-else-if="filteredTasks.length === 0" class="text-center py-16">
        <div class="w-20 h-20 mx-auto mb-4 rounded-full bg-studio-charcoal/50 flex items-center justify-center">
          <svg class="w-10 h-10 text-studio-slate" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
          </svg>
        </div>
        <h4 class="text-lg font-display font-medium text-studio-cream mb-2">Queue Empty</h4>
        <p class="text-studio-stone">No tasks found matching your filters.</p>
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="(task, index) in filteredTasks"
          :key="task.id"
          class="group flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 rounded-xl bg-studio-charcoal/20 border border-transparent hover:border-amber-500/20 hover:bg-studio-charcoal/40 transition-all duration-300"
          :style="{
            opacity: mounted ? 1 : 0,
            transform: mounted ? 'translateX(0)' : 'translateX(-20px)',
            transition: `all 0.4s ease-out ${0.25 + index * 0.05}s`
          }"
        >
          <!-- Task Info -->
          <div class="flex items-center gap-4 flex-1">
            <!-- Task Type Icon -->
            <div class="w-12 h-12 rounded-xl bg-studio-charcoal/50 flex items-center justify-center group-hover:bg-amber-500/10 transition-all">
              <svg class="w-6 h-6 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" :d="getTaskTypeInfo(task.task_type).iconPath" />
              </svg>
            </div>

            <!-- Task Details -->
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-1">
                <span class="font-medium text-studio-cream group-hover:text-amber-400 transition-colors">
                  {{ getTaskTypeInfo(task.task_type).label }}
                </span>
                <StatusBadge :status="task.status" />
              </div>

              <div class="text-sm text-studio-slate">
                Song ID: <span class="font-mono text-studio-sand">{{ task.song_id }}</span>
              </div>

              <div class="text-xs text-studio-slate mt-1">
                Created: {{ new Date(task.created_at).toLocaleString() }}
                • Priority: {{ task.priority }}
                • Retries: {{ task.retry_count }}
              </div>

              <!-- Error Message -->
              <div
                v-if="task.error_message"
                class="mt-2 text-xs text-studio-error bg-studio-error/10 border border-studio-error/30 rounded-lg px-3 py-2"
              >
                Error: {{ task.error_message }}
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex items-center gap-2">
            <button
              v-if="task.status === 'failed'"
              class="btn-secondary text-xs px-4 py-2 flex items-center gap-2"
              @click="handleRetryTask(task.id)"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Retry
            </button>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
