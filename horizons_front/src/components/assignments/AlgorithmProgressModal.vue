<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm px-4"
        @click.self="onBackdropClick"
      >
        <div class="w-full max-w-lg bg-slate-950 border border-slate-700/60 rounded-2xl p-6">

          <!-- En-tête -->
          <div class="flex items-start justify-between gap-3 mb-5">
            <div>
              <h2 class="text-[15px] font-medium text-slate-100">{{ title }}</h2>
              <p class="text-[13px] text-slate-500 mt-0.5">{{ subtitle }}</p>
            </div>
            <div class="w-8.5 h-8.5 rounded-full flex items-center justify-center shrink-0" :class="iconWrapClass">
              <Loader2 v-if="phase === 'running'" class="w-4 h-4 text-teal-400 animate-spin" />
              <CheckCircle2 v-else-if="phase === 'success'" class="w-4 h-4 text-teal-400" />
              <XCircle v-else-if="phase === 'error'" class="w-4 h-4 text-red-400" />
              <Clock v-else class="w-4 h-4 text-slate-500" />
            </div>
          </div>

          <!-- Barre de progression -->
          <div class="mb-4">
            <div class="flex justify-between items-center mb-1.5">
              <span class="text-xs text-slate-500 truncate flex-1 min-w-0 pr-3">
                {{ progressMessage || 'En attente…' }}
              </span>
              <span class="text-[13px] font-medium text-slate-100 tabular-nums">
                {{ progress }}%
              </span>
            </div>
            <div class="h-1.25 bg-slate-800 rounded-full overflow-hidden">
              <div
                class="h-full rounded-full transition-[width] duration-300 ease-out"
                :class="phase === 'error' ? 'bg-red-500' : 'bg-teal-500'"
                :style="{ width: progress + '%' }"
              />
            </div>
          </div>

          <!-- Pills de phase -->
          <div class="flex gap-1.5 flex-wrap mb-4">
            <span
              v-for="(p, i) in PHASES"
              :key="i"
              class="inline-flex items-center gap-1.5 text-[11px] px-2.5 py-0.75 rounded-full border transition-all duration-200"
              :class="{
                'border-teal-600 bg-teal-950/60 text-teal-400':    i === currentPhaseIndex,
                'border-slate-700/50 bg-slate-800 text-slate-600': i < currentPhaseIndex || phase === 'success',
                'border-slate-700/50 text-slate-500':               i > currentPhaseIndex && phase !== 'success',
              }"
            >
              <span class="w-1.25 h-1.25 rounded-full bg-current" />
              {{ p.label }}
            </span>
          </div>

          <!-- Métriques live -->
          <div v-if="stats" class="grid grid-cols-4 gap-2 mb-4">
            <div class="bg-slate-800 rounded-lg px-2 py-2.5 text-center">
              <div class="text-[15px] font-medium text-slate-100 tabular-nums">{{ stats.generation }}</div>
              <div class="text-[10px] text-slate-500 mt-0.5">Génération</div>
            </div>
            <div class="bg-teal-950/60 border border-teal-800/40 rounded-lg px-2 py-2.5 text-center">
              <div class="text-[15px] font-medium text-teal-400 tabular-nums">{{ stats.satisfaction }}</div>
              <div class="text-[10px] text-slate-500 mt-0.5">Satisfaction</div>
            </div>
            <div class="bg-slate-800 rounded-lg px-2 py-2.5 text-center">
              <div class="text-[15px] font-medium text-slate-100 tabular-nums">{{ stats.postes }}</div>
              <div class="text-[10px] text-slate-500 mt-0.5">Affectations</div>
            </div>
            <div class="bg-slate-800 rounded-lg px-2 py-2.5 text-center">
              <div class="text-[15px] font-medium text-slate-100 tabular-nums">{{ stats.benevoles }}</div>
              <div class="text-[10px] text-slate-500 mt-0.5">Bénévoles</div>
            </div>
          </div>

          <!-- Log terminal -->
          <div ref="logRef" class="bg-[#080c14] border border-slate-800 rounded-lg px-3 py-2.5 max-h-20 overflow-y-auto flex flex-col gap-0.5 mb-4">
            <p
              v-for="(line, i) in logLines"
              :key="i"
              class="text-[11px] font-mono"
              :class="i === logLines.length - 1 ? 'text-slate-400' : 'text-slate-600'"
            >{{ line }}</p>
            <p v-if="!logLines.length" class="text-[11px] font-mono text-slate-700">En attente de démarrage…</p>
          </div>

          <!-- Alerte résultat -->
          <Transition
            enter-active-class="transition-opacity duration-300"
            enter-from-class="opacity-0"
            leave-active-class="transition-opacity duration-300"
            leave-to-class="opacity-0"
          >
            <div
              v-if="alertMsg"
              class="text-[13px] px-3 py-2.5 rounded-lg mb-4"
              :class="alertClass"
            >
              {{ alertMsg }}
            </div>
          </Transition>

          <!-- Footer -->
          <div class="flex justify-end gap-2 pt-4 border-t border-slate-700/40">
            <template v-if="phase === 'idle'">
              <button
                class="text-[13px] px-4 py-1.75 rounded-lg border border-slate-700/60 bg-transparent text-slate-300 cursor-pointer hover:bg-slate-800 transition-colors"
                @click="$emit('update:modelValue', false)"
              >Annuler</button>
              <button
                class="text-[13px] px-4 py-1.75 rounded-lg border border-teal-600 bg-teal-800/40 text-white cursor-pointer hover:bg-teal-700/50 transition-colors"
                @click="$emit('run')"
              >Lancer l'algorithme</button>
            </template>
            <template v-else-if="phase === 'success'">
              <button
                class="text-[13px] px-4 py-1.75 rounded-lg border border-teal-600 bg-teal-800/40 text-white cursor-pointer hover:bg-teal-700/50 transition-colors"
                @click="handleSuccess()"
              >Fermer</button>
            </template>
            <template v-else-if="phase === 'error'">
              <button
                class="text-[13px] px-4 py-1.75 rounded-lg border border-slate-700/60 bg-transparent text-slate-300 cursor-pointer hover:bg-slate-800 transition-colors"
                @click="$emit('update:modelValue', false)"
              >Fermer</button>
              <button
                class="text-[13px] px-4 py-1.75 rounded-lg border border-teal-600 bg-teal-800/40 text-white cursor-pointer hover:bg-teal-700/50 transition-colors"
                @click="$emit('run')"
              >Réessayer</button>
            </template>
          </div>

        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { Loader2, CheckCircle2, XCircle, Clock } from 'lucide-vue-next'
import { useActivityLogger } from '../../composables/Activity/useActivityLogger'

export type AlgorithmPhase = 'idle' | 'running' | 'success' | 'error'

export interface AlgorithmStats {
  generation:   string
  satisfaction: string
  postes:       string
  benevoles:    string
}

interface Props {
  modelValue:      boolean
  phase:           AlgorithmPhase
  progress:        number
  progressMessage: string
  logLines:        string[]
  stats?:          AlgorithmStats | null
  alertMsg?:       string
}

const props = withDefaults(defineProps<Props>(), {
  stats:    null,
  alertMsg: '',
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'run':    []
  'cancel': []
}>()

const PHASES = [
  { label: 'Initialisation' },
  { label: 'Évolution' },
  { label: 'Finalisation' },
]

const { geneticAlgorithmRun } = useActivityLogger()

const currentPhaseIndex = computed(() => {
  if (props.phase === 'idle')    return -1
  if (props.phase === 'success') return 3
  if (props.phase === 'error')   return 0
  if (props.progress < 5)  return 0
  if (props.progress < 95) return 1
  return 2
})

const title = computed(() => ({
  idle:    "Lancer l'algorithme génétique",
  running: 'Algorithme en cours…',
  success: 'Affectations générées',
  error:   "Échec de l'algorithme",
}[props.phase]))

const subtitle = computed(() => ({
  idle:    'Affecte automatiquement les bénévoles aux postes',
  running: 'Ne fermez pas cette fenêtre',
  success: 'Les affectations ont été sauvegardées',
  error:   "Une erreur s'est produite — vous pouvez réessayer",
}[props.phase]))

const iconWrapClass = computed(() => ({
  idle:    'bg-slate-800',
  running: 'bg-teal-950/60',
  success: 'bg-teal-950/60',
  error:   'bg-red-950/50',
}[props.phase]))

function onBackdropClick() {
  if (props.phase === 'running') return
}

const alertClass = computed(() => {
  if (props.phase === 'success') return 'bg-teal-950/40 border border-teal-800/50 text-teal-400'
  if (props.phase === 'error')   return 'bg-red-950/40 border border-red-800/50 text-red-400'
  return 'bg-teal-950/40 border border-teal-800/50 text-teal-400'
})

function handleSuccess() {
  emit('update:modelValue', false)
  if (props.stats) geneticAlgorithmRun(props.stats.satisfaction, props.stats.postes, props.stats.benevoles)


}

const logRef = ref<HTMLElement | null>(null)

watch(() => props.logLines.length, async () => {
  await nextTick()
  if (logRef.value) logRef.value.scrollTop = logRef.value.scrollHeight
})
</script>

<style scoped>
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s, transform 0.2s; }
.modal-enter-from, .modal-leave-to { opacity: 0; transform: scale(0.96); }
</style>