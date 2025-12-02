<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useStudioStore } from '@/stores/studio'

const store = useStudioStore()

const visualStyles = [
  { id: 'lyric', name: 'Lyric Video', icon: 'M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z', description: 'Animated lyrics with cover art', backendStyle: 'lyric' },
  { id: 'waveform', name: 'Waveform', icon: 'M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3', description: 'Animated audio waveform', backendStyle: 'waveform' },
  { id: 'text_overlay', name: 'Title Overlay', icon: 'M4 6h16M4 12h16m-7 6h7', description: 'Song title over cover art', backendStyle: 'text_overlay' },
  { id: 'static', name: 'Static Cover', icon: 'M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z', description: 'Just the cover art', backendStyle: 'static' },
]

const lyricStyles = [
  { id: 'fade', name: 'Fade In/Out', description: 'Smooth fade transitions', icon: 'M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z' },
  { id: 'karaoke', name: 'Karaoke', description: 'Highlight words as they play', icon: 'M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3' },
  { id: 'scroll', name: 'Scroll', description: 'Scrolling credits style', icon: 'M19 14l-7 7m0 0l-7-7m7 7V3' },
]

const colorThemes = [
  { id: 'genre_based', name: 'Genre Based', colors: ['#f59e0b', '#ec4899', '#8b5cf6'] },
  { id: 'monochrome', name: 'Monochrome', colors: ['#ffffff', '#94a3b8', '#334155'] },
  { id: 'neon', name: 'Neon', colors: ['#00ffff', '#ff00ff', '#ffff00'] },
  { id: 'warm', name: 'Warm', colors: ['#f97316', '#fbbf24', '#ef4444'] },
  { id: 'cool', name: 'Cool', colors: ['#06b6d4', '#3b82f6', '#8b5cf6'] },
  { id: 'custom', name: 'Custom', colors: [] },
]

function getBackendStyle(uiStyle: string): string {
  const style = visualStyles.find(s => s.id === uiStyle)
  return style?.backendStyle || 'lyric'
}

const selectedStyle = computed({
  get: () => store.videoSettings.visualStyle,
  set: (value) => {
    store.updateVideoSettings({ visualStyle: value })
    store.video.style = getBackendStyle(value) as any
  }
})

const selectedLyricStyle = computed({
  get: () => store.video.lyricStyle,
  set: (value) => {
    store.video.lyricStyle = value
  }
})

const selectedTheme = computed({
  get: () => store.videoSettings.colorTheme,
  set: (value) => store.updateVideoSettings({ colorTheme: value })
})

const customColors = ref({
  primary: '#f59e0b',
  secondary: '#ec4899',
  accent: '#8b5cf6'
})

watch([() => store.videoSettings, () => store.video], () => {
  if (store.projectId) {
    store.updateProject()
  }
}, { deep: true })

function selectStyle(styleId: string) {
  selectedStyle.value = styleId
}

function selectTheme(themeId: string) {
  selectedTheme.value = themeId
  if (themeId === 'custom') {
    store.updateVideoSettings({ customColors: customColors.value })
  }
}

function updateCustomColor(key: string, value: string) {
  customColors.value[key as keyof typeof customColors.value] = value
  if (selectedTheme.value === 'custom') {
    store.updateVideoSettings({ customColors: customColors.value })
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Step Header -->
    <div>
      <div class="flex items-center gap-2 mb-2">
        <div class="led-indicator violet"></div>
        <span class="text-xs font-condensed text-studio-stone uppercase tracking-widest">Video Configuration</span>
      </div>
      <h2 class="text-xl font-display font-semibold text-studio-cream">Video Settings</h2>
      <p class="text-sm text-studio-sand mt-1">Customize the visual style of your production</p>
    </div>

    <!-- Visual Style Selection -->
    <div class="space-y-4">
      <div class="flex items-center gap-2">
        <div class="w-1.5 h-1.5 rounded-full bg-studio-rose-500"></div>
        <h3 class="text-sm font-condensed text-studio-sand uppercase tracking-wider">Visual Style</h3>
      </div>

      <div class="grid gap-3 md:grid-cols-2">
        <button
          v-for="style in visualStyles"
          :key="style.id"
          @click="selectStyle(style.id)"
          class="group relative p-4 rounded-xl text-left transition-all duration-300 border"
          :class="[
            selectedStyle === style.id
              ? 'bg-studio-rose-500/10 border-studio-rose-500/50'
              : 'bg-studio-charcoal/30 border-studio-graphite/40 hover:bg-studio-charcoal/50 hover:border-studio-rose-500/20'
          ]"
        >
          <div v-if="selectedStyle === style.id" class="absolute top-3 right-3">
            <div class="led-indicator green"></div>
          </div>

          <div class="flex items-center gap-4">
            <div
              class="w-12 h-12 rounded-xl flex items-center justify-center transition-all duration-300"
              :class="[
                selectedStyle === style.id
                  ? 'bg-studio-rose-500/20'
                  : 'bg-studio-graphite/50 group-hover:bg-studio-rose-500/10'
              ]"
            >
              <svg
                class="w-6 h-6 transition-colors"
                :class="[
                  selectedStyle === style.id
                    ? 'text-studio-rose-400'
                    : 'text-studio-sand group-hover:text-studio-rose-400'
                ]"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" :d="style.icon" />
              </svg>
            </div>
            <div class="flex-1">
              <div class="font-medium text-studio-cream">{{ style.name }}</div>
              <div class="text-xs text-studio-stone mt-0.5">{{ style.description }}</div>
            </div>
          </div>
        </button>
      </div>
    </div>

    <!-- Lyric Style Selection -->
    <div v-if="selectedStyle === 'lyric'" class="space-y-4">
      <div class="flex items-center gap-2">
        <div class="w-1.5 h-1.5 rounded-full bg-studio-amber"></div>
        <h3 class="text-sm font-condensed text-studio-sand uppercase tracking-wider">Lyric Animation</h3>
      </div>

      <div class="grid gap-3 md:grid-cols-3">
        <button
          v-for="style in lyricStyles"
          :key="style.id"
          @click="selectedLyricStyle = style.id"
          class="group relative p-4 rounded-xl text-left transition-all duration-300 border"
          :class="[
            selectedLyricStyle === style.id
              ? 'bg-studio-amber/10 border-studio-amber/50'
              : 'bg-studio-charcoal/30 border-studio-graphite/40 hover:bg-studio-charcoal/50 hover:border-studio-amber/20'
          ]"
        >
          <div v-if="selectedLyricStyle === style.id" class="absolute top-2 right-2">
            <div class="led-indicator amber"></div>
          </div>

          <div class="w-10 h-10 rounded-lg mb-3 flex items-center justify-center"
            :class="[
              selectedLyricStyle === style.id
                ? 'bg-studio-amber/20'
                : 'bg-studio-graphite/50'
            ]"
          >
            <svg class="w-5 h-5" :class="selectedLyricStyle === style.id ? 'text-studio-amber' : 'text-studio-slate'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" :d="style.icon" />
            </svg>
          </div>
          <div class="font-medium text-studio-cream text-sm">{{ style.name }}</div>
          <div class="text-xs text-studio-stone mt-0.5">{{ style.description }}</div>
        </button>
      </div>
    </div>

    <!-- Color Theme Selection -->
    <div class="space-y-4">
      <div class="flex items-center gap-2">
        <div class="w-1.5 h-1.5 rounded-full bg-studio-gold"></div>
        <h3 class="text-sm font-condensed text-studio-sand uppercase tracking-wider">Color Theme</h3>
      </div>

      <div class="grid gap-3 md:grid-cols-3">
        <button
          v-for="theme in colorThemes"
          :key="theme.id"
          @click="selectTheme(theme.id)"
          class="group relative p-4 rounded-xl text-left transition-all duration-300 border"
          :class="[
            selectedTheme === theme.id
              ? 'bg-studio-gold/10 border-studio-gold/50'
              : 'bg-studio-charcoal/30 border-studio-graphite/40 hover:bg-studio-charcoal/50 hover:border-studio-gold/20'
          ]"
        >
          <div class="font-medium text-studio-cream text-sm mb-3">{{ theme.name }}</div>
          <div v-if="theme.colors.length > 0" class="flex gap-2">
            <div
              v-for="(color, idx) in theme.colors"
              :key="idx"
              class="w-6 h-6 rounded-lg border border-studio-graphite/50 shadow-inner"
              :style="{ backgroundColor: color }"
            ></div>
          </div>
          <div v-else class="flex gap-2">
            <div class="w-6 h-6 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500"></div>
            <span class="text-xs text-studio-slate self-center">Pick your own</span>
          </div>
        </button>
      </div>
    </div>

    <!-- Custom Color Picker -->
    <div v-if="selectedTheme === 'custom'" class="stat-card violet space-y-4">
      <div class="flex items-center gap-2">
        <div class="led-indicator violet pulsing"></div>
        <h3 class="text-sm font-condensed text-studio-sand uppercase tracking-wider">Custom Colors</h3>
      </div>

      <div class="grid gap-4 md:grid-cols-3">
        <div>
          <label class="input-label">Primary</label>
          <div class="flex items-center gap-3">
            <input
              type="color"
              :value="customColors.primary"
              @input="updateCustomColor('primary', ($event.target as HTMLInputElement).value)"
              class="w-12 h-12 rounded-lg cursor-pointer border border-studio-graphite/60 bg-transparent"
            />
            <input
              type="text"
              :value="customColors.primary"
              @input="updateCustomColor('primary', ($event.target as HTMLInputElement).value)"
              class="input-field flex-1 text-sm font-mono"
            />
          </div>
        </div>
        <div>
          <label class="input-label">Secondary</label>
          <div class="flex items-center gap-3">
            <input
              type="color"
              :value="customColors.secondary"
              @input="updateCustomColor('secondary', ($event.target as HTMLInputElement).value)"
              class="w-12 h-12 rounded-lg cursor-pointer border border-studio-graphite/60 bg-transparent"
            />
            <input
              type="text"
              :value="customColors.secondary"
              @input="updateCustomColor('secondary', ($event.target as HTMLInputElement).value)"
              class="input-field flex-1 text-sm font-mono"
            />
          </div>
        </div>
        <div>
          <label class="input-label">Accent</label>
          <div class="flex items-center gap-3">
            <input
              type="color"
              :value="customColors.accent"
              @input="updateCustomColor('accent', ($event.target as HTMLInputElement).value)"
              class="w-12 h-12 rounded-lg cursor-pointer border border-studio-graphite/60 bg-transparent"
            />
            <input
              type="text"
              :value="customColors.accent"
              @input="updateCustomColor('accent', ($event.target as HTMLInputElement).value)"
              class="input-field flex-1 text-sm font-mono"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Additional Settings -->
    <div class="space-y-4">
      <div class="flex items-center gap-2">
        <div class="w-1.5 h-1.5 rounded-full bg-studio-bronze"></div>
        <h3 class="text-sm font-condensed text-studio-sand uppercase tracking-wider">Additional Options</h3>
      </div>

      <div class="space-y-3">
        <!-- Show Title Toggle -->
        <div class="flex items-center justify-between p-4 rounded-xl bg-studio-charcoal/30 border border-studio-graphite/40">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-studio-graphite/50 flex items-center justify-center">
              <svg class="w-5 h-5 text-studio-sand" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
              </svg>
            </div>
            <div>
              <div class="font-medium text-studio-cream text-sm">Show Song Title</div>
              <div class="text-xs text-studio-stone">Display title overlay on video</div>
            </div>
          </div>
          <label class="toggle-track" :class="{ active: store.videoSettings.showTitle }">
            <input
              type="checkbox"
              :checked="store.videoSettings.showTitle"
              @change="store.updateVideoSettings({ showTitle: ($event.target as HTMLInputElement).checked })"
              class="sr-only"
            />
            <div class="toggle-thumb"></div>
          </label>
        </div>

        <!-- Show Artist Toggle -->
        <div class="flex items-center justify-between p-4 rounded-xl bg-studio-charcoal/30 border border-studio-graphite/40">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-studio-graphite/50 flex items-center justify-center">
              <svg class="w-5 h-5 text-studio-sand" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <div>
              <div class="font-medium text-studio-cream text-sm">Show Artist Name</div>
              <div class="text-xs text-studio-stone">Display artist/creator name</div>
            </div>
          </div>
          <label class="toggle-track" :class="{ active: store.videoSettings.showArtist }">
            <input
              type="checkbox"
              :checked="store.videoSettings.showArtist"
              @change="store.updateVideoSettings({ showArtist: ($event.target as HTMLInputElement).checked })"
              class="sr-only"
            />
            <div class="toggle-thumb"></div>
          </label>
        </div>

        <!-- High Quality Toggle -->
        <div class="flex items-center justify-between p-4 rounded-xl bg-studio-charcoal/30 border border-studio-graphite/40">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-studio-graphite/50 flex items-center justify-center">
              <svg class="w-5 h-5 text-studio-sand" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <div>
              <div class="font-medium text-studio-cream text-sm">High Quality (1080p)</div>
              <div class="text-xs text-studio-stone">Render at 1920x1080 resolution</div>
            </div>
          </div>
          <label class="toggle-track" :class="{ active: store.videoSettings.highQuality }">
            <input
              type="checkbox"
              :checked="store.videoSettings.highQuality"
              @change="store.updateVideoSettings({ highQuality: ($event.target as HTMLInputElement).checked })"
              class="sr-only"
            />
            <div class="toggle-thumb"></div>
          </label>
        </div>
      </div>
    </div>
  </div>
</template>
