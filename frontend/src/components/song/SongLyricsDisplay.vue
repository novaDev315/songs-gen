<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  lyrics: string
}>()

interface LyricSection {
  type: 'tag' | 'line'
  content: string
  tagType?: string
}

// Map structure tags to colors
const tagColors: Record<string, string> = {
  verse: 'text-blue-400',
  chorus: 'text-amber-400',
  bridge: 'text-purple-400',
  intro: 'text-emerald-400',
  outro: 'text-emerald-400',
  'pre-chorus': 'text-orange-400',
  hook: 'text-amber-400',
  breakdown: 'text-pink-400',
  interlude: 'text-teal-400',
  instrumental: 'text-cyan-400',
  solo: 'text-cyan-400',
  default: 'text-studio-slate'
}

const parsedLyrics = computed<LyricSection[]>(() => {
  if (!props.lyrics) return []

  const lines = props.lyrics.split('\n')
  const sections: LyricSection[] = []

  for (const line of lines) {
    const trimmed = line.trim()

    // Check if line is a structure tag like [Verse], [Chorus], etc.
    const tagMatch = trimmed.match(/^\[([^\]]+)\]$/)
    if (tagMatch) {
      const tagContent = tagMatch[1].toLowerCase()
      // Determine tag type for coloring
      let tagType = 'default'
      for (const key of Object.keys(tagColors)) {
        if (tagContent.includes(key)) {
          tagType = key
          break
        }
      }
      sections.push({
        type: 'tag',
        content: tagMatch[1],
        tagType
      })
    } else if (trimmed) {
      sections.push({
        type: 'line',
        content: trimmed
      })
    } else {
      // Empty line for spacing
      sections.push({
        type: 'line',
        content: ''
      })
    }
  }

  return sections
})

function getTagColor(tagType: string): string {
  return tagColors[tagType] || tagColors.default
}
</script>

<template>
  <div class="lyrics-container">
    <div class="max-h-96 overflow-y-auto pr-2 custom-scrollbar">
      <div
        v-for="(section, index) in parsedLyrics"
        :key="index"
        :class="[
          section.type === 'tag'
            ? ['font-bold text-sm uppercase tracking-wider mt-4 mb-2 first:mt-0', getTagColor(section.tagType || 'default')]
            : section.content
              ? 'text-studio-cream leading-relaxed'
              : 'h-2'
        ]"
      >
        <template v-if="section.type === 'tag'">
          <span class="inline-flex items-center gap-2">
            <span class="w-2 h-2 rounded-full" :class="getTagColor(section.tagType || 'default').replace('text-', 'bg-')"></span>
            {{ section.content }}
          </span>
        </template>
        <template v-else>
          {{ section.content }}
        </template>
      </div>

      <div v-if="!parsedLyrics.length" class="text-studio-slate italic">
        No lyrics available
      </div>
    </div>
  </div>
</template>

<style scoped>
.lyrics-container {
  @apply bg-studio-charcoal/30 rounded-xl p-4;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  @apply bg-studio-void/50 rounded;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  @apply bg-studio-slate/50 rounded hover:bg-studio-slate/70;
}
</style>
