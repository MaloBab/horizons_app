<template>
  <button
    class="flex items-center justify-center gap-0.5 min-w-7 h-7 px-1.5 rounded-lg transition-all text-xs"
    :class="active
      ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
      : 'text-slate-400 hover:text-white hover:bg-white/10'"
    :title="title"
    @mousedown.prevent="emit('act')"
  >
    <slot />
  </button>
</template>

<script setup lang="ts">
defineProps<{ title?: string; active?: boolean }>()
const emit = defineEmits<{ act: [] }>()
</script>