<script setup lang="ts">
import { ref, computed } from 'vue'
import { useStudioStore } from '@/stores/studio'

const store = useStudioStore()
const selectedMethod = ref<'template' | 'ai' | 'upload' | null>(null)
const selectedTemplate = ref<string | null>(null)
const aiPrompt = ref('')
const uploadedFile = ref<File | null>(null)
const previewUrl = ref<string | null>(null)
const mounted = ref(true)

const templates = {
  pop: ['gradient_bright', 'neon_city', 'abstract_colorful'],
  rock: ['dark_grunge', 'fire_smoke', 'electric'],
  'hip-hop': ['urban_night', 'gold_chains', 'street_art'],
  edm: ['laser_grid', 'spectrum', 'dj_silhouette'],
  jazz: ['vintage_sepia', 'piano_keys', 'smoky_club'],
  country: ['sunset_field', 'acoustic_wood', 'barn'],
}

const genreTemplates = computed(() => {
  const genre = store.selectedSong?.genre?.toLowerCase() || 'pop'
  return templates[genre as keyof typeof templates] || templates.pop
})

const methods = [
  { id: 'template', name: 'Template', description: 'Free & instant', icon: 'M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z' },
  { id: 'ai', name: 'AI Generated', description: 'Unique designs', icon: 'M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z' },
  { id: 'upload', name: 'Upload', description: 'Your own image', icon: 'M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12' },
]

async function generateTemplate(templateId: string) {
  selectedTemplate.value = templateId
  await store.generateTemplateCover(templateId)
}

async function generateAI() {
  await store.generateAICover(aiPrompt.value || undefined)
}

function handleFileUpload(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    uploadedFile.value = file
    previewUrl.value = URL.createObjectURL(file)
  }
}

async function uploadFile() {
  if (uploadedFile.value) {
    await store.uploadCover(uploadedFile.value)
  }
}

function skipCover() {
  store.cover.type = 'skip'
}

function formatTemplateName(name: string): string {
  return name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}
</script>

<template>
  <div class="space-y-6">
    <!-- Step Header -->
    <div>
      <div class="flex items-center gap-2 mb-2">
        <div class="led-indicator rose"></div>
        <span class="text-xs font-condensed text-studio-stone uppercase tracking-widest">Cover Design</span>
      </div>
      <h2 class="text-xl font-display font-semibold text-studio-cream">Cover Art</h2>
      <p class="text-sm text-studio-sand mt-1">Create or upload your video thumbnail</p>
    </div>

    <!-- Method Selection -->
    <div class="grid gap-3 md:grid-cols-3">
      <button
        v-for="(method, index) in methods"
        :key="method.id"
        @click="selectedMethod = method.id as any"
        class="group relative p-5 rounded-xl text-center transition-all duration-300 border"
        :class="[
          selectedMethod === method.id
            ? 'bg-studio-rose-500/10 border-studio-rose-500/50'
            : 'bg-studio-charcoal/30 border-studio-graphite/40 hover:bg-studio-charcoal/50 hover:border-studio-rose-500/20'
        ]"
        :style="{
          opacity: mounted ? 1 : 0,
          transform: mounted ? 'translateY(0)' : 'translateY(10px)',
          transition: `all 0.3s ease-out ${index * 0.05}s`
        }"
      >
        <div
          class="w-14 h-14 mx-auto mb-3 rounded-xl flex items-center justify-center transition-all duration-300"
          :class="[
            selectedMethod === method.id
              ? 'bg-studio-rose-500/20'
              : 'bg-studio-graphite/50 group-hover:bg-studio-rose-500/10'
          ]"
        >
          <svg
            class="w-7 h-7 transition-colors"
            :class="[
              selectedMethod === method.id
                ? 'text-studio-rose-400'
                : 'text-studio-sand group-hover:text-studio-rose-400'
            ]"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" :d="method.icon" />
          </svg>
        </div>
        <div class="font-medium text-studio-cream">{{ method.name }}</div>
        <div class="text-xs text-studio-stone mt-1">{{ method.description }}</div>

        <!-- Selection Indicator -->
        <div v-if="selectedMethod === method.id" class="absolute top-3 right-3">
          <div class="led-indicator green"></div>
        </div>
      </button>
    </div>

    <!-- Template Selection -->
    <div v-if="selectedMethod === 'template'" class="space-y-4">
      <div class="flex items-center gap-2">
        <div class="w-1.5 h-1.5 rounded-full bg-studio-amber"></div>
        <h3 class="text-sm font-condensed text-studio-sand uppercase tracking-wider">Select Template</h3>
      </div>

      <div class="grid gap-3 grid-cols-3">
        <button
          v-for="template in genreTemplates"
          :key="template"
          @click="generateTemplate(template)"
          class="group p-4 rounded-xl text-center transition-all duration-300 border"
          :class="[
            selectedTemplate === template
              ? 'bg-studio-success/10 border-studio-success/50'
              : 'bg-studio-charcoal/30 border-studio-graphite/40 hover:bg-studio-charcoal/50 hover:border-studio-rose-500/20'
          ]"
        >
          <div
            class="w-10 h-10 mx-auto mb-2 rounded-lg flex items-center justify-center"
            :class="[
              selectedTemplate === template
                ? 'bg-studio-success/20'
                : 'bg-studio-graphite/50'
            ]"
          >
            <svg class="w-5 h-5" :class="selectedTemplate === template ? 'text-studio-success' : 'text-studio-slate'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <div class="text-sm text-studio-cream capitalize">{{ formatTemplateName(template) }}</div>
        </button>
      </div>
    </div>

    <!-- AI Generation -->
    <div v-if="selectedMethod === 'ai'" class="space-y-4">
      <div class="flex items-center gap-2">
        <div class="w-1.5 h-1.5 rounded-full bg-studio-violet-500"></div>
        <h3 class="text-sm font-condensed text-studio-sand uppercase tracking-wider">AI Cover Generation</h3>
      </div>

      <div class="space-y-3">
        <label class="input-label">Describe your cover (optional)</label>
        <textarea
          v-model="aiPrompt"
          placeholder="Leave empty to auto-generate based on song mood, or describe your vision..."
          class="input-field h-24 resize-none"
        ></textarea>
      </div>

      <button
        @click="generateAI"
        :disabled="store.isLoading"
        class="btn btn-primary w-full"
      >
        <svg v-if="store.isLoading" class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
        {{ store.isLoading ? 'Generating...' : 'Generate Cover' }}
      </button>
    </div>

    <!-- Upload -->
    <div v-if="selectedMethod === 'upload'" class="space-y-4">
      <div class="flex items-center gap-2">
        <div class="w-1.5 h-1.5 rounded-full bg-studio-gold"></div>
        <h3 class="text-sm font-condensed text-studio-sand uppercase tracking-wider">Upload Cover Image</h3>
      </div>

      <label class="flex flex-col items-center justify-center w-full h-48 rounded-xl cursor-pointer transition-all duration-300 border-2 border-dashed border-studio-graphite/60 hover:border-studio-rose-500/50 bg-studio-charcoal/20 hover:bg-studio-charcoal/40">
        <div v-if="!previewUrl" class="text-center">
          <div class="w-14 h-14 mx-auto mb-3 rounded-xl bg-studio-graphite/50 flex items-center justify-center">
            <svg class="w-7 h-7 text-studio-slate" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
          </div>
          <p class="text-studio-sand">Click to upload or drag and drop</p>
          <p class="text-studio-slate text-xs mt-1">PNG, JPG up to 5MB</p>
        </div>
        <img v-else :src="previewUrl" class="h-full object-contain rounded-lg" />
        <input type="file" class="hidden" accept="image/*" @change="handleFileUpload" />
      </label>

      <button
        v-if="uploadedFile"
        @click="uploadFile"
        :disabled="store.isLoading"
        class="btn btn-primary w-full"
      >
        <svg v-if="store.isLoading" class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M5 13l4 4L19 7" />
        </svg>
        {{ store.isLoading ? 'Uploading...' : 'Use This Cover' }}
      </button>
    </div>

    <!-- Cover Preview -->
    <div v-if="store.cover.path" class="stat-card rose">
      <div class="flex items-center gap-2 mb-4">
        <div class="led-indicator green"></div>
        <h3 class="text-sm font-condensed text-studio-sand uppercase tracking-wider">Cover Preview</h3>
      </div>
      <div class="flex justify-center">
        <img :src="'/api/v1' + store.cover.path" class="max-h-48 rounded-xl shadow-lg" />
      </div>
    </div>

    <!-- Skip Option -->
    <div class="pt-2">
      <button
        @click="skipCover"
        class="text-studio-slate hover:text-studio-sand text-sm transition-colors flex items-center gap-2"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
        </svg>
        Skip for now (use default)
      </button>
    </div>
  </div>
</template>
