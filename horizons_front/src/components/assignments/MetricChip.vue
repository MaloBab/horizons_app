<template>
  <div class="flex items-center gap-2">
    <div class="flex flex-col">
      <span class="text-xs text-slate-500 leading-none mb-0.5">{{ label }}</span>
      <span
        class="text-sm font-bold font-mono leading-none"
        :class="{
          'text-cyan-400':  color === 'cyan',
          'text-green-400': color === 'green',
          'text-amber-400': color === 'amber',
          'text-red-400':   color === 'red',
          'text-slate-300': !color || color === 'neutral',
        }"
      >{{ value }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  value: string
  label: string
  color?: 'cyan' | 'green' | 'amber' | 'red' | 'neutral'
}>()
</script>