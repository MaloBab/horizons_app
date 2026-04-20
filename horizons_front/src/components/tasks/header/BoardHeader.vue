<template>
  <header class="relative z-20 flex items-center justify-between px-6 h-14 border-b border-white/5 bg-linear-to-r from-slate-900/95 via-slate-800/80 to-slate-900/95 backdrop-blur-md shadow-[0_4px_20px_-4px_rgba(0,0,0,0.3)] overflow-hidden">
    <div class="absolute top-0 left-0 w-full h-px bg-linear-to-r from-transparent via-cyan-500/20 to-transparent pointer-events-none"></div>
    <div class="absolute -left-10 -top-10 w-32 h-32 bg-cyan-500/5 rounded-full blur-2xl pointer-events-none"></div>

    <div class="flex items-center gap-4 select-none pointer-events-none z-10">
      
      <div class="relative flex items-center justify-center w-10 h-10 rounded-xl bg-slate-900 border border-white/10 shadow-inner overflow-hidden">
        <div class="absolute inset-0 bg-cyan-500/10 blur-md"></div>
        
        <svg class="absolute bottom-0 left-0 w-[200%] h-full wave-1" viewBox="0 0 200 40" preserveAspectRatio="none">
          <path class="fill-cyan-600/30" d="M0,15 Q25,0 50,15 T100,15 T150,15 T200,15 V40 H0 Z"></path>
        </svg>

        <svg class="absolute bottom-0 left-0 w-[200%] h-full wave-2" viewBox="0 0 200 40" preserveAspectRatio="none">
          <path class="fill-blue-500/40" d="M0,22 Q25,10 50,22 T100,22 T150,22 T200,22 V40 H0 Z"></path>
        </svg>

        <svg class="absolute bottom-0 left-0 w-[200%] h-full wave-3" viewBox="0 0 200 40" preserveAspectRatio="none">
          <path class="fill-cyan-400/80" d="M0,28 Q25,20 50,28 T100,28 T150,28 T200,28 V40 H0 Z"></path>
        </svg>
      </div>

      <div class="flex flex-col justify-center">
        <h2 class="text-[16px] font-bold tracking-wide text-transparent bg-clip-text bg-white">
          Suivi d'activités
        </h2>
        <div class="flex items-center gap-2 mt-0.5">
          <div class="h-[1.2px] w-4 bg-linear-to-r from-cyan-500/60 to-transparent"></div>
          <span class="text-[7px] text-slate-500 uppercase tracking-[0.2em] font-semibold">Espace partagé</span>
          <div class="h-[1.2px] w-4 bg-linear-to-r from-transparent to-cyan-500/60"></div>
        </div>
      </div>
      
    </div>

    <div class="flex items-center gap-3 relative z-10">

      <Transition name="fade">
        <span v-if="error" class="text-xs text-red-400 bg-red-500/10 border border-red-500/30 px-3 py-1.5 rounded-lg shadow-[0_0_10px_rgba(239,68,68,0.15)]">
          {{ error }}
        </span>
      </Transition>

      <div class="flex items-center rounded-xl border border-white/10 bg-slate-800/30 shadow-inner overflow-hidden">
        <button
          @click="$emit('add-tag')"
          class="flex items-center gap-1.5 px-3 py-2 text-sm text-slate-400 hover:text-cyan-300 hover:bg-cyan-500/15 transition-all duration-300 border-r border-white/10"
          title="Créer un tag"
        ><TagIcon class="w-3.5 h-3.5" /><Plus class="w-3 h-3" /></button>
        <button
          @click="$emit('delete-tag')"
          class="flex items-center gap-1.5 px-3 py-2 text-sm text-slate-400 hover:text-red-300 hover:bg-red-500/15 transition-all duration-300"
          title="Supprimer un tag"
        ><TagIcon class="w-3.5 h-3.5" /><Minus class="w-3 h-3" /></button>
      </div>

      <Transition name="fade">
        <button
          v-if="selectedClosedCount > 0"
          @click="$emit('delete-tasks')"
          class="flex items-center gap-1.5 px-3 py-2 rounded-xl text-sm font-medium border border-red-500/40 bg-red-500/10 text-red-300 hover:bg-red-500/20 hover:shadow-[0_0_15px_rgba(239,68,68,0.2)] hover:-translate-y-0.5 transition-all duration-300"
        >
          <Trash2 class="w-3.5 h-3.5" />
          Supprimer ({{ selectedClosedCount }})
        </button>
      </Transition>

      <button
        @click="$emit('create-task')"
        class="flex items-center gap-2 px-4 py-2 rounded-xl bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 text-sm font-medium hover:bg-cyan-500/25 hover:shadow-[0_0_20px_rgba(6,182,212,0.25)] hover:-translate-y-0.5 transition-all duration-300"
      ><Plus class="w-4 h-4" /> Nouvelle tâche</button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { Plus, Minus, Tag as TagIcon, Trash2 } from 'lucide-vue-next'

defineProps<{
  error?: string | null
  selectedClosedCount: number
}>()

defineEmits(['add-tag', 'delete-tag', 'delete-tasks', 'create-task'])
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from,  .fade-leave-to      { opacity: 0; }

@keyframes wave-slide {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}
.wave-1 { animation: wave-slide 5s linear infinite; }
.wave-2 { animation: wave-slide 4s linear infinite; }
.wave-3 { animation: wave-slide 3s linear infinite; }
</style>