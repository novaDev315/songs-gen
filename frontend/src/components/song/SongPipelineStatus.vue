<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  status: string
  hasAudio: boolean
  hasVideo: boolean
  youtubeUrl?: string | null
}>()

interface PipelineStage {
  key: string
  label: string
  icon: string
  completed: boolean
  current: boolean
}

const stages = computed<PipelineStage[]>(() => {
  const isPublished = props.status === 'uploaded' || !!props.youtubeUrl

  return [
    {
      key: 'created',
      label: 'Created',
      icon: '✓',
      completed: true,
      current: !props.hasAudio && !props.hasVideo && !isPublished
    },
    {
      key: 'audio',
      label: 'Audio Ready',
      icon: '♪',
      completed: props.hasAudio,
      current: props.hasAudio && !props.hasVideo && !isPublished
    },
    {
      key: 'video',
      label: 'Video Ready',
      icon: '▶',
      completed: props.hasVideo,
      current: props.hasVideo && !isPublished
    },
    {
      key: 'published',
      label: 'Published',
      icon: '📺',
      completed: isPublished,
      current: isPublished
    }
  ]
})

const currentStageIndex = computed(() => {
  const idx = stages.value.findIndex(s => s.current)
  return idx >= 0 ? idx : 0
})
</script>

<template>
  <div class="pipeline-container">
    <h3 class="text-sm font-semibold text-studio-slate uppercase tracking-wider mb-4">Pipeline Status</h3>

    <div class="flex items-center justify-between relative">
      <!-- Progress line background -->
      <div class="absolute top-5 left-8 right-8 h-0.5 bg-studio-charcoal"></div>

      <!-- Progress line filled -->
      <div
        class="absolute top-5 left-8 h-0.5 bg-gradient-to-r from-emerald-500 to-amber-500 transition-all duration-500"
        :style="{ width: `calc(${(currentStageIndex / (stages.length - 1)) * 100}% - 4rem)` }"
      ></div>

      <!-- Stages -->
      <div
        v-for="(stage, index) in stages"
        :key="stage.key"
        class="relative flex flex-col items-center z-10"
      >
        <!-- Stage circle -->
        <div
          :class="[
            'w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold transition-all duration-300',
            stage.completed
              ? 'bg-gradient-to-br from-emerald-500 to-emerald-600 text-white shadow-lg shadow-emerald-500/30'
              : stage.current
                ? 'bg-gradient-to-br from-amber-500 to-orange-500 text-white shadow-lg shadow-amber-500/30 animate-pulse'
                : 'bg-studio-charcoal text-studio-slate'
          ]"
        >
          {{ stage.icon }}
        </div>

        <!-- Stage label -->
        <span
          :class="[
            'mt-2 text-xs font-medium whitespace-nowrap',
            stage.completed
              ? 'text-emerald-400'
              : stage.current
                ? 'text-amber-400'
                : 'text-studio-slate'
          ]"
        >
          {{ stage.label }}
        </span>
      </div>
    </div>

    <!-- Status message -->
    <div class="mt-6 text-center">
      <span
        :class="[
          'inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium',
          props.status === 'uploaded' || props.youtubeUrl
            ? 'bg-emerald-500/20 text-emerald-400'
            : props.hasVideo
              ? 'bg-amber-500/20 text-amber-400'
              : props.hasAudio
                ? 'bg-blue-500/20 text-blue-400'
                : 'bg-studio-charcoal text-studio-slate'
        ]"
      >
        <span class="w-2 h-2 rounded-full animate-pulse" :class="[
          props.status === 'uploaded' || props.youtubeUrl
            ? 'bg-emerald-400'
            : props.hasVideo
              ? 'bg-amber-400'
              : props.hasAudio
                ? 'bg-blue-400'
                : 'bg-studio-slate'
        ]"></span>
        {{ props.status === 'uploaded' || props.youtubeUrl
          ? 'Published to YouTube'
          : props.hasVideo
            ? 'Ready to publish'
            : props.hasAudio
              ? 'Video not generated'
              : 'Audio not ready'
        }}
      </span>
    </div>
  </div>
</template>

<style scoped>
.pipeline-container {
  @apply bg-studio-charcoal/30 rounded-xl p-6;
}
</style>
