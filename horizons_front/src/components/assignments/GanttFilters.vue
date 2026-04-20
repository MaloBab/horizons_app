<template>
  <div class="bg-slate-800/50 backdrop-blur-sm border border-white/10 rounded-xl p-4">
    <div class="flex flex-wrap gap-3 items-center">

      <!-- Recherche poste -->
      <div class="relative flex-1 min-w-40">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
        <input id="search-job"
          :value="filters.search"
          @input="emit('update:filters', { ...filters, search: ($event.target as HTMLInputElement).value })"
          type="text"
          placeholder="Rechercher un poste…"
          class="w-full bg-slate-700/50 border border-white/10 rounded-lg pl-9 pr-4 py-2 text-sm text-white placeholder-slate-500 outline-none focus:border-cyan-500/50 transition-colors"
        />
      </div>

      <div class="w-px h-6 bg-white/10 hidden sm:block" />

      <!-- État de remplissage -->
      <AppSelect
        :model-value="filters.fillStatus"
        @update:model-value="emit('update:filters', { ...filters, fillStatus: $event as GanttFilters['fillStatus'] })"
        :options="[
          { label: 'Tous états', value: '' },
          { label: 'Vides',      value: 'empty' },
          { label: 'Partiels',   value: 'partial' },
          { label: 'Complets',   value: 'full' },
        ]"
      />

      <!-- Filtre par jour -->
      <AppSelect
        :model-value="filters.dayIndex ?? ''"
        @update:model-value="emit('update:filters', { ...filters, dayIndex: $event === '' ? null : Number($event) })"
        :options="[
          { label: 'Tous les jours', value: '' },
          ...festivalDays.map(day => ({
            label: day.label,
            value: day.day,
          }))
        ]"
      />

      <div class="w-px h-6 bg-white/10 hidden sm:block" />

      <!-- Filtre bénévole (autocomplete) -->
      <VolunteerAutocomplete
        ref="volunteerAutocompleteRef"
        :model-value="filters.volunteerId"
        :volunteers="volunteers"
        @update:model-value="onVolunteerChange"
      />

      <!-- Réinitialiser -->
      <button
        v-if="hasActiveFilters"
        @click="emit('reset')"
        class="text-sm text-red-400 hover:text-red-500 transition-colors flex items-center gap-1"
      >
        <X class="w-3.5 h-3.5" /> Réinitialiser
      </button>

    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { Search, X } from 'lucide-vue-next'
import VolunteerAutocomplete from './VolunteerAutocomplete.vue'
import type { Volunteer } from '../../types/benevole.types'
import type { FestivalDay } from '../../types/planning.types'
import AppSelect from '../shared/AppSelect.vue'

// ── Types ─────────────────────────────────────────────────────────────────────

export interface GanttFilters {
  search:      string
  fillStatus:  '' | 'empty' | 'partial' | 'full'
  dayIndex:    number | null
  volunteerId: string
}

// ── Props & emits ─────────────────────────────────────────────────────────────

const props = defineProps<{
  filters:      GanttFilters
  festivalDays: FestivalDay[]
  volunteers:   Volunteer[]
}>()

const emit = defineEmits<{
  'update:filters': [filters: GanttFilters]
  'reset': []
}>()

// ── Computed ──────────────────────────────────────────────────────────────────

const hasActiveFilters = computed(() =>
  props.filters.search      !== '' ||
  props.filters.fillStatus  !== '' ||
  props.filters.dayIndex    !== null ||
  props.filters.volunteerId !== ''
)

// ── Refs ──────────────────────────────────────────────────────────────────────

const volunteerAutocompleteRef = ref<InstanceType<typeof VolunteerAutocomplete> | null>(null)

// ── Handlers ──────────────────────────────────────────────────────────────────

function onVolunteerChange(id: string) {
  emit('update:filters', { ...props.filters, volunteerId: id })
}

watch(hasActiveFilters, () => {
  volunteerAutocompleteRef.value?.refreshPosition()
})
</script>