<template>
  <section class="bg-slate-700/30 rounded-xl p-3 border border-slate-600/40 h-full">
    <div class="flex items-center justify-between mb-3">
      <h3 class="text-sm font-semibold text-white flex items-center gap-2">
        <Calendar class="w-4 h-4 text-green-400" />
        Disponibilités
        <span class="text-slate-400 text-xs font-normal">({{ volunteer.slots.length }} créneaux)</span>
      </h3>
      <button
        @click="$emit('toggle-edit')"
        class="p-1.5 rounded-lg transition-colors"
        :class="isEditing ? 'bg-green-500/20 text-green-300' : 'hover:bg-slate-600 text-slate-400'"
      >
        <Pencil class="w-3.5 h-3.5" />
      </button>
    </div>

    <!-- ── Lecture ─────────────────────────────────────────────────────────── -->
    <div v-if="!isEditing">
      <div v-if="displayGroups.length > 0" class="space-y-3 max-h-130 overflow-y-auto pr-1 custom-scrollbar">
        <div v-for="(group, gi) in displayGroups" :key="gi">
          <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5">{{ group.day }}</p>
          <div class="space-y-1">
            <div
              v-for="(slot, si) in group.slots" :key="si"
              class="bg-slate-700/50 rounded-lg px-3 py-2 border flex items-center justify-between"
              :class="slot.consumed
                ? 'border-amber-500/40 opacity-50'
                : 'border-slate-600/50'"
            >
              <span class="text-white text-sm font-medium">{{ slot.label }}</span>
              <Clock
                class="w-4 h-4 shrink-0"
                :class="slot.consumed ? 'text-amber-400' : 'text-green-400'"
              />
            </div>
          </div>
        </div>
      </div>
      <p v-else class="text-slate-400 text-xs text-center py-8">Aucune disponibilité enregistrée</p>
    </div>

    <!-- ── Édition ─────────────────────────────────────────────────────────── -->
    <div v-else class="space-y-3 max-h-130 overflow-y-auto pr-1 custom-scrollbar">

      <div class="flex items-center gap-3 text-xs text-slate-500 bg-slate-700/30 rounded-lg px-3 py-2">
        <span class="flex items-center gap-1">
          <span class="inline-block w-3 h-3 rounded-sm bg-green-500/25 border border-green-500/60"></span>
          Actif — cliquer pour retirer
        </span>
        <span class="flex items-center gap-1">
          <span class="inline-block w-3 h-3 rounded-sm bg-slate-700 border border-slate-600"></span>
          Inactif — cliquer pour ajouter
        </span>
      </div>

      <div v-for="(bloc, bi) in editBlocs" :key="bi">
        <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
          {{ bloc.label }}
        </p>
        <div class="grid grid-cols-5 gap-1">
          <button
            v-for="hour in bloc.hours" :key="hour"
            @click="$emit('toggle-slot', bloc.dayIndex, hour)"
            :disabled="loadingSlotKey === `${bloc.dayIndex}-${hour}`"
            class="relative text-xs rounded-md py-1.5 font-medium transition-all border"
            :class="hasSlot(bloc.dayIndex, hour)
              ? 'bg-green-500/25 border-green-500/60 text-green-300 hover:bg-red-500/20 hover:border-red-500/50 hover:text-red-300'
              : 'bg-slate-700/50 border-slate-600/50 text-slate-500 hover:bg-green-500/10 hover:border-green-500/30 hover:text-green-400'"
          >
            <Loader2 v-if="loadingSlotKey === `${bloc.dayIndex}-${hour}`" class="w-3 h-3 animate-spin mx-auto" />
            <span v-else>{{ hour >= 24 ? `${hour - 24}h` : `${hour}h` }}</span>
          </button>
        </div>
      </div>

    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Calendar, Clock, Pencil, Loader2 } from 'lucide-vue-next'
import type { Volunteer } from '../../../types/benevole.types'
import { JOURS_SEMAINE } from '../../../types/benevole.types'

const props = defineProps<{
  volunteer:        Volunteer
  isEditing:        boolean
  loadingSlotKey:   string | null
  consumedSlotKeys: ReadonlySet<string>
}>()

defineEmits<{
  'toggle-edit': []
  'toggle-slot': [dayIndex: number, hour: number]
}>()

// ── Constantes ────────────────────────────────────────────────────────────────
const STORED_DAY_INDICES = [3, 4, 5, 6]
const HOURS_DAY   = Array.from({ length: 16 }, (_, i) => i + 8)  // [8..23]
const HOURS_NIGHT = Array.from({ length: 6  }, (_, i) => i + 24) // [24..29]

// ── Structure des blocs d'édition ────────────────────────────────────────────
interface EditBloc { label: string; dayIndex: number; hours: number[] }

const editBlocs = computed<EditBloc[]>(() => {
  const blocs: EditBloc[] = []
  for (const dayIndex of STORED_DAY_INDICES) {
    blocs.push({
      label:    JOURS_SEMAINE[dayIndex] ?? `Jour ${dayIndex}`,
      dayIndex,
      hours:    HOURS_DAY,
    })
    blocs.push({
      label:    (JOURS_SEMAINE[dayIndex] ?? `Jour ${dayIndex}`) + ' (nuit)',
      dayIndex,
      hours:    HOURS_NIGHT,
    })
  }
  return blocs
})

// ── Set réactif des slots disponibles ────────────────────────────────────────
const slotSet = computed(() => new Set(
  props.volunteer.slots.map(vs =>
    `${vs.slot.day_index}-${vs.slot.start_time}-${vs.slot.end_time}`
  )
))

function hasSlot(dayIndex: number, hour: number): boolean {
  return slotSet.value.has(`${dayIndex}-${hour}-${hour + 1}`)
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function fmtH(h: number): string {
  return `${h >= 24 ? h - 24 : h}h`
}

// ── Calcul des groupes d'affichage (lecture) ──────────────────────────────────
//
// On explose chaque VolunteerSlot en heures unitaires, puis on sépare
// les heures "libres" des heures "consommées" (affectation existante).
// Les deux séries sont ensuite fusionnées en plages contiguës séparément,
// ce qui produit naturellement la fragmentation autour des affectations.
//
// Ex : disponible 8h–20h, affecté 18h–20h
//   → plage libre  : 8h–18h
//   → plage occupée: 18h–20h (affichée atténuée)

interface DisplaySlot { label: string; consumed: boolean }
interface DayGroup    { day: string; slots: DisplaySlot[] }

const displayGroups = computed<DayGroup[]>(() => {
  // Collecter toutes les heures unitaires, tagguées libre/consommée
  const allHours: { day_index: number; hour: number; consumed: boolean }[] = []

  for (const vs of props.volunteer.slots) {
    const { day_index, start_time, end_time } = vs.slot
    for (let h = start_time; h < end_time; h++) {
      const key      = `${props.volunteer.id}__${day_index}__${h}`
      const consumed = props.consumedSlotKeys.has(key)
      allHours.push({ day_index, hour: h, consumed })
    }
  }

  // Trier par jour, puis heure
  allHours.sort((a, b) => a.day_index - b.day_index || a.hour - b.hour)

  // Fusionner les heures contiguës de même statut (libre OU consommée)
  const merged: { day_index: number; start: number; end: number; consumed: boolean }[] = []
  for (const { day_index, hour, consumed } of allHours) {
    const last = merged[merged.length - 1]
    if (
      last &&
      last.day_index === day_index &&
      last.consumed  === consumed  &&
      last.end       === hour
    ) {
      last.end = hour + 1
    } else {
      merged.push({ day_index, start: hour, end: hour + 1, consumed })
    }
  }

  // Grouper par jour
  const map = new Map<number, DisplaySlot[]>()
  for (const { day_index, start, end, consumed } of merged) {
    const label = `${fmtH(start)} – ${fmtH(end)}`
    if (!map.has(day_index)) map.set(day_index, [])
    map.get(day_index)!.push({ label, consumed })
  }

  return Array.from(map.entries())
    .sort(([a], [b]) => a - b)
    .map(([dayIndex, slots]) => ({
      day: JOURS_SEMAINE[dayIndex] ?? `Jour ${dayIndex}`,
      slots,
    }))
})
</script>