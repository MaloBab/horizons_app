<template>
  <aside class="flex flex-col h-full bg-slate-900/60 border-r border-white/8 w-72 shrink-0">

    <!-- ── En-tête ──────────────────────────────────────────────────────── -->
    <div class="px-3 pt-3 pb-2 border-b border-white/8 shrink-0 space-y-1.5">

      <!-- Titre -->
      <h2 class="text-xs font-semibold text-slate-400 uppercase tracking-wider px-0.5">
        Bénévoles
        <span class="text-slate-600 font-mono ml-1">({{ volunteers.length }})</span>
      </h2>

      <!-- Recherche -->
      <div class="relative">
        <Search class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3 h-3 text-slate-500 pointer-events-none" />
        <input id="search-volunteer-for-assignment"
          v-model="filters.search"
          type="text"
          placeholder="Rechercher…"
          class="w-full bg-slate-800/60 border border-white/10 rounded-md pl-7 pr-2.5 py-1.5 text-xs text-white placeholder-slate-500 outline-none focus:border-cyan-500/50 transition-colors"
        />
      </div>

      <!-- Statut + Type -->
      <div class="flex gap-1.5">
        <AppSelect
          class="flex-1"
          v-model="filters.status"
          :default="''"
          :options="[
            { label: 'Tous statuts', value: '' },
            { label: 'Non affectés', value: 'unassigned' },
            { label: 'Affectés',     value: 'assigned' },
          ]"
        />
        <AppSelect
          class="flex-1"
          v-model="filters.type"
          :default="''"
          :options="[
            { label: 'Tous types',  value: '' },
            { label: 'Normal',      value: 'Normal' },
            { label: 'Spécialisé',  value: 'Specialise' },
          ]"
        />
      </div>

      <!-- Satisfaction + Toggles sur la même ligne -->
      <div class="flex gap-1.5">
        <AppSelect
          class="flex-1"
          v-model="filters.satisfactionMin"
          :default="0"
          :options="[
            { label: 'Satisfaction', value: 0 },
            { label: '≥ 75%',        value: 0.75 },
            { label: '≥ 50%',        value: 0.5 },
            { label: '≥ 25%',        value: 0.25 },
          ]"
        />

        <button
          @click="filters.overLimitOnly = !filters.overLimitOnly"
          class="flex items-center justify-center gap-1 px-2 py-1.5 rounded-md text-xs border transition-all shrink-0"
          :class="filters.overLimitOnly
            ? 'bg-red-500/20 text-red-300 border-red-500/30'
            : 'bg-slate-800/60 text-slate-400 border-white/10 hover:border-white/20 hover:text-slate-300'"
          title="Bénévoles dépassant la limite horaire"
        >
          <TriangleAlert class="w-3 h-3 shrink-0" />
          <span>Limite</span>
        </button>

        <button
          @click="filters.withMatesOnly = !filters.withMatesOnly"
          class="flex items-center justify-center gap-1 px-2 py-1.5 rounded-md text-xs border transition-all shrink-0"
          :class="filters.withMatesOnly
            ? 'bg-pink-500/20 text-pink-300 border-pink-500/30'
            : 'bg-slate-800/60 text-slate-400 border-white/10 hover:border-white/20 hover:text-slate-300'"
          title="Bénévoles avec affinités"
        >
          <Heart class="w-3 h-3 shrink-0" />
          <span>Aff</span>
        </button>
      </div>

      <!-- Tri -->
      <div class="flex gap-1.5">
        <AppSelect
          class="flex-1"
          v-model="sortKey"
          :default="'firstName'"
          :options="[
            { label: 'Prénom',            value: 'firstName' },
            { label: 'Nom de famille',    value: 'lastName' },
            { label: 'Satisfaction',      value: 'satisfaction' },
            { label: 'Heures totales',    value: 'hours' },
            { label: 'Libres en premier', value: 'status' },
          ]"
        />
        <button
          @click="sortDir = sortDir === 'asc' ? 'desc' : 'asc'"
          class="p-1.5 bg-slate-800/60 border rounded-md transition-all shrink-0"
          :class="sortDir === 'asc'
            ? 'text-cyan-400 border-cyan-500/30'
            : 'text-violet-400 border-violet-500/30'"
          :title="sortDir === 'asc' ? 'Croissant → cliquer pour inverser' : 'Décroissant → cliquer pour inverser'"
        >
          <ArrowUp   v-if="sortDir === 'asc'" class="w-3 h-3" />
          <ArrowDown v-else                   class="w-3 h-3" />
        </button>
      </div>

    </div>

    <!-- ── Liste ─────────────────────────────────────────────────────────── -->
    <div class="flex-1 overflow-y-auto py-3 px-3 space-y-2">

      <template v-if="filtered.length > 0">
        <VolunteerCard
          v-for="v in filtered"
          :key="v.id"
          :volunteer="v"
          :metrics="metricsMap.get(v.id)"
          @click="$emit('open-detail', $event)"
          @dblclick="$emit('filter-volunteer', $event)"
          @dragstart="$emit('dragstart', $event)"
          @dragend="$emit('dragend')"
        />
      </template>

      <div
        v-else
        class="flex flex-col items-center justify-center py-12 text-slate-600"
      >
        <Users class="w-8 h-8 mb-2 opacity-40" />
        <p class="text-sm">Aucun bénévole trouvé</p>
      </div>

    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { Search, Heart, ArrowUp, ArrowDown, Users, TriangleAlert } from 'lucide-vue-next'
import { storeToRefs } from 'pinia'
import { useAssignmentStore } from '../../stores/useAssignmentStore'
import { useBenevoles } from '../../composables/useBenevoles'
import type { Volunteer } from '../../types/benevole.types'
import VolunteerCard from './VolunteerCard.vue'
import AppSelect from '../shared/AppSelect.vue'

defineEmits<{
  'open-detail': [volunteer: Volunteer]
  'filter-volunteer':[volunteer: Volunteer]
  'dragstart':   [volunteerId: string]
  'dragend':     []
}>()

const store = useAssignmentStore()
const { metricsMap, assignmentsByVolunteer } = storeToRefs(store)
const { volunteers } = useBenevoles()

const filters = reactive({
  search:          '',
  status:          '' as '' | 'assigned' | 'unassigned',
  type:            '' as '' | 'Normal' | 'Specialise',
  satisfactionMin: 0,
  overLimitOnly:   false,
  withMatesOnly:   false,
})

const sortKey = ref<'firstName' | 'lastName' | 'satisfaction' | 'hours' | 'status'>('firstName')
const sortDir = ref<'asc' | 'desc'>('asc')


const filtered = computed<Volunteer[]>(() => {
  let list = [...volunteers.value]

  if (filters.search) {
    const q = filters.search.toLowerCase()
    list = list.filter(v =>
      `${v.first_name} ${v.last_name}`.toLowerCase().includes(q) ||
      v.email.toLowerCase().includes(q)
    )
  }

  if (filters.status === 'assigned') {
    list = list.filter(v => (assignmentsByVolunteer.value.get(v.id)?.length ?? 0) > 0)
  } else if (filters.status === 'unassigned') {
    list = list.filter(v => (assignmentsByVolunteer.value.get(v.id)?.length ?? 0) === 0)
  }

  if (filters.type) {
    list = list.filter(v => v.volunteer_type === filters.type)
  }

  if (filters.satisfactionMin > 0) {
    list = list.filter(v =>
      (metricsMap.value.get(v.id)?.satisfaction_score ?? 0) >= filters.satisfactionMin
    )
  }

  if (filters.overLimitOnly) {
    list = list.filter(v => metricsMap.value.get(v.id)?.daily_limit_exceeded === true)
  }

  if (filters.withMatesOnly) {
    list = list.filter(v => v.mates.length > 0)
  }

  list.sort((a, b) => {
    let cmp = 0
    const ma = metricsMap.value.get(a.id)
    const mb = metricsMap.value.get(b.id)

    switch (sortKey.value) {
      case 'firstName':
        cmp = a.first_name.localeCompare(b.first_name)
        break
      case 'lastName':
        cmp = a.last_name.localeCompare(b.last_name)
        break
      case 'satisfaction':
        cmp = (ma?.satisfaction_score ?? 0) - (mb?.satisfaction_score ?? 0)
        break
      case 'hours':
        cmp = (ma?.total_hours ?? 0) - (mb?.total_hours ?? 0)
        break
      case 'status': {
        const aA = (assignmentsByVolunteer.value.get(a.id)?.length ?? 0) > 0 ? 1 : 0
        const bA = (assignmentsByVolunteer.value.get(b.id)?.length ?? 0) > 0 ? 1 : 0
        cmp = aA - bA
        break
      }
    }
    return sortDir.value === 'asc' ? cmp : -cmp
  })

  return list
})
</script>