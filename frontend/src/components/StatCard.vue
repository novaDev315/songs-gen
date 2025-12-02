<script setup lang="ts">
defineProps<{
  value: string | number
  label: string
  accent?: 'cyan' | 'magenta' | 'gold' | 'purple'
  trend?: { value: string; positive: boolean }
}>()
</script>

<template>
  <div :class="['stat-card', accent || 'cyan']">
    <div class="font-display text-4xl font-bold text-sf-text-primary">
      {{ value }}
    </div>
    <div class="text-xs text-sf-text-muted uppercase tracking-widest mt-2">
      {{ label }}
    </div>
    <div v-if="trend" :class="['text-xs mt-2', trend.positive ? 'text-sf-status-success' : 'text-sf-status-error']">
      {{ trend.positive ? '↑' : '↓' }} {{ trend.value }}
    </div>
  </div>
</template>
