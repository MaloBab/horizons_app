<template>
  <div class="flex items-center gap-1 px-4 pt-3 border-b border-slate-700/50 bg-slate-800 shrink-0">
    <button
      class="relative flex items-center gap-1.5 px-4 py-2 text-xs font-medium transition-colors rounded-t-lg"
      :class="modelValue === 'grouped'
        ? 'text-blue-400 bg-slate-700/50'
        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/30'"
      @click="$emit('update:modelValue', 'grouped')"
    >
      <LayoutGrid class="w-3.5 h-3.5" />
      Par groupe
      <span v-if="modelValue === 'grouped'" class="absolute bottom-0 inset-x-0 h-0.5 rounded-full bg-blue-500" />
    </button>

    <button
      class="relative flex items-center gap-1.5 px-4 py-2 text-xs font-medium transition-colors rounded-t-lg"
      :class="modelValue === 'orphans'
        ? 'text-amber-400 bg-slate-700/50'
        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/30'"
      @click="$emit('update:modelValue', 'orphans')"
    >
      <Unlink class="w-3.5 h-3.5" />
      Pôles non reliés
      <span
        v-if="orphanCount > 0"
        class="px-1.5 py-0.5 rounded-full text-[10px] font-bold border"
        :class="modelValue === 'orphans'
          ? 'bg-amber-500/20 text-amber-300 border-amber-500/30'
          : 'bg-slate-700 text-slate-500 border-slate-600'"
      >{{ orphanCount }}</span>
      <span v-if="modelValue === 'orphans'" class="absolute bottom-0 inset-x-0 h-0.5 rounded-full bg-amber-400" />
    </button>
  </div>
</template>

<script setup lang="ts">
import { LayoutGrid, Unlink } from 'lucide-vue-next'

defineProps<{ modelValue: 'grouped' | 'orphans'; orphanCount: number }>()
defineEmits<{ 'update:modelValue': [v: 'grouped' | 'orphans'] }>()
</script>