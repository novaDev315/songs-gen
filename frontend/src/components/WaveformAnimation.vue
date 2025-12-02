<script setup lang="ts">
</script>

<template>
  <div class="flex items-end justify-center gap-1 h-8">
    <div v-for="i in 8" :key="i" class="waveform-bar" :style="{ height: '20%' }" />
  </div>
</template>
