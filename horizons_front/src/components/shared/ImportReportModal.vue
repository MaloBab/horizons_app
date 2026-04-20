<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="isOpen && report"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        @click.self="$emit('close')"
      >
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-slate-950/80 backdrop-blur-sm" @click="$emit('close')" />

        <!-- Modal -->
        <div class="relative bg-slate-800/90 backdrop-blur-xl border border-white/10 rounded-2xl w-full max-w-2xl shadow-2xl overflow-hidden">
          <!-- Glow accents -->
          <div class="absolute top-0 right-0 w-48 h-48 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
          <div class="absolute bottom-0 left-0 w-32 h-32 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />

          <div class="relative z-10">

            <!-- Header -->
            <div class="flex items-center justify-between p-6 border-b border-white/5">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-linear-to-br from-emerald-500/30 to-cyan-500/30 border border-emerald-500/20 flex items-center justify-center shrink-0">
                  <FileCheck class="w-5 h-5 text-emerald-400" />
                </div>
                <div>
                  <h2 class="text-lg font-bold text-white">Rapport d'import</h2>
                  <p class="text-sm text-slate-400">{{ report.total_parsed }} lignes analysées</p>
                </div>
              </div>
              <button
                @click="$emit('close')"
                class="p-1.5 text-slate-400 hover:text-white hover:bg-white/5 rounded-lg transition-all duration-200"
              >
                <X class="w-5 h-5" />
              </button>
            </div>

            <!-- Stats -->
            <div class="grid grid-cols-3 gap-3 p-6 border-b border-white/5">
              <div class="bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-4 text-center">
                <p class="text-3xl font-bold text-emerald-400">{{ report.total_persisted }}</p>
                <p class="text-xs text-slate-400 mt-1 uppercase tracking-wider">Persistés</p>
              </div>
              <div class="bg-amber-500/10 border border-amber-500/20 rounded-xl p-4 text-center">
                <p class="text-3xl font-bold text-amber-400">{{ report.total_warnings }}</p>
                <p class="text-xs text-slate-400 mt-1 uppercase tracking-wider">Avertissements</p>
              </div>
              <div class="bg-red-500/10 border border-red-500/20 rounded-xl p-4 text-center">
                <p class="text-3xl font-bold text-red-400">{{ report.total_errors }}</p>
                <p class="text-xs text-slate-400 mt-1 uppercase tracking-wider">Erreurs</p>
              </div>
            </div>

            <!-- Tabs -->
            <div class="flex gap-1 px-6 pt-4">
              <button
                v-for="tab in visibleTabs"
                :key="tab.key"
                @click="activeTab = tab.key"
                class="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200"
                :class="activeTab === tab.key
                  ? 'bg-slate-600/60 text-white'
                  : 'text-slate-400 hover:text-slate-300 hover:bg-white/5'"
              >
                <span>{{ tab.icon }}</span>
                {{ tab.label }}
                <span
                  class="px-1.5 py-0.5 rounded-full text-[10px] font-bold"
                  :class="tab.badgeClass"
                >{{ tab.count }}</span>
              </button>
            </div>

            <!-- Tab content -->
            <div class="px-6 pb-2 pt-3 max-h-64 overflow-y-auto custom-scrollbar">

              <!-- Persistés -->
              <template v-if="activeTab === 'persisted'">
                <div v-if="report.persisted.length === 0" class="text-center text-slate-500 text-sm py-8">
                  Aucun élément persisté
                </div>

                <!-- Mode job -->
                <template v-else-if="mode === 'job'">
                  <div
                    v-for="item in report.persisted" :key="(item as any).id"
                    class="flex items-center gap-3 py-2 border-b border-white/5 last:border-0"
                  >
                    <div class="w-2 h-2 rounded-full bg-emerald-400 shrink-0" />
                    <span class="text-sm text-white font-medium flex-1 truncate">{{ (item as any).name }}</span>
                    <span class="text-xs text-slate-400 shrink-0">{{ (item as any).category?.label }}</span>
                    <span class="text-xs text-slate-500 shrink-0">
                      {{ (item as any).slot?.start_time }}h → {{ (item as any).slot?.end_time }}h
                    </span>
                  </div>
                </template>

                <!-- Mode bénévole -->
                <template v-else-if="mode === 'volunteer'">
                  <div
                    v-for="item in report.persisted" :key="(item as any).id"
                    class="flex items-center gap-3 py-2 border-b border-white/5 last:border-0"
                  >
                    <div class="w-2 h-2 rounded-full bg-emerald-400 shrink-0" />
                    <div class="w-7 h-7 rounded-full bg-linear-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-xs shrink-0">
                      {{ (item as any).first_name?.[0] }}{{ (item as any).last_name?.[0] }}
                    </div>
                    <span class="text-sm text-white font-medium flex-1 truncate">
                      {{ (item as any).first_name }} {{ (item as any).last_name }}
                    </span>
                    <span class="text-xs text-slate-400 shrink-0 truncate max-w-40">{{ (item as any).email }}</span>
                    <span class="text-xs text-slate-500 shrink-0">
                      {{ (item as any).slots?.length ?? 0 }} créneaux
                    </span>
                  </div>
                </template>
              </template>

              <!-- Warnings -->
              <template v-if="activeTab === 'warnings'">
                <div v-if="report.warnings.length === 0" class="text-center text-slate-500 text-sm py-8">
                  Aucun avertissement
                </div>
                <div
                  v-for="(w, i) in report.warnings" :key="`w-${i}`"
                  class="flex items-start gap-3 py-2 border-b border-white/5 last:border-0"
                >
                  <span class="text-[10px] text-slate-500 shrink-0 mt-0.5 w-8">L.{{ w.ligne }}</span>
                  <span class="text-xs font-medium text-amber-300/90 shrink-0 w-40 truncate" :title="w.nom">{{ w.nom }}</span>
                  <span class="text-xs text-slate-400">{{ w.message }}</span>
                </div>
              </template>

              <!-- Erreurs -->
              <template v-if="activeTab === 'errors'">
                <div v-if="report.errors.length === 0" class="text-center text-slate-500 text-sm py-8">
                  Aucune erreur
                </div>
                <div
                  v-for="(e, i) in report.errors" :key="`e-${i}`"
                  class="flex items-start gap-3 py-2 border-b border-white/5 last:border-0"
                >
                  <span class="text-[10px] text-slate-500 shrink-0 mt-0.5 w-8">L.{{ e.ligne }}</span>
                  <span v-if="e.nom" class="text-xs font-medium text-red-300/90 shrink-0 w-40 truncate" :title="e.nom">{{ e.nom }}</span>
                  <span class="text-xs text-slate-400">{{ e.message }}</span>
                </div>
              </template>

            </div>

            <!-- Footer -->
            <div class="p-6 pt-4">
              <button
                @click="$emit('close')"
                class="w-full px-4 py-2.5 bg-slate-700/50 hover:bg-slate-600/50 text-slate-300 rounded-xl font-medium transition-all duration-200 border border-white/5 hover:border-white/10"
              >
                Fermer
              </button>
            </div>

          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { X, FileCheck } from 'lucide-vue-next'
import type { ImportReport } from '../../types/import.types'

interface Props {
  isOpen: boolean
  report: ImportReport | null
  /** 'job' (défaut) ou 'volunteer' — contrôle l'affichage de l'onglet Persistés */
  mode?:  'job' | 'volunteer'
}

const props = withDefaults(defineProps<Props>(), { mode: 'job' })
defineEmits<{ close: [] }>()

const activeTab = ref<'persisted' | 'warnings' | 'errors'>('persisted')

const tabs = computed(() => [
  {
    key:        'persisted' as const,
    label:      'Persistés',
    icon:       '✅',
    count:      props.report?.total_persisted ?? 0,
    badgeClass: 'bg-emerald-500/20 text-emerald-400',
  },
  {
    key:        'warnings' as const,
    label:      'Avertissements',
    icon:       '⚠️',
    count:      props.report?.total_warnings ?? 0,
    badgeClass: 'bg-amber-500/20 text-amber-400',
  },
  {
    key:        'errors' as const,
    label:      'Erreurs',
    icon:       '❌',
    count:      props.report?.total_errors ?? 0,
    badgeClass: 'bg-red-500/20 text-red-400',
  },
])

const visibleTabs = computed(() => tabs.value.filter(t => t.count > 0 || t.key === 'persisted'))
</script>

<style scoped>
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s ease; }
.modal-enter-active .relative, .modal-leave-active .relative { transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.2s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from .relative { transform: scale(0.95) translateY(8px); opacity: 0; }

.custom-scrollbar::-webkit-scrollbar       { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #475569; border-radius: 2px; }
</style>