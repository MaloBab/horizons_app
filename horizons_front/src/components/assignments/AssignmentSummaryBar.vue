<template>
  <div class="shrink-0 z-40 bg-slate-900/95 backdrop-blur-md border-b border-white/8">
    <div class="px-6 py-3 flex items-center gap-6 flex-wrap">

      <!-- Métriques -->
      <div class="flex items-center gap-5 flex-1 flex-wrap">
        <MetricChip :value="`${metrics.jobs_filled}/${metrics.jobs_total}`" label="Postes pourvus" :color="fillRatio(metrics.jobs_filled, metrics.jobs_total)" />
        <div class="w-px h-6 bg-white/10 hidden sm:block" />
        <MetricChip :value="`${metrics.volunteers_assigned}/${metrics.volunteers_total}`" label="Bénévoles affectés" :color="fillRatio(metrics.volunteers_assigned, metrics.volunteers_total)" />
        <div class="w-px h-6 bg-white/10 hidden sm:block" />
        <MetricChip :value="`${Math.round(metrics.avg_satisfaction * 100)}%`" label="Satisfaction moy." :color="satisfactionColor(metrics.avg_satisfaction)" />
        <div class="w-px h-6 bg-white/10 hidden sm:block" />
        <MetricChip :value="`${metrics.avg_hours_per_day.toFixed(1)}h`" label="Heures moy./jour" color="cyan" />
      </div>

      <!-- Actions -->
      <div class="flex items-center gap-2 shrink-0">

        <!-- Undo / Redo -->
        <div class="flex items-center gap-1 bg-slate-800/60 border border-white/8 rounded-lg p-1">
          <button :disabled="!canUndo || isLoading" @click="store.undo()"
            class="p-1.5 rounded-md transition-all"
            :class="canUndo && !isLoading ? 'text-slate-300 hover:bg-white/10 hover:text-white' : 'text-slate-600 cursor-not-allowed'"
            title="Annuler (Ctrl+Z)">
            <Undo2 class="w-4 h-4" />
          </button>
          <span class="text-[10px] text-slate-500 font-mono px-1 min-w-12 text-center">
            {{ historyPosition.current }}/{{ historyPosition.total }}
          </span>
          <button :disabled="!canRedo || isLoading" @click="store.redo()"
            class="p-1.5 rounded-md transition-all"
            :class="canRedo && !isLoading ? 'text-slate-300 hover:bg-white/10 hover:text-white' : 'text-slate-600 cursor-not-allowed'"
            title="Rétablir (Ctrl+Y)">
            <Redo2 class="w-4 h-4" />
          </button>
        </div>

        <!-- Lancer l'algorithme -->
        <button @click="handleRunAlgorithm" :disabled="isLoading"
          class="flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-all border"
          :class="isLoading ? 'bg-purple-500/10 text-purple-400/50 border-purple-500/20 cursor-wait' : 'bg-purple-500/15 text-purple-300 border-purple-500/30 hover:bg-purple-500/25'">
          <Loader2 v-if="isLoading" class="w-4 h-4 animate-spin" />
          <Zap v-else class="w-4 h-4" />
          <span>{{ isLoading ? 'Calcul…' : "Affectation automatique" }}</span>
        </button>


        <!-- Tout supprimer (assignments) -->
        <button @click="handleClearAll" :disabled="isLoading"
          class="flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-all border border-red-500/30 bg-red-500/5 text-red-300/65 hover:border-red-500/55 hover:bg-red-500/15 hover:text-red-300 disabled:opacity-20 disabled:cursor-not-allowed">
          <Trash2 class="w-4 h-4" />
          <span>Tout supprimer</span>
        </button>

        <!-- Sauvegarder -->
        <button @click="handleSave" :disabled="saveState === 'saving' || saveState === 'saved'"
          class="flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-all border"
          :class="saveButtonClass">
          <Loader2 v-if="saveState === 'saving'" class="w-4 h-4 animate-spin" />
          <Check v-else-if="saveState === 'saved'" class="w-4 h-4" />
          <AlertCircle v-else-if="saveState === 'error'" class="w-4 h-4" />
          <Save v-else class="w-4 h-4" />
          <span>{{ saveLabel }}</span>
          <span v-if="saveState === 'unsaved'" class="w-1.5 h-1.5 rounded-full bg-red-400 animate-pulse" />
        </button>

      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import { Undo2, Redo2, Zap, Save, Check, AlertCircle, Loader2, Trash2 } from 'lucide-vue-next'
import { storeToRefs } from 'pinia'
import { useAssignmentStore } from '../../stores/useAssignmentStore'
import { useActivityLogger } from '../../composables/Activity/useActivityLogger'
import MetricChip from './MetricChip.vue'

const emit = defineEmits(['confirm-delete-all', 'run-algorithm'])
const { scheduleModified } = useActivityLogger()
const store = useAssignmentStore()
const { globalMetrics: metrics, canUndo, canRedo, historyPosition, isLoading, saveState } = storeToRefs(store)

function fillRatio(filled: number, total: number): 'green' | 'amber' | 'red' | 'neutral' {
  if (total === 0) return 'neutral'
  const r = filled / total
  if (r >= 1)   return 'green'
  if (r >= 0.5) return 'amber'
  return 'red'
}

function satisfactionColor(score: number): 'green' | 'amber' | 'red' {
  if (score >= 0.75) return 'green'
  if (score >= 0.4)  return 'amber'
  return 'red'
}

const saveButtonClass = computed(() => {
  switch (saveState.value) {
    case 'saved':  return 'bg-green-500/10 text-green-400 border-green-500/20 cursor-default'
    case 'saving': return 'bg-slate-700/50 text-slate-400 border-white/10 cursor-wait'
    case 'error':  return 'bg-red-500/15 text-red-300 border-red-500/30 hover:bg-red-500/25'
    default:       return 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30 hover:bg-cyan-500/25'
  }
})

const saveLabel = computed(() => {
  switch (saveState.value) {
    case 'saved':  return 'Sauvegardé'
    case 'saving': return 'Sauvegarde…'
    case 'error':  return 'Réessayer'
    default:       return 'Sauvegarder'
  }
})

async function handleClearAll() {
  if (isLoading.value) return
    emit('confirm-delete-all')
  }


async function handleSave() {
  if (saveState.value === 'saving' || saveState.value === 'saved') return
  scheduleModified(historyPosition.value.current)
  await store.save()
}

async function handleRunAlgorithm() {
  if (isLoading.value) return
  emit('run-algorithm')
}

function onKeydown(e: KeyboardEvent) {
  if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return
  if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey) { e.preventDefault(); store.undo() }
  if ((e.ctrlKey || e.metaKey) && (e.key === 'y' || (e.key === 'z' && e.shiftKey))) { e.preventDefault(); store.redo() }
}

onMounted(()   => document.addEventListener('keydown', onKeydown))
onUnmounted(() => document.removeEventListener('keydown', onKeydown))
</script>