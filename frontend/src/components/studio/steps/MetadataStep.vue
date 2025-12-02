<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useStudioStore } from '@/stores/studio'

const store = useStudioStore()

const title = ref('')
const description = ref('')
const tags = ref<string[]>([])
const tagInput = ref('')
const category = ref('Music')
const privacy = ref('public')

const categories = [
  'Music',
  'Entertainment',
  'Education',
  'How-to & Style',
  'People & Blogs',
  'Gaming',
  'Film & Animation',
]

const privacyOptions = [
  { value: 'public', label: 'Public', description: 'Anyone can watch', icon: 'M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z' },
  { value: 'unlisted', label: 'Unlisted', description: 'Only people with link', icon: 'M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1' },
  { value: 'private', label: 'Private', description: 'Only you', icon: 'M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z' },
]

const suggestedTags = computed(() => {
  const genre = store.selectedSong?.genre?.toLowerCase() || 'music'
  const baseTags = [
    genre,
    `${genre} music`,
    'ai music',
    'suno ai',
    'ai generated',
    'music video',
  ]
  return baseTags.filter(tag => !tags.value.includes(tag))
})

onMounted(() => {
  if (store.selectedSong) {
    title.value = store.selectedSong.title || ''
    description.value = generateDescription()
    tags.value = generateDefaultTags()
  }
})

function generateDescription(): string {
  const song = store.selectedSong
  if (!song) return ''

  return `${song.title} - ${song.genre} Music

Created with Suno AI

🎵 Genre: ${song.genre}
🎤 Style: ${song.style_prompt || 'AI Generated'}

${song.lyrics ? '📝 Lyrics:\n' + song.lyrics.substring(0, 500) : ''}

#AIMusic #SunoAI #${song.genre.replace(/\s+/g, '')}

Generated using AI music generation technology.`
}

function generateDefaultTags(): string[] {
  const genre = store.selectedSong?.genre?.toLowerCase() || 'music'
  return [
    genre,
    `${genre} music`,
    'ai music',
    'suno ai',
    'ai generated music',
  ]
}

function addTag(tag: string) {
  const cleanTag = tag.trim().toLowerCase()
  if (cleanTag && !tags.value.includes(cleanTag) && tags.value.length < 15) {
    tags.value.push(cleanTag)
    tagInput.value = ''
    updateMetadata()
  }
}

function removeTag(index: number) {
  tags.value.splice(index, 1)
  updateMetadata()
}

function handleTagInput(event: KeyboardEvent) {
  if (event.key === 'Enter') {
    event.preventDefault()
    addTag(tagInput.value)
  } else if (event.key === 'Backspace' && !tagInput.value && tags.value.length > 0) {
    removeTag(tags.value.length - 1)
  }
}

function updateMetadata() {
  store.updateMetadata({
    title: title.value,
    description: description.value,
    tags: tags.value,
    category: category.value,
    privacy: privacy.value,
  })
}

const watchTitle = computed(() => {
  updateMetadata()
  return title.value
})

const watchDescription = computed(() => {
  updateMetadata()
  return description.value
})
</script>

<template>
  <div class="space-y-6">
    <!-- Step Header -->
    <div>
      <div class="flex items-center gap-2 mb-2">
        <div class="led-indicator gold"></div>
        <span class="text-xs font-condensed text-studio-stone uppercase tracking-widest">Publishing Details</span>
      </div>
      <h2 class="text-xl font-display font-semibold text-studio-cream">Video Metadata</h2>
      <p class="text-sm text-studio-sand mt-1">Set title, description, tags, and YouTube details</p>
    </div>

    <!-- Title -->
    <div class="space-y-2">
      <div class="flex items-center justify-between">
        <label class="input-label">Title</label>
        <span class="text-xs text-studio-slate font-mono">{{ title.length }}/100</span>
      </div>
      <input
        v-model="title"
        type="text"
        maxlength="100"
        placeholder="Enter video title..."
        class="input-field"
        @input="watchTitle"
      />
      <p class="text-xs text-studio-slate">Make it catchy and descriptive</p>
    </div>

    <!-- Description -->
    <div class="space-y-2">
      <div class="flex items-center justify-between">
        <label class="input-label">Description</label>
        <span class="text-xs text-studio-slate font-mono">{{ description.length }}/5000</span>
      </div>
      <textarea
        v-model="description"
        maxlength="5000"
        placeholder="Enter video description..."
        class="input-field h-40 resize-none"
        @input="watchDescription"
      ></textarea>
      <p class="text-xs text-studio-slate">Include relevant information and links</p>
    </div>

    <!-- Tags -->
    <div class="space-y-3">
      <div class="flex items-center justify-between">
        <label class="input-label">Tags</label>
        <span class="text-xs text-studio-slate font-mono">{{ tags.length }}/15</span>
      </div>

      <!-- Tag Input Area -->
      <div class="p-3 rounded-xl bg-studio-charcoal/50 border border-studio-graphite/60 focus-within:border-studio-rose-500/50 transition-colors">
        <div class="flex flex-wrap gap-2">
          <div
            v-for="(tag, idx) in tags"
            :key="idx"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-studio-rose-500/20 text-studio-rose-400 text-sm"
          >
            <span>{{ tag }}</span>
            <button
              @click="removeTag(idx)"
              class="hover:text-studio-cream transition-colors"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <input
            v-model="tagInput"
            type="text"
            placeholder="Add tags..."
            class="flex-1 min-w-[120px] bg-transparent text-studio-cream placeholder:text-studio-slate outline-none text-sm"
            @keydown="handleTagInput"
            :disabled="tags.length >= 15"
          />
        </div>
      </div>

      <!-- Suggested Tags -->
      <div v-if="suggestedTags.length > 0" class="space-y-2">
        <p class="text-xs text-studio-stone">Suggested tags:</p>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="tag in suggestedTags.slice(0, 8)"
            :key="tag"
            @click="addTag(tag)"
            class="px-3 py-1.5 rounded-lg text-sm bg-studio-charcoal/30 border border-studio-graphite/40 text-studio-sand hover:border-studio-rose-500/30 hover:text-studio-rose-400 transition-all"
          >
            <span class="text-studio-rose-400 mr-1">+</span>{{ tag }}
          </button>
        </div>
      </div>
    </div>

    <!-- Category -->
    <div class="space-y-2">
      <label class="input-label">Category</label>
      <select
        v-model="category"
        @change="updateMetadata"
        class="input-field"
      >
        <option v-for="cat in categories" :key="cat" :value="cat">
          {{ cat }}
        </option>
      </select>
    </div>

    <!-- Privacy -->
    <div class="space-y-3">
      <label class="input-label">Privacy</label>
      <div class="grid gap-3 md:grid-cols-3">
        <button
          v-for="option in privacyOptions"
          :key="option.value"
          @click="privacy = option.value; updateMetadata()"
          class="group relative p-4 rounded-xl text-left transition-all duration-300 border"
          :class="[
            privacy === option.value
              ? 'bg-studio-gold/10 border-studio-gold/50'
              : 'bg-studio-charcoal/30 border-studio-graphite/40 hover:bg-studio-charcoal/50 hover:border-studio-gold/20'
          ]"
        >
          <div v-if="privacy === option.value" class="absolute top-2 right-2">
            <div class="led-indicator green"></div>
          </div>

          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg flex items-center justify-center"
              :class="privacy === option.value ? 'bg-studio-gold/20' : 'bg-studio-graphite/50'"
            >
              <svg class="w-5 h-5" :class="privacy === option.value ? 'text-studio-gold' : 'text-studio-slate'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" :d="option.icon" />
              </svg>
            </div>
            <div class="flex-1">
              <div class="font-medium text-studio-cream text-sm">{{ option.label }}</div>
              <div class="text-xs text-studio-stone">{{ option.description }}</div>
            </div>
          </div>
        </button>
      </div>
    </div>

    <!-- Preview Summary -->
    <div class="stat-card gold">
      <div class="flex items-center gap-2 mb-4">
        <div class="led-indicator amber"></div>
        <h3 class="text-sm font-condensed text-studio-sand uppercase tracking-wider">Summary</h3>
      </div>
      <div class="space-y-2 text-sm">
        <div class="flex items-center justify-between py-2 border-b border-studio-graphite/30">
          <span class="text-studio-stone">Title</span>
          <span class="text-studio-cream font-medium truncate ml-4 max-w-[60%]">{{ title || '(No title)' }}</span>
        </div>
        <div class="flex items-center justify-between py-2 border-b border-studio-graphite/30">
          <span class="text-studio-stone">Category</span>
          <span class="text-studio-cream">{{ category }}</span>
        </div>
        <div class="flex items-center justify-between py-2 border-b border-studio-graphite/30">
          <span class="text-studio-stone">Privacy</span>
          <span class="text-studio-cream capitalize">{{ privacy }}</span>
        </div>
        <div class="flex items-center justify-between py-2">
          <span class="text-studio-stone">Tags</span>
          <span class="text-studio-cream">{{ tags.length }} tags</span>
        </div>
      </div>
    </div>
  </div>
</template>
