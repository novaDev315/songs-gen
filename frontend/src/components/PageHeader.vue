<script setup lang="ts">
defineProps<{
  title: string
  subtitle?: string
  icon?: string
}>()
</script>

<template>
  <div class="mb-8">
    <h1 class="font-display text-3xl font-bold flex items-center gap-3">
      <span v-if="icon" class="text-4xl">{{ icon }}</span>
      <span class="gradient-text">{{ title }}</span>
    </h1>
    <p v-if="subtitle" class="text-sf-text-secondary mt-2">{{ subtitle }}</p>
  </div>
</template>
