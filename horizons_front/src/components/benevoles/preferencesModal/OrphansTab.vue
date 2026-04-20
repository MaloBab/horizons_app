<template>
  <div class="flex flex-col gap-3">

    <div class="flex items-start gap-2.5 px-3 py-2.5 bg-amber-500/10 border border-amber-500/20 rounded-xl">
      <AlertTriangle class="w-3.5 h-3.5 text-amber-400 shrink-0 mt-px" />
      <p class="text-xs text-amber-300/80 leading-relaxed">
        Ces pôles existent en base mais ne sont rattachés à aucun groupe de préférence.
        Rattache-les à un groupe existant ou supprime-les.
      </p>
    </div>

    <div class="flex flex-col gap-0.5">

      <div v-if="orphanCategories.length === 0" class="flex flex-col items-center gap-2 py-10 text-slate-600">
        <CheckCircle class="w-6 h-6 opacity-40" />
        <p class="text-xs">Tous les pôles sont rattachés</p>
      </div>

      <div
        v-for="cat in orphanCategories"
        :key="cat.id"
        class="group flex items-center gap-3 px-3 h-9 bg-white/3 border border-amber-500/15 rounded-lg hover:border-amber-500/30 transition-colors"
      >
        <div class="flex-1 min-w-0 flex items-center gap-2">
          <span class="text-xs font-medium text-slate-200 truncate">{{ cat.label }}</span>
          <span v-if="cat.pole_id != null" class="shrink-0 text-[10px] font-mono text-cyan-400/50">p{{ cat.pole_id }}</span>
        </div>

        <select
          class="text-[11px] bg-slate-700 border border-white/10 rounded-lg px-2 py-1 text-slate-300 outline-none focus:border-cyan-500/40 cursor-pointer hover:border-white/20 transition-colors max-w-36"
          @change="handleAttach(cat, ($event.target as HTMLSelectElement).value)"
        >
          <option value="">Rattacher à…</option>
          <option v-for="pref in preferences" :key="pref.id" :value="pref.id">{{ pref.label }}</option>
        </select>

        <button
          class="w-5 h-5 shrink-0 flex items-center justify-center rounded text-slate-600 hover:text-red-400 hover:bg-red-500/10 opacity-0 group-hover:opacity-100 transition-all"
          @click="$emit('delete-category', cat)"
        >
          <Trash2 class="w-3 h-3" />
        </button>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { AlertTriangle, CheckCircle, Trash2 } from 'lucide-vue-next'
import type { Preference, Category } from '../../../types/planning.types'

defineProps<{ orphanCategories: Category[]; preferences: Preference[] }>()
const emit = defineEmits<{
  'attach-category': [cat: Category, preferenceId: number]
  'delete-category': [cat: Category]
}>()

const handleAttach = (cat: Category, preferenceIdStr: string) => {
  if (!preferenceIdStr) return
  emit('attach-category', cat, parseInt(preferenceIdStr))
}
</script>