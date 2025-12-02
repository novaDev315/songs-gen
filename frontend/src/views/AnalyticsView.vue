<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { api } from '@/api/client'

const mounted = ref(false)
const loading = ref(true)

// API data
const dashboardData = ref<any>(null)
const recentSongs = ref<any[]>([])

// Fetch analytics data from API
const fetchAnalytics = async () => {
  loading.value = true
  try {
    const [analytics, songs] = await Promise.all([
      api.get('/analytics/dashboard'),
      api.getSongs(20)
    ])
    dashboardData.value = analytics
    recentSongs.value = songs || []
  } catch (error) {
    console.error('Failed to fetch analytics:', error)
  } finally {
    loading.value = false
  }
}

// Key Metrics from API
const metrics = computed(() => {
  const overview = dashboardData.value?.overview
  if (!overview) {
    return { totalSongs: 0, successRate: 0, published: 0, failed: 0 }
  }

  const total = overview.total_songs || 0
  const published = overview.published_songs || 0
  const successRate = total > 0 ? Math.round((published / total) * 100) : 0

  return {
    totalSongs: total,
    successRate,
    published,
    failed: overview.failed_songs || 0
  }
})

// Status Chart Data from songs
const statusChart = computed(() => {
  const songs = recentSongs.value
  const total = songs.length || 1

  const statusCounts: Record<string, { count: number; color: string }> = {
    pending: { count: 0, color: 'bg-gray-500' },
    uploading: { count: 0, color: 'bg-blue-500' },
    generating: { count: 0, color: 'bg-yellow-500' },
    downloaded: { count: 0, color: 'bg-cyan-500' },
    evaluated: { count: 0, color: 'bg-purple-500' },
    uploaded: { count: 0, color: 'bg-green-500' },
    published: { count: 0, color: 'bg-green-500' },
    failed: { count: 0, color: 'bg-red-500' }
  }

  songs.forEach((song: any) => {
    if (song.status in statusCounts) {
      statusCounts[song.status].count++
    }
  })

  return Object.entries(statusCounts)
    .filter(([_, data]) => data.count > 0)
    .map(([status, data]) => ({
      status: status.charAt(0).toUpperCase() + status.slice(1),
      count: data.count,
      percentage: Math.round((data.count / total) * 100),
      color: data.color
    }))
})

// Performance Gauges from real data
const performanceGauges = computed(() => {
  const overview = dashboardData.value?.overview
  const quality = dashboardData.value?.quality

  const total = overview?.total_songs || 0
  const published = overview?.published_songs || 0
  const failed = overview?.failed_songs || 0

  const processed = published + failed
  const efficiency = processed > 0 ? Math.round((published / processed) * 100) : 0

  const weekSongs = overview?.songs_this_week || 0
  const processingRate = total > 0 ? Math.min(100, Math.round((weekSongs / Math.max(total, 1)) * 100 * 4)) : 0

  const qualityScore = quality?.average_score || 0

  return [
    { label: 'Pipeline Efficiency', value: efficiency, color: '#d4a574' },
    { label: 'Weekly Activity', value: processingRate, color: '#c9a227' },
    { label: 'Quality Score', value: Math.round(qualityScore), color: '#cd7f32' }
  ]
})

// Activity Heatmap from timeline data
const activityHeatmap = computed(() => {
  const timeline = dashboardData.value?.songs_over_time || []
  const weeks: { date: string; count: number }[][] = []
  const now = new Date()

  const dateCountMap: Record<string, number> = {}
  timeline.forEach((point: { date: string; count: number }) => {
    dateCountMap[point.date] = point.count
  })

  for (let week = 0; week < 4; week++) {
    const days: { date: string; count: number }[] = []
    for (let day = 0; day < 7; day++) {
      const date = new Date(now)
      date.setDate(date.getDate() - (week * 7 + day))
      const dateStr = date.toISOString().split('T')[0]

      days.push({
        date: date.toLocaleDateString(),
        count: dateCountMap[dateStr] || 0
      })
    }
    weeks.unshift(days)
  }

  return weeks
})

const getHeatmapColor = (count: number): string => {
  if (count === 0) return 'bg-studio-charcoal/30'
  if (count <= 2) return 'bg-studio-amber/20'
  if (count <= 4) return 'bg-studio-amber/40'
  if (count <= 6) return 'bg-studio-amber/60'
  return 'bg-studio-amber'
}

// Recent Activity from songs
const recentActivity = computed(() => {
  return recentSongs.value.slice(0, 5).map((song: any, index: number) => {
    const statusColors: Record<string, string> = {
      published: 'border-studio-success',
      uploaded: 'border-studio-success',
      downloaded: 'border-cyan-500',
      evaluated: 'border-purple-500',
      generating: 'border-yellow-500',
      pending: 'border-studio-slate',
      failed: 'border-studio-error'
    }

    const statusMessages: Record<string, string> = {
      published: 'Published to YouTube',
      uploaded: 'Uploaded successfully',
      downloaded: 'Downloaded from Suno',
      evaluated: 'Quality evaluation complete',
      generating: 'Generation in progress',
      pending: 'Added to queue',
      failed: 'Processing failed'
    }

    const timeAgo = getTimeAgo(song.updated_at || song.created_at)

    return {
      id: index,
      title: statusMessages[song.status] || 'Status updated',
      description: `"${song.title}"`,
      time: timeAgo,
      borderColor: statusColors[song.status] || 'border-studio-slate'
    }
  })
})

const getTimeAgo = (dateStr: string): string => {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins} min ago`
  if (diffHours < 24) return `${diffHours} hours ago`
  return `${diffDays} days ago`
}

onMounted(async () => {
  await fetchAnalytics()
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
          <div class="w-1 h-8 rounded-full bg-gradient-to-b from-cyan-500 to-studio-violet-500"></div>
          <span class="text-xs font-condensed text-studio-stone uppercase tracking-[0.2em]">Insights</span>
        </div>
        <h1 class="font-display text-4xl lg:text-5xl font-semibold text-studio-cream tracking-tight">
          Analytics
        </h1>
        <p class="text-studio-sand font-body mt-2 max-w-lg">
          Performance metrics and insights for your song automation pipeline.
        </p>
      </div>

      <!-- Quick stats summary -->
      <div class="flex items-center gap-3 self-start lg:self-auto">
        <div class="px-4 py-2 rounded-xl bg-studio-black/60 border border-studio-graphite/40">
          <span class="text-2xl font-display font-semibold text-studio-cream">{{ metrics.totalSongs }}</span>
          <span class="text-xs text-studio-stone ml-2 uppercase tracking-wider">Songs</span>
        </div>
        <div class="px-4 py-2 rounded-xl bg-studio-success/10 border border-studio-success/30">
          <span class="text-2xl font-display font-semibold text-studio-success">{{ metrics.successRate }}%</span>
          <span class="text-xs text-studio-success/70 ml-2 uppercase tracking-wider">Success</span>
        </div>
      </div>
    </header>

    <!-- Loading State -->
    <div
      v-if="loading"
      class="flex flex-col items-center justify-center py-20"
    >
      <div class="relative w-20 h-20 mb-6">
        <div class="absolute inset-0 rounded-full border-4 border-studio-graphite/30"></div>
        <div class="absolute inset-0 rounded-full border-4 border-cyan-500 border-t-transparent animate-spin"></div>
      </div>
      <p class="text-studio-sand animate-pulse-soft">Loading analytics...</p>
    </div>

    <template v-else>
      <!-- Key Metrics -->
      <div
        class="grid grid-cols-2 lg:grid-cols-4 gap-4"
        :style="{
          opacity: mounted ? 1 : 0,
          transform: mounted ? 'translateY(0)' : 'translateY(20px)',
          transition: 'all 0.5s ease-out 0.1s'
        }"
      >
        <div class="stat-card rose group">
          <div class="flex items-start justify-between">
            <div>
              <p class="text-xs font-condensed text-studio-stone uppercase tracking-wider mb-2">Total Songs</p>
              <p class="text-3xl font-display font-semibold text-studio-cream">{{ metrics.totalSongs }}</p>
            </div>
            <div class="w-12 h-12 rounded-xl bg-studio-graphite/50 flex items-center justify-center">
              <svg class="w-6 h-6 text-studio-rose-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
              </svg>
            </div>
          </div>
        </div>

        <div class="stat-card amber group">
          <div class="flex items-start justify-between">
            <div>
              <p class="text-xs font-condensed text-studio-stone uppercase tracking-wider mb-2">Success Rate</p>
              <p class="text-3xl font-display font-semibold text-studio-cream">{{ metrics.successRate }}%</p>
            </div>
            <div class="w-12 h-12 rounded-xl bg-studio-graphite/50 flex items-center justify-center">
              <svg class="w-6 h-6 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div class="stat-card violet group">
          <div class="flex items-start justify-between">
            <div>
              <p class="text-xs font-condensed text-studio-stone uppercase tracking-wider mb-2">Published</p>
              <p class="text-3xl font-display font-semibold text-studio-cream">{{ metrics.published }}</p>
            </div>
            <div class="w-12 h-12 rounded-xl bg-studio-graphite/50 flex items-center justify-center">
              <svg class="w-6 h-6 text-studio-violet-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </div>
          </div>
        </div>

        <div class="stat-card gold group">
          <div class="flex items-start justify-between">
            <div>
              <p class="text-xs font-condensed text-studio-stone uppercase tracking-wider mb-2">Failed</p>
              <p class="text-3xl font-display font-semibold text-studio-cream">{{ metrics.failed }}</p>
            </div>
            <div class="w-12 h-12 rounded-xl bg-studio-graphite/50 flex items-center justify-center">
              <svg class="w-6 h-6 text-studio-error" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- Charts Row -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Songs by Status Bar Chart -->
        <section
          class="card-static"
          :style="{
            opacity: mounted ? 1 : 0,
            transform: mounted ? 'translateY(0)' : 'translateY(20px)',
            transition: 'all 0.5s ease-out 0.15s'
          }"
        >
          <div class="flex items-center gap-3 mb-6">
            <div class="w-2 h-2 rounded-full bg-cyan-500" style="box-shadow: 0 0 8px rgba(6, 182, 212, 0.5);"></div>
            <h3 class="text-sm font-condensed text-studio-sand uppercase tracking-widest">Songs by Status</h3>
          </div>

          <div v-if="statusChart.length > 0" class="space-y-4">
            <div
              v-for="(item, index) in statusChart"
              :key="item.status"
              class="flex items-center gap-4"
              :style="{
                opacity: mounted ? 1 : 0,
                transform: mounted ? 'translateX(0)' : 'translateX(-20px)',
                transition: `all 0.4s ease-out ${0.2 + index * 0.05}s`
              }"
            >
              <div class="w-24 text-sm text-studio-sand font-medium">{{ item.status }}</div>
              <div class="flex-1 h-8 bg-studio-charcoal/30 rounded-lg overflow-hidden">
                <div
                  :class="item.color"
                  :style="{ width: `${item.percentage}%` }"
                  class="h-full rounded-lg transition-all duration-700 flex items-center justify-end pr-3"
                >
                  <span v-if="item.percentage > 15" class="text-xs font-bold text-white">{{ item.count }}</span>
                </div>
              </div>
              <div class="w-16 text-sm text-studio-stone text-right font-mono">{{ item.percentage }}%</div>
            </div>
          </div>
          <div v-else class="text-center py-12">
            <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-studio-charcoal/30 flex items-center justify-center">
              <svg class="w-8 h-8 text-studio-slate" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2z" />
              </svg>
            </div>
            <p class="text-studio-stone">No songs yet</p>
            <p class="text-sm text-studio-slate mt-1">Add songs to see status distribution</p>
          </div>
        </section>

        <!-- Performance Gauges -->
        <section
          class="card-static"
          :style="{
            opacity: mounted ? 1 : 0,
            transform: mounted ? 'translateY(0)' : 'translateY(20px)',
            transition: 'all 0.5s ease-out 0.2s'
          }"
        >
          <div class="flex items-center gap-3 mb-6">
            <div class="w-2 h-2 rounded-full bg-studio-gold" style="box-shadow: 0 0 8px rgba(201, 162, 39, 0.5);"></div>
            <h3 class="text-sm font-condensed text-studio-sand uppercase tracking-widest">Performance Metrics</h3>
          </div>

          <div class="grid grid-cols-3 gap-4">
            <div
              v-for="(gauge, index) in performanceGauges"
              :key="gauge.label"
              class="flex flex-col items-center"
              :style="{
                opacity: mounted ? 1 : 0,
                transform: mounted ? 'scale(1)' : 'scale(0.8)',
                transition: `all 0.5s ease-out ${0.25 + index * 0.1}s`
              }"
            >
              <svg class="w-24 h-24" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="40" fill="none" stroke="#1f1f1f" stroke-width="8" />
                <circle
                  cx="50" cy="50" r="40" fill="none"
                  :stroke="gauge.color"
                  stroke-width="8"
                  stroke-linecap="round"
                  :stroke-dasharray="`${gauge.value * 2.51} 251`"
                  transform="rotate(-90 50 50)"
                  class="transition-all duration-1000"
                />
                <text x="50" y="50" text-anchor="middle" dominant-baseline="middle" class="text-lg font-bold fill-studio-cream">
                  {{ gauge.value }}%
                </text>
              </svg>
              <div class="text-xs text-studio-stone mt-3 text-center font-condensed uppercase tracking-wider">{{ gauge.label }}</div>
            </div>
          </div>
        </section>
      </div>

      <!-- Activity Heatmap -->
      <section
        class="card-static"
        :style="{
          opacity: mounted ? 1 : 0,
          transform: mounted ? 'translateY(0)' : 'translateY(20px)',
          transition: 'all 0.5s ease-out 0.25s'
        }"
      >
        <div class="flex items-center gap-3 mb-6">
          <div class="w-2 h-2 rounded-full bg-studio-amber" style="box-shadow: 0 0 8px rgba(212, 165, 116, 0.5);"></div>
          <h3 class="text-sm font-condensed text-studio-sand uppercase tracking-widest">Activity Heatmap (Last 4 Weeks)</h3>
        </div>

        <div class="flex gap-1.5">
          <div
            v-for="(week, weekIndex) in activityHeatmap"
            :key="weekIndex"
            class="flex flex-col gap-1.5"
          >
            <div
              v-for="(day, dayIndex) in week"
              :key="dayIndex"
              :class="getHeatmapColor(day.count)"
              :title="`${day.count} songs on ${day.date}`"
              class="w-4 h-4 rounded cursor-pointer hover:ring-2 hover:ring-studio-amber/50 transition-all"
            />
          </div>
        </div>
        <div class="flex items-center gap-3 mt-6 text-xs text-studio-slate">
          <span class="font-condensed uppercase tracking-wider">Less</span>
          <div class="flex gap-1.5">
            <div class="w-4 h-4 bg-studio-charcoal/30 rounded" />
            <div class="w-4 h-4 bg-studio-amber/20 rounded" />
            <div class="w-4 h-4 bg-studio-amber/40 rounded" />
            <div class="w-4 h-4 bg-studio-amber/60 rounded" />
            <div class="w-4 h-4 bg-studio-amber rounded" />
          </div>
          <span class="font-condensed uppercase tracking-wider">More</span>
        </div>
      </section>

      <!-- Recent Activity Timeline -->
      <section
        class="card-static"
        :style="{
          opacity: mounted ? 1 : 0,
          transform: mounted ? 'translateY(0)' : 'translateY(20px)',
          transition: 'all 0.5s ease-out 0.3s'
        }"
      >
        <div class="flex items-center gap-3 mb-6">
          <div class="w-2 h-2 rounded-full bg-studio-violet-500" style="box-shadow: 0 0 8px rgba(155, 126, 217, 0.5);"></div>
          <h3 class="text-sm font-condensed text-studio-sand uppercase tracking-widest">Recent Activity</h3>
        </div>

        <div v-if="recentActivity.length > 0" class="space-y-4">
          <div
            v-for="(activity, index) in recentActivity"
            :key="activity.id"
            class="flex gap-4 pl-4 border-l-4 py-3 rounded-r-lg bg-studio-charcoal/10 hover:bg-studio-charcoal/20 transition-colors"
            :class="activity.borderColor"
            :style="{
              opacity: mounted ? 1 : 0,
              transform: mounted ? 'translateX(0)' : 'translateX(-20px)',
              transition: `all 0.4s ease-out ${0.35 + index * 0.05}s`
            }"
          >
            <div class="flex-1">
              <div class="text-studio-cream font-medium">{{ activity.title }}</div>
              <div class="text-sm text-studio-stone mt-1">{{ activity.description }}</div>
            </div>
            <div class="text-xs text-studio-slate font-mono self-center">{{ activity.time }}</div>
          </div>
        </div>
        <div v-else class="text-center py-12">
          <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-studio-charcoal/30 flex items-center justify-center">
            <svg class="w-8 h-8 text-studio-slate" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <p class="text-studio-stone">No recent activity</p>
          <p class="text-sm text-studio-slate mt-1">Activity will appear here as songs are processed</p>
        </div>
      </section>
    </template>
  </div>
</template>
