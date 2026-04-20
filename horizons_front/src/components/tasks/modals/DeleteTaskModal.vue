<template>
  <Transition name="modal">
    <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/70 backdrop-blur-sm" @click="emit('cancel')" />
      <div class="relative z-10 w-full max-w-sm bg-slate-900 border border-white/10 rounded-2xl shadow-2xl p-6">

        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-xl bg-red-500/15 border border-red-500/30 flex items-center justify-center shrink-0">
            <Trash2 class="w-5 h-5 text-red-400" />
          </div>
          <div>
            <h2 class="text-base font-semibold text-white">Supprimer les tâches</h2>
            <p class="text-xs text-slate-500 mt-0.5">
              {{ count }} tâche{{ count > 1 ? 's' : '' }} fermée{{ count > 1 ? 's' : '' }} sélectionnée{{ count > 1 ? 's' : '' }}
            </p>
          </div>
        </div>

        <p class="text-sm text-slate-400 mb-5">
          Cette action est <strong class="text-white">irréversible</strong>. Les tâches supprimées ne pourront pas être récupérées.
        </p>

        <div class="flex items-center justify-end gap-3">
          <button
            @click="emit('cancel')"
            class="px-4 py-2 rounded-xl text-sm text-slate-400 hover:text-white transition-colors"
          >Annuler</button>
          <button
            @click="emit('confirm')"
            :disabled="loading"
            class="px-5 py-2 rounded-xl text-sm font-medium bg-red-500/15 text-red-300 border border-red-500/30 hover:bg-red-500/25 transition-all disabled:opacity-30 disabled:cursor-not-allowed"
          >
            <span v-if="loading" class="flex items-center gap-1.5">
              <div class="w-3 h-3 rounded-full border-2 border-red-500/40 border-t-red-400 animate-spin" />
              Suppression…
            </span>
            <span v-else>Confirmer</span>
          </button>
        </div>

      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { Trash2 } from 'lucide-vue-next'

defineProps<{ open: boolean; count: number; loading: boolean }>()
const emit = defineEmits<{ confirm: []; cancel: [] }>()
</script>

<style scoped>
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s ease; }
.modal-enter-from,   .modal-leave-to     { opacity: 0; }
.modal-enter-active .relative,
.modal-leave-active .relative { transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1); }
.modal-enter-from   .relative,
.modal-leave-to     .relative { transform: scale(0.95) translateY(8px); }
</style>