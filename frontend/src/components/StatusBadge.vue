<script setup lang="ts">
defineProps<{
  status: string
}>()

const statusClasses: Record<string, string> = {
  pending: 'status-pending',
  running: 'status-running',
  generating: 'status-running',
  completed: 'status-completed',
  downloaded: 'status-completed',
  evaluated: 'status-completed',
  uploaded: 'status-completed',
  failed: 'status-failed',
}
</script>

<template>
  <span :class="['status-badge', statusClasses[status] || 'status-pending']">
    <span class="led-indicator" :class="statusClasses[status]?.replace('status-', 'bg-sf-status-')" />
    {{ status.toUpperCase() }}
  </span>
</template>
