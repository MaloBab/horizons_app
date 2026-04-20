<template>
  <div class="flex items-center justify-between px-4 h-10 border-b-2 border-slate-600/80 bg-slate-800 shrink-0">
    <div class="flex items-center gap-5">
      <span class="text-xl font-semibold text-cyan-600 uppercase tracking-wider"> Préférences & Pôles </span>
      <div class="flex items-center gap-1.5 ml-2">
        <span class="px-2 py-0.5 rounded-full text-[10px] font-medium bg-slate-700 border border-white/10 text-slate-400">
          {{ preferences.length }} groupe{{ preferences.length > 1 ? 's' : '' }}
        </span>
        <span
          v-if="orphanCount > 0"
          class="px-2 py-0.5 rounded-full text-[10px] font-medium bg-amber-500/20 border border-amber-500/30 text-amber-300"
        >
          {{ orphanCount }} non relié{{ orphanCount > 1 ? 's' : '' }}
        </span>
      </div>
    </div>

    <button
      class="flex items-center justify-center w-6 h-6 rounded-lg text-slate-500 hover:text-white hover:bg-white/10 transition-colors"
      aria-label="Fermer"
      @click="$emit('close')"
    >
      <X class="w-3.5 h-3.5" />
    </button>

  </div>
</template>

<script setup lang="ts">
import { X } from 'lucide-vue-next'
import type { Preference } from '../../../types/planning.types'

defineProps<{ preferences: Preference[]; orphanCount: number }>()
defineEmits<{ close: [] }>()
</script>