<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { api } from '@/api/client'

const mounted = ref(false)

// Suno Integration
const sunoStatus = reactive({
  connected: false,
  message: 'Unable to check status'
})
const isRefreshingSuno = ref(false)

const refreshSunoStatus = async () => {
  isRefreshingSuno.value = true
  try {
    const response = await api.get('/system/status')
    sunoStatus.connected = response.suno?.session_valid || false
    sunoStatus.message = sunoStatus.connected ? 'Session is valid' : 'Session expired or not found'
  } catch (error) {
    sunoStatus.connected = false
    sunoStatus.message = 'Unable to check status'
  } finally {
    isRefreshingSuno.value = false
  }
}

// YouTube Integration
const youtubeStatus = reactive({
  connected: false,
  message: 'Unable to check status'
})
const isConnectingYouTube = ref(false)

const connectYouTube = async () => {
  isConnectingYouTube.value = true
  try {
    const response = await api.get('/youtube/auth-url')
    if (response.auth_url) {
      window.location.href = response.auth_url
    }
  } catch (error) {
    console.error('Failed to initiate YouTube auth:', error)
  } finally {
    isConnectingYouTube.value = false
  }
}

// Automation Settings
const automationSettings = reactive({
  autoUpload: false,
  qualityThreshold: 3
})

// System Info
const systemInfo = reactive({
  version: '1.0.0',
  databaseConnected: true,
  fileWatcherActive: true
})

// Save Settings
const isSaving = ref(false)
const showSaveConfirmation = ref(false)

const saveSettings = async () => {
  isSaving.value = true
  try {
    // Save automation settings to backend
    await api.post('/settings', {
      auto_upload: automationSettings.autoUpload,
      quality_threshold: automationSettings.qualityThreshold
    })

    showSaveConfirmation.value = true
    setTimeout(() => {
      showSaveConfirmation.value = false
    }, 3000)
  } catch (error) {
    console.error('Failed to save settings:', error)
  } finally {
    isSaving.value = false
  }
}

// Fetch initial status on mount
onMounted(async () => {
  try {
    // Fetch comprehensive system metrics
    const metrics = await api.get('/system/metrics')

    // Update system info from metrics
    systemInfo.version = metrics.system?.version || '1.0.0'
    systemInfo.databaseConnected = metrics.database?.connected || false
    // File watcher is active if watch folder exists (it's started on app startup)
    systemInfo.fileWatcherActive = metrics.storage?.watch_folder_exists || false

    // Try to fetch Suno status separately
    try {
      const sunoResponse = await api.get('/system/status')
      sunoStatus.connected = sunoResponse.suno?.session_valid || false
      sunoStatus.message = sunoStatus.connected ? 'Session is valid' : 'Session expired or not found'
    } catch {
      sunoStatus.connected = false
      sunoStatus.message = 'Session check unavailable'
    }

    // YouTube status - assume not connected unless we have credentials
    youtubeStatus.connected = false
    youtubeStatus.message = 'Authorization required'
  } catch (error) {
    console.error('Failed to fetch system status:', error)
  }

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
          <div class="w-1 h-8 rounded-full bg-gradient-to-b from-studio-bronze to-amber-600"></div>
          <span class="text-xs font-condensed text-studio-stone uppercase tracking-[0.2em]">Configuration</span>
        </div>
        <h1 class="font-display text-4xl lg:text-5xl font-semibold text-studio-cream tracking-tight">
          Settings
        </h1>
        <p class="text-studio-sand font-body mt-2 max-w-lg">
          Configure your automation pipeline preferences and integrations.
        </p>
      </div>

      <!-- Quick status indicators -->
      <div class="flex items-center gap-3 self-start lg:self-auto">
        <div
          class="px-4 py-2 rounded-xl border"
          :class="sunoStatus.connected
            ? 'bg-studio-success/10 border-studio-success/30'
            : 'bg-studio-warning/10 border-studio-warning/30'"
        >
          <div class="flex items-center gap-2">
            <div
              class="w-2 h-2 rounded-full"
              :class="sunoStatus.connected ? 'bg-studio-success' : 'bg-studio-warning'"
              :style="{ boxShadow: sunoStatus.connected ? '0 0 8px rgba(74, 222, 128, 0.6)' : '0 0 8px rgba(250, 204, 21, 0.6)' }"
            ></div>
            <span class="text-xs uppercase tracking-wider" :class="sunoStatus.connected ? 'text-studio-success' : 'text-studio-warning'">
              Suno
            </span>
          </div>
        </div>
        <div
          class="px-4 py-2 rounded-xl border"
          :class="youtubeStatus.connected
            ? 'bg-studio-success/10 border-studio-success/30'
            : 'bg-studio-error/10 border-studio-error/30'"
        >
          <div class="flex items-center gap-2">
            <div
              class="w-2 h-2 rounded-full"
              :class="youtubeStatus.connected ? 'bg-studio-success' : 'bg-studio-error'"
              :style="{ boxShadow: youtubeStatus.connected ? '0 0 8px rgba(74, 222, 128, 0.6)' : '0 0 8px rgba(239, 68, 68, 0.6)' }"
            ></div>
            <span class="text-xs uppercase tracking-wider" :class="youtubeStatus.connected ? 'text-studio-success' : 'text-studio-error'">
              YouTube
            </span>
          </div>
        </div>
      </div>
    </header>

    <!-- 2x2 Card Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Suno Integration Card -->
      <div
        class="card-static"
        :style="{
          opacity: mounted ? 1 : 0,
          transform: mounted ? 'translateY(0)' : 'translateY(20px)',
          transition: 'all 0.5s ease-out 0.1s'
        }"
      >
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-full bg-studio-amber/20 flex items-center justify-center">
            <svg class="w-5 h-5 text-studio-amber" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
            </svg>
          </div>
          <div>
            <h3 class="text-lg font-semibold text-studio-cream">Suno Integration</h3>
            <p class="text-sm text-studio-slate">Session-based authentication</p>
          </div>
        </div>

        <div class="space-y-4">
          <!-- Status Indicator -->
          <div class="flex items-center gap-3 p-3 rounded-lg bg-studio-charcoal/50">
            <div
              class="w-2.5 h-2.5 rounded-full"
              :class="sunoStatus.connected ? 'bg-studio-vu-green' : 'bg-studio-vu-yellow'"
              :style="{ boxShadow: sunoStatus.connected ? '0 0 8px rgba(74, 222, 128, 0.6)' : '0 0 8px rgba(250, 204, 21, 0.6)' }"
            ></div>
            <div class="flex-1">
              <p class="text-sm font-medium text-studio-cream">
                {{ sunoStatus.connected ? 'Session Active' : 'Session Expired' }}
              </p>
              <p class="text-xs text-studio-slate">{{ sunoStatus.message }}</p>
            </div>
            <button
              @click="refreshSunoStatus"
              :disabled="isRefreshingSuno"
              class="px-4 py-2 text-sm font-condensed uppercase tracking-wider border border-studio-amber/50 text-studio-amber rounded-sm hover:bg-studio-amber/10 transition-all disabled:opacity-50"
            >
              {{ isRefreshingSuno ? 'Checking...' : 'Refresh' }}
            </button>
          </div>

          <p class="text-xs text-studio-slate">
            Run setup script to create session: <code class="text-studio-amber">python tools/suno_auth_setup.py</code>
          </p>
        </div>
      </div>

      <!-- YouTube Integration Card -->
      <div
        class="card-static"
        :style="{
          opacity: mounted ? 1 : 0,
          transform: mounted ? 'translateY(0)' : 'translateY(20px)',
          transition: 'all 0.5s ease-out 0.15s'
        }"
      >
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-full bg-studio-error/20 flex items-center justify-center">
            <svg class="w-5 h-5 text-studio-error" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
          </div>
          <div>
            <h3 class="text-lg font-semibold text-studio-cream">YouTube Integration</h3>
            <p class="text-sm text-studio-slate">Connect your YouTube channel</p>
          </div>
        </div>

        <div class="space-y-4">
          <!-- Status Indicator -->
          <div class="flex items-center gap-3 p-3 rounded-lg bg-studio-charcoal/50">
            <div
              class="w-2.5 h-2.5 rounded-full"
              :class="youtubeStatus.connected ? 'bg-studio-vu-green' : 'bg-studio-vu-yellow'"
              :style="{ boxShadow: youtubeStatus.connected ? '0 0 8px rgba(74, 222, 128, 0.6)' : '0 0 8px rgba(250, 204, 21, 0.6)' }"
            ></div>
            <div class="flex-1">
              <p class="text-sm font-medium text-studio-cream">
                {{ youtubeStatus.connected ? 'Connected' : 'Not Connected' }}
              </p>
              <p class="text-xs text-studio-slate">{{ youtubeStatus.message }}</p>
            </div>
            <button
              @click="connectYouTube"
              :disabled="isConnectingYouTube"
              class="px-4 py-2 text-sm font-condensed uppercase tracking-wider bg-studio-amber text-studio-void rounded-sm hover:bg-studio-gold transition-all disabled:opacity-50"
            >
              {{ isConnectingYouTube ? 'Connecting...' : 'Connect YouTube' }}
            </button>
          </div>

          <p class="text-xs text-studio-slate">
            One-time authorization required. After connecting, uploads work automatically.
          </p>
        </div>
      </div>

      <!-- Automation Card -->
      <div
        class="card-static"
        :style="{
          opacity: mounted ? 1 : 0,
          transform: mounted ? 'translateY(0)' : 'translateY(20px)',
          transition: 'all 0.5s ease-out 0.2s'
        }"
      >
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-full bg-studio-bronze/20 flex items-center justify-center">
            <svg class="w-5 h-5 text-studio-bronze" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <div>
            <h3 class="text-lg font-semibold text-studio-cream">Automation</h3>
            <p class="text-sm text-studio-slate">Pipeline automation preferences</p>
          </div>
        </div>

        <div class="space-y-6">
          <!-- Auto Upload Toggle -->
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-studio-cream">Auto Upload to YouTube</p>
              <p class="text-xs text-studio-slate">Automatically upload approved songs</p>
            </div>
            <button
              @click="automationSettings.autoUpload = !automationSettings.autoUpload"
              class="toggle-track"
              :class="{ 'active': automationSettings.autoUpload }"
            >
              <span class="toggle-thumb"></span>
            </button>
          </div>

          <!-- Quality Threshold -->
          <div>
            <div class="flex items-center justify-between mb-2">
              <p class="text-xs font-condensed uppercase tracking-wider text-studio-slate">Quality Threshold</p>
              <span class="text-lg font-display text-studio-amber">{{ automationSettings.qualityThreshold }}</span>
            </div>
            <input
              v-model.number="automationSettings.qualityThreshold"
              type="range"
              min="1"
              max="5"
              step="1"
              class="w-full h-1.5 bg-studio-charcoal rounded-full appearance-none cursor-pointer quality-slider"
            />
            <div class="flex justify-between text-xs text-studio-slate mt-2">
              <span>1</span>
              <span>2</span>
              <span>3</span>
              <span>4</span>
              <span>5</span>
            </div>
            <p class="text-xs text-studio-slate mt-2">Minimum rating required for auto-approval</p>
          </div>
        </div>
      </div>

      <!-- System Info Card -->
      <div
        class="card-static"
        :style="{
          opacity: mounted ? 1 : 0,
          transform: mounted ? 'translateY(0)' : 'translateY(20px)',
          transition: 'all 0.5s ease-out 0.25s'
        }"
      >
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-full bg-studio-info/20 flex items-center justify-center">
            <svg class="w-5 h-5 text-studio-info" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <h3 class="text-lg font-semibold text-studio-cream">System Info</h3>
            <p class="text-sm text-studio-slate">Application information</p>
          </div>
        </div>

        <div class="space-y-3">
          <!-- Version -->
          <div class="flex items-center justify-between py-2 border-b border-studio-charcoal/50">
            <span class="text-sm text-studio-sand">Version</span>
            <span class="text-sm font-mono text-studio-cream">{{ systemInfo.version }}</span>
          </div>

          <!-- Database Status -->
          <div class="flex items-center justify-between py-2 border-b border-studio-charcoal/50">
            <span class="text-sm text-studio-sand">Database</span>
            <span
              class="text-sm font-medium"
              :class="systemInfo.databaseConnected ? 'text-studio-success' : 'text-studio-error'"
            >
              {{ systemInfo.databaseConnected ? 'Connected' : 'Disconnected' }}
            </span>
          </div>

          <!-- File Watcher Status -->
          <div class="flex items-center justify-between py-2">
            <span class="text-sm text-studio-sand">File Watcher</span>
            <span
              class="text-sm font-medium"
              :class="systemInfo.fileWatcherActive ? 'text-studio-success' : 'text-studio-error'"
            >
              {{ systemInfo.fileWatcherActive ? 'Active' : 'Inactive' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Save Button -->
    <div
      class="flex justify-center"
      :style="{
        opacity: mounted ? 1 : 0,
        transform: mounted ? 'translateY(0)' : 'translateY(20px)',
        transition: 'all 0.5s ease-out 0.3s'
      }"
    >
      <button
        @click="saveSettings"
        :disabled="isSaving"
        class="px-12 py-3 text-sm font-condensed uppercase tracking-wider border-2 border-studio-amber/50 text-studio-amber rounded-sm hover:border-studio-amber hover:bg-studio-amber/10 transition-all disabled:opacity-50"
      >
        <span class="flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          {{ isSaving ? 'Saving...' : 'Save Settings' }}
        </span>
      </button>
    </div>

    <!-- Save Confirmation Toast -->
    <Transition name="toast">
      <div
        v-if="showSaveConfirmation"
        class="fixed bottom-6 right-6 px-6 py-3 bg-studio-success text-studio-void font-medium rounded-sm shadow-lg"
      >
        Settings saved successfully!
      </div>
    </Transition>
  </div>
</template>

<style scoped>
/* Quality threshold slider */
.quality-slider::-webkit-slider-thumb {
  appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #d4a574;
  cursor: pointer;
  box-shadow: 0 0 10px rgba(212, 165, 116, 0.5);
}

.quality-slider::-moz-range-thumb {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #d4a574;
  cursor: pointer;
  border: none;
  box-shadow: 0 0 10px rgba(212, 165, 116, 0.5);
}

/* Toast animation */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(20px);
}
</style>
