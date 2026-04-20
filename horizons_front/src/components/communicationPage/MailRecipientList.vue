<template>
  <div class="flex flex-col h-full">
    <!-- En-tête -->
    <div class="shrink-0 mb-4">

      <!-- Titre + compteurs sur deux lignes propres -->
      <div class="mb-3">
        <span class="text-[10px] font-semibold uppercase tracking-[0.15em] text-slate-500 block mb-1.5">
          Destinataires
        </span>
        <div class="flex items-center gap-2">
          <span
            v-if="selectedIds.size > 0"
            class="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-cyan-500/15 text-cyan-400 border border-cyan-500/20"
          >
            {{ selectedIds.size }} sélectionné{{ selectedIds.size > 1 ? 's' : '' }}
          </span>
          <span class="text-[10px] text-slate-600">
            {{ assignedCount }}/{{ volunteers.length }} affectés
          </span>
        </div>
      </div>

      <!-- Barre de recherche -->
      <div class="relative mb-3">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-600 pointer-events-none" />
        <input
          v-model="search"
          type="text"
          placeholder="Rechercher un bénévole…"
          class="w-full pl-9 pr-3 py-2 text-xs bg-slate-900/60 border border-white/6 rounded-lg text-slate-200 placeholder-slate-600 outline-none focus:border-cyan-500/30 transition-all"
        />
      </div>

      <!-- Contrôles sur deux lignes -->
      <div class="flex flex-col gap-2">

        <!-- Toggle affectés -->
        <button
          @click="onlyAssigned = !onlyAssigned"
          class="flex items-center gap-2 px-3 py-2 rounded-lg text-xs transition-all border w-full"
          :class="onlyAssigned
            ? 'bg-emerald-500/10 border-emerald-500/25 text-emerald-400'
            : 'bg-slate-800/60 border-white/6 text-slate-500 hover:text-slate-300 hover:border-white/10'"
        >
          <div
            class="w-1.5 h-1.5 rounded-full transition-colors shrink-0"
            :class="onlyAssigned ? 'bg-emerald-400' : 'bg-slate-600'"
          />
          Affectés seulement
        </button>

        <!-- Tout / Aucun -->
        <div class="grid grid-cols-2 gap-2">
          <button
            @click="selectAll"
            class="py-2 rounded-lg text-xs bg-slate-800/60 border border-white/6 text-slate-400 hover:text-white hover:bg-slate-700/60 hover:border-white/15 transition-all"
          >
            Tout sélectionner
          </button>
          <button
            @click="deselectAll"
            :disabled="selectedIds.size === 0"
            class="py-2 rounded-lg text-xs border transition-all"
            :class="selectedIds.size > 0
              ? 'bg-slate-800/60 border-white/6 text-slate-400 hover:text-white hover:bg-slate-700/60 hover:border-white/15'
              : 'bg-transparent border-transparent text-slate-700 cursor-not-allowed'"
          >
            Désélectionner
          </button>
        </div>

      </div>
    </div>

    <!-- Séparateur -->
    <div class="shrink-0 h-px bg-white/5 mb-3" />

    <!-- Liste -->
    <div class="flex-1 overflow-y-auto -mx-1 px-1 space-y-1 min-h-0">
      <TransitionGroup name="list">
        <div
          v-for="v in filtered"
          :key="v.id"
          @click="toggleSelect(v.id)"
          class="group flex items-center gap-3 px-3 py-2.5 rounded-xl border cursor-pointer select-none transition-all duration-150"
          :class="selectedIds.has(v.id)
            ? 'bg-cyan-500/8 border-cyan-500/20 hover:bg-cyan-500/12'
            : 'bg-slate-800/30 border-white/4 hover:bg-slate-800/60 hover:border-white/8'"
        >
          <!-- Checkbox -->
          <div
            class="shrink-0 w-4 h-4 rounded-sm border flex items-center justify-center transition-all duration-150"
            :class="selectedIds.has(v.id)
              ? 'bg-cyan-500 border-cyan-400 shadow-[0_0_8px_rgba(6,182,212,0.3)]'
              : 'border-white/15 bg-slate-900/40 group-hover:border-white/25'"
          >
            <svg
              v-if="selectedIds.has(v.id)"
              class="w-2.5 h-2.5 text-white"
              viewBox="0 0 10 10"
              fill="none"
            >
              <path d="M1.5 5l2.5 2.5 4.5-4.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>

          <!-- Avatar -->
          <div
            class="shrink-0 w-7 h-7 rounded-full flex items-center justify-center text-[12px] font-bold transition-colors"
            :class="selectedIds.has(v.id)
              ? 'bg-cyan-500/20 text-cyan-300'
              : 'bg-slate-700/80 text-slate-400 group-hover:bg-slate-700'"
          >
            {{ v.first_name[0] }}{{ v.last_name[0] }}
          </div>

          <!-- Infos -->
          <div class="flex-1 min-w-0">
            <p
              class="text-[12px] font-medium truncate transition-colors"
              :class="selectedIds.has(v.id) ? 'text-cyan-100' : 'text-slate-300 group-hover:text-slate-200'"
            >
              {{ v.first_name }} {{ v.last_name }}
            </p>
            <p class="text-[10px] text-slate-600 truncate">{{ v.email }}</p>
          </div>
        </div>
      </TransitionGroup>

      <p v-if="filtered.length === 0" class="text-center text-xs text-slate-600 py-8">
        Aucun bénévole trouvé
      </p>
    </div>

    <!-- Footer -->
    <div class="shrink-0 mt-3 pt-3 border-t border-white/5 flex justify-between items-center">
      <span class="text-[10px] text-slate-600">{{ filtered.length }} visible(s)</span>
      <span class="text-[10px] text-slate-600">{{ volunteers.length }} au total</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Search } from 'lucide-vue-next'
import type { Volunteer } from '../../types/benevole.types'

const props = defineProps<{
  volunteers: Volunteer[]
  assignmentsByVolunteer: Map<string, { job_id: number }[]>
}>()

const emit = defineEmits<{
  'update:selectedIds': [ids: Set<string>]
}>()

const search       = ref('')
const onlyAssigned = ref(false)
const selectedIds  = ref<Set<string>>(new Set())

const jobCount = (id: string) => props.assignmentsByVolunteer.get(id)?.length ?? 0

const assignedCount = computed(() =>
  props.volunteers.filter(v => jobCount(v.id) > 0).length
)

const filtered = computed(() => {
  const q = search.value.toLowerCase()
  return props.volunteers.filter(v => {
    const matchSearch   = !q || `${v.first_name} ${v.last_name} ${v.email}`.toLowerCase().includes(q)
    const matchAssigned = !onlyAssigned.value || jobCount(v.id) > 0
    return matchSearch && matchAssigned
  })
})

function toggleSelect(id: string) {
  const next = new Set(selectedIds.value)
  next.has(id) ? next.delete(id) : next.add(id)
  selectedIds.value = next
  emit('update:selectedIds', next)
}

function selectAll() {
  const next = new Set(filtered.value.map(v => v.id))
  selectedIds.value = next
  emit('update:selectedIds', next)
}

function deselectAll() {
  selectedIds.value = new Set()
  emit('update:selectedIds', new Set())
}
</script>

<style scoped>
.list-move,
.list-enter-active,
.list-leave-active {
  transition: all 0.15s ease;
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(-6px);
}
</style>