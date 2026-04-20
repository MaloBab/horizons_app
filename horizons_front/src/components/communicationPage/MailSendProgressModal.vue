<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-all duration-200 ease-out"
      leave-active-class="transition-all duration-150 ease-in"
      enter-from-class="opacity-0"
      leave-to-class="opacity-0"
    >
      <div
        v-if="show"
        class="fixed inset-0 z-50 flex items-center justify-center p-6 bg-black/70 backdrop-blur-sm"
      >
        <Transition
          enter-active-class="transition-all duration-200 ease-out"
          enter-from-class="opacity-0 scale-95 translate-y-2"
        >
          <div
            v-if="show"
            class="bg-slate-900 border border-white/10 rounded-2xl shadow-2xl flex flex-col"
            style="width: min(520px, 100%)"
          >
            <!-- Header -->
            <div class="flex items-center gap-3 px-6 py-5 border-b border-white/8">
              <div
                class="w-9 h-9 rounded-xl flex items-center justify-center shrink-0"
                :class="isDone ? (hasErrors ? 'bg-amber-500/15' : 'bg-emerald-500/15') : 'bg-cyan-500/15'"
              >
                <CheckCircle2 v-if="isDone && !hasErrors" class="w-5 h-5 text-emerald-400" />
                <AlertTriangle v-else-if="isDone && hasErrors" class="w-5 h-5 text-amber-400" />
                <Loader2 v-else class="w-5 h-5 text-cyan-400 animate-spin" />
              </div>
              <div>
                <h2 class="text-sm font-semibold text-white">
                  {{ isDone ? 'Envoi terminé' : 'Envoi en cours…' }}
                </h2>
                <p class="text-xs text-slate-500 mt-0.5">
                  {{ done }} / {{ total }} mail{{ total > 1 ? 's' : '' }} traité{{ total > 1 ? 's' : '' }}
                </p>
              </div>
            </div>

            <!-- Barre de progression -->
            <div class="px-6 py-4 border-b border-white/5">
              <div class="flex items-center justify-between text-xs text-slate-500 mb-2">
                <span>Progression</span>
                <span class="font-mono">{{ Math.round(progress * 100) }}%</span>
              </div>
              <div class="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                <div
                  class="h-full rounded-full transition-all duration-300"
                  :class="isDone ? (hasErrors ? 'bg-amber-500' : 'bg-emerald-500') : 'bg-cyan-500'"
                  :style="{ width: `${Math.round(progress * 100)}%` }"
                />
              </div>

              <!-- Compteurs succès / erreur -->
              <div v-if="results.length > 0" class="flex items-center gap-4 mt-3">
                <span class="flex items-center gap-1.5 text-xs text-emerald-400">
                  <CheckCircle2 class="w-3.5 h-3.5" />
                  {{ successCount }} envoyé{{ successCount > 1 ? 's' : '' }}
                </span>
                <span v-if="errorCount > 0" class="flex items-center gap-1.5 text-xs text-red-400">
                  <XCircle class="w-3.5 h-3.5" />
                  {{ errorCount }} échec{{ errorCount > 1 ? 's' : '' }}
                </span>
              </div>
            </div>

            <!-- Liste des résultats (scroll) -->
            <div v-if="results.length > 0" class="max-h-52 overflow-y-auto px-4 py-3 space-y-1">
              <div
                v-for="r in results"
                :key="r.volunteer_id"
                class="flex items-center gap-3 px-3 py-2 rounded-lg text-xs"
                :class="r.success ? 'bg-emerald-500/5' : 'bg-red-500/8'"
              >
                <component
                  :is="r.success ? CheckCircle2 : XCircle"
                  class="w-3.5 h-3.5 shrink-0"
                  :class="r.success ? 'text-emerald-400' : 'text-red-400'"
                />
                <span class="flex-1 text-slate-300 truncate">{{ r.email }}</span>
                <span v-if="!r.success && r.error" class="text-red-400/70 truncate max-w-30" :title="r.error">
                  {{ r.error }}
                </span>
              </div>
            </div>

            <!-- Footer -->
            <div class="px-6 py-4 border-t border-white/8 flex items-center justify-end gap-3">
              <button
                v-if="isDone"
                class="px-4 py-2 text-sm bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
                @click="$emit('close')"
              >
                Fermer
              </button>
              <button
                v-if="isDone && errorCount > 0"
                class="px-4 py-2 text-sm bg-amber-600 hover:bg-amber-500 text-white rounded-lg transition-colors flex items-center gap-2"
                @click="$emit('retry-errors')"
              >
                <RefreshCw class="w-3.5 h-3.5" />
                Réessayer ({{ errorCount }})
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { CheckCircle2, XCircle, AlertTriangle, Loader2, RefreshCw } from 'lucide-vue-next'
import type { SendResult } from '../../composables/useMailTemplate'

const props = defineProps<{
  show:    boolean
  done:    number
  total:   number
  results: SendResult[]
}>()

defineEmits<{
  close:         []
  'retry-errors': []
}>()

const progress     = computed(() => props.total > 0 ? props.done / props.total : 0)
const isDone       = computed(() => props.done >= props.total && props.total > 0)
const successCount = computed(() => props.results.filter(r => r.success).length)
const errorCount   = computed(() => props.results.filter(r => !r.success).length)
const hasErrors    = computed(() => errorCount.value > 0)
</script>