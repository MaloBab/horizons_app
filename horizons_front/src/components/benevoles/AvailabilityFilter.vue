<template>
  <div class="flex flex-col w-full" style="gap: 10px;">

    <!-- Ligne 1 : label + chips + compteur global + reset -->
    <div class="flex flex-wrap items-center" style="gap: 8px;">
      <span class="text-[11px] font-medium uppercase tracking-widest text-slate-500 whitespace-nowrap shrink-0">
        Disponibilité
      </span>

      <!-- Chips jours -->
      <div class="flex flex-wrap min-w-0" style="gap: 6px;">
        <button
          v-for="day in festivalDays"
          :key="day.offset"
          @click="selectDay(day.offset)"
          class="day-chip inline-flex items-center rounded-full text-xs font-medium cursor-pointer select-none whitespace-nowrap transition-all duration-150"
          :class="selectedDay === day.offset ? 'day-chip--active' : 'day-chip--idle'"
          style="padding: 3px 10px;"
        >
          {{ day.shortLabel }}
        </button>

        <div v-if="festivalDays.length === 0" class="text-xs text-slate-600 italic">
          Aucun festival configuré
        </div>
      </div>

      <!-- Compteur global -->
      <Transition
        enter-active-class="transition-all duration-200 ease-out"
        enter-from-class="opacity-0 scale-90"
        enter-to-class="opacity-100 scale-100"
        leave-active-class="transition-all duration-150 ease-in"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-90"
      >
        <span
          class="inline-flex items-center whitespace-nowrap tabular-nums"
          style="font-size: 11px; color: #64748b;"
        >
          <span style="color: #a5b4fc; font-weight: 500; font-size: 13px;">{{ props.filteredVolunteersLenght }}</span>
          <span style="margin-left: 3px;">bénévole{{ filteredVolunteersLenght !== 1 ? 's' : '' }}</span>
        </span>
      </Transition>

      <!-- Spacer -->
      <div class="flex-1" />

      <!-- Bouton réinitialiser -->
      <Transition
        enter-active-class="transition-all duration-200 ease-out"
        enter-from-class="opacity-0 scale-95"
        enter-to-class="opacity-100 scale-100"
        leave-active-class="transition-all duration-150 ease-in"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-95"
      >
        <button
          v-if="isActive"
          @click="reset"
          class="reset-btn inline-flex items-center shrink-0 select-none font-medium rounded-lg transition-all duration-150"
          style="gap: 5px; padding: 3px 10px; font-size: 11px;"
        >
          <RotateCcw style="width: 11px; height: 11px;" />
          Réinitialiser
        </button>
      </Transition>
    </div>

    <!-- Ligne 2 : timeline -->
    <div class="flex flex-col" style="gap: 4px; --side: 38px; --gap: 8px;">

      <!-- Track row -->
      <div class="flex items-center" style="gap: var(--gap);">

        <!-- Borne gauche -->
        <span
          class="text-[12px] font-medium tabular-nums text-right shrink-0 transition-colors duration-100"
          :class="selStart !== null ? 'text-slate-200' : 'text-slate-700'"
          style="width: var(--side);"
        >
          {{ selStart !== null ? fmtHour(HOURS[selStart]!) : '—' }}
        </span>

        <!-- Track -->
        <div
          ref="tlRef"
          class="relative flex-1 rounded-lg cursor-crosshair select-none"
          style="height: 28px; background: rgba(15,23,42,0.7); border: 0.5px solid rgba(148,163,184,0.12);"
          @mousedown.prevent="onTlMousedown"
        >
          <!-- Grille -->
          <div class="absolute inset-0 flex rounded-lg overflow-hidden pointer-events-none">
            <div
              v-for="(_, i) in HOURS"
              :key="i"
              class="flex-1"
              style="border-right: 0.5px solid rgba(148,163,184,0.07);"
            />
          </div>

          <!-- Sélection -->
          <div
            v-if="selStart !== null && selEnd !== null"
            class="absolute pointer-events-none rounded-md"
            style="top: 3px; bottom: 3px; background: rgba(99,102,241,0.22); border: 0.5px solid rgba(99,102,241,0.45);"
            :style="selStyle"
          />

          <!-- Poignée gauche -->
          <div
            v-if="selStart !== null"
            class="absolute top-1/2 -translate-y-1/2 z-10 cursor-ew-resize"
            style="width: 8px; height: 18px; background: #818cf8; border-radius: 3px;"
            :style="{ left: `calc(${idxToFrac(selStart) * 100}% - 4px)` }"
            @mousedown.stop.prevent="startDrag('left')"
          />

          <!-- Poignée droite -->
          <div
            v-if="selEnd !== null"
            class="absolute top-1/2 -translate-y-1/2 z-10 cursor-ew-resize"
            style="width: 8px; height: 18px; background: #818cf8; border-radius: 3px;"
            :style="{ left: `calc(${idxToFrac(rightEdgeIdx) * 100}% - 4px)` }"
            @mousedown.stop.prevent="startDrag('right')"
          />
        </div>

        <!-- Borne droite -->
        <span
          class="text-[12px] font-medium tabular-nums text-left shrink-0 transition-colors duration-100"
          :class="selEnd !== null ? 'text-slate-200' : 'text-slate-700'"
          style="width: var(--side);"
        >
          {{ selEnd !== null ? fmtHour(HOURS[rightEdgeIdx] ?? 30) : '—' }}
        </span>
      </div>

      <!-- Ticks — padding = --side + --gap de chaque côté pour aligner avec la track -->
      <div style="padding: 0 calc(var(--side) + var(--gap));">
        <div class="relative w-full" style="height: 14px;">
          <span
            v-for="tick in visibleTicks"
            :key="tick.h"
            class="absolute text-[10px] whitespace-nowrap"
            :class="tick.edge ? 'text-slate-500 font-medium' : 'text-slate-600'"
            :style="tickStyle(tick)"
          >{{ tick.label }}</span>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { RotateCcw } from 'lucide-vue-next'
import type { Volunteer } from '../../types/benevole.types'
import { useFestivalStore } from '../../stores/useFestivalStore'
import { useAssignmentStore } from '../../stores/useAssignmentStore'

const props = defineProps<{ volunteers: Volunteer[], filteredVolunteersLenght: number }>()
const emit  = defineEmits<{ filter: [ids: Set<string> | null] }>()

const festivalStore   = useFestivalStore()
const assignmentStore = useAssignmentStore()

// ─── Heures ───────────────────────────────────────────────────────────────────

const HOURS   = Array.from({ length: 23 }, (_, i) => i + 8)
const N       = HOURS.length   
const MAX_IDX = N - 1

const fmtHour = (h: number) => `${h >= 24 ? h - 24 : h}h`

// Tous les ticks possibles, du plus dense au plus espacé
// On filtre selon la largeur de la track au runtime
const ALL_TICK_SETS: number[][] = [
  [8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30],  // >= ~500px
  [8, 12, 16, 20, 24, 28, 30],                       // >= ~280px
  [8, 16, 24, 30],                                   // >= ~140px
  [8, 30],                                           // fallback
]

// Largeur de la track observée via ResizeObserver
const trackWidth = ref(0)
const tlRef      = ref<HTMLElement | null>(null)

let ro: ResizeObserver | null = null

// Ticks adaptés à la largeur disponible
// On choisit le set le plus dense qui tient dans la largeur
// (chaque label ~24px, on veut au moins 20px entre labels)
const activeTicks = computed(() => {
  const w = trackWidth.value
  if (w === 0) return ALL_TICK_SETS[0]!
  // Nombre de labels max qui tiennent (label ≈ 24px, espacement min 16px)
  const maxLabels = Math.floor(w / 40) + 2
  for (const set of ALL_TICK_SETS) {
    if (set.length <= maxLabels) return set
  }
  return ALL_TICK_SETS[ALL_TICK_SETS.length - 1]!
})

const visibleTicks = computed(() => {
  return activeTicks.value
    .map(h => {
      const idx = HOURS.indexOf(h)
      if (idx < 0) return null
      return { h, frac: idx / MAX_IDX, label: fmtHour(h), edge: h === 8 || h === 30 }
    })
    .filter(Boolean) as { h: number; frac: number; label: string; edge: boolean }[]
})

function tickStyle(tick: { frac: number; h: number }) {
  if (tick.h === 8)  return { left: '0',  transform: 'none' }
  if (tick.h === 30) return { right: '0', transform: 'none' }
  return { left: `${tick.frac * 100}%`, transform: 'translateX(-50%)' }
}

// ─── Jours ────────────────────────────────────────────────────────────────────

const DAY_SHORT = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
const DAY_FULL  = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']

const festivalDays = computed(() => {
  const f = festivalStore.festival
  if (!f?.start_date || !f?.end_date) return []
  const cursor = new Date(f.start_date)
  const end    = new Date(f.end_date)
  const result: { offset: number; dayIndex: number; shortLabel: string; fullLabel: string }[] = []
  let offset = 0
  while (cursor <= end) {
    const dayIndex = (cursor.getDay() + 6) % 7
    result.push({ offset, dayIndex,
      shortLabel: `${DAY_SHORT[dayIndex]} ${cursor.getDate()}/${cursor.getMonth() + 1}`,
      fullLabel:  `${DAY_FULL[dayIndex]} ${cursor.getDate().toString().padStart(2,'0')}/${(cursor.getMonth()+1).toString().padStart(2,'0')}`,
    })
    cursor.setDate(cursor.getDate() + 1)
    offset++
  }
  return result
})

watch(festivalDays, (days) => {
  if (selectedDay.value !== null && !days.find(d => d.offset === selectedDay.value))
    selectedDay.value = null
})

// ─── État ─────────────────────────────────────────────────────────────────────

const selectedDay = ref<number | null>(null)
const selStart    = ref<number | null>(null)
const selEnd      = ref<number | null>(null)

function selectDay(offset: number) {
  selectedDay.value = selectedDay.value === offset ? null : offset
}

const rightEdgeIdx = computed((): number => {
  if (selEnd.value === null) return MAX_IDX
  return Math.min(selEnd.value + 1, MAX_IDX)
})

// ─── Drag ─────────────────────────────────────────────────────────────────────

let dragType: 'new' | 'left' | 'right' | null = null
let dragAnchor = 0

function getFrac(e: MouseEvent): number {
  const r = tlRef.value?.getBoundingClientRect()
  if (!r) return 0
  return Math.max(0, Math.min(1, (e.clientX - r.left) / r.width))
}

function fracToSlotIdx(f: number): number { return Math.min(Math.round(f * MAX_IDX), MAX_IDX - 1) }
function fracToEdgeIdx(f: number): number { return Math.min(Math.round(f * MAX_IDX), MAX_IDX) }
function idxToFrac(i: number): number     { return i / MAX_IDX }

function onTlMousedown(e: MouseEvent) {
  dragType   = 'new'
  dragAnchor = fracToSlotIdx(getFrac(e))
  selStart.value = dragAnchor
  selEnd.value   = dragAnchor
}

function startDrag(type: 'left' | 'right') { dragType = type }

function onMousemove(e: MouseEvent) {
  if (!dragType) return
  const f = getFrac(e)
  if (dragType === 'new') {
    const idx = fracToSlotIdx(f)
    selStart.value = Math.min(dragAnchor, idx)
    selEnd.value   = Math.max(dragAnchor, idx)
  } else if (dragType === 'left') {
    selStart.value = Math.min(fracToSlotIdx(f), selEnd.value ?? 0)
  } else {
    const edgeIdx = fracToEdgeIdx(f)
    selEnd.value  = Math.min(Math.max(edgeIdx - 1, selStart.value ?? 0), MAX_IDX - 1)
  }
}

function onMouseup() { dragType = null }

onMounted(() => {
  if (!festivalStore.festival && !festivalStore.isLoading) festivalStore.fetchFestival()
  document.addEventListener('mousemove', onMousemove)
  document.addEventListener('mouseup',   onMouseup)

  // ResizeObserver sur la track pour adapter les ticks
  if (tlRef.value) {
    ro = new ResizeObserver(entries => {
      trackWidth.value = entries[0]?.contentRect.width ?? 0
    })
    ro.observe(tlRef.value)
    trackWidth.value = tlRef.value.getBoundingClientRect().width
  }
})

onUnmounted(() => {
  document.removeEventListener('mousemove', onMousemove)
  document.removeEventListener('mouseup',   onMouseup)
  ro?.disconnect()
})

// ─── Style sélection ──────────────────────────────────────────────────────────

const selStyle = computed(() => {
  if (selStart.value === null || selEnd.value === null) return {}
  const l = idxToFrac(selStart.value)
  const r = idxToFrac(rightEdgeIdx.value)
  return { left: `${l * 100}%`, width: `${(r - l) * 100}%` }
})

// ─── Disponibilité ────────────────────────────────────────────────────────────

function availableHours(volunteerId: string, dayIndex: number): Set<number> {
  const v = props.volunteers.find(v => v.id === volunteerId)
  if (!v) return new Set()
  const avail = new Set<number>()
  for (const vs of v.slots) {
    if (vs.slot.day_index !== dayIndex) continue
    for (let h = vs.slot.start_time; h < vs.slot.end_time; h++) {
      if (!assignmentStore.consumedSlotKeys.has(`${volunteerId}__${dayIndex}__${h}`)) avail.add(h)
    }
  }
  return avail
}

const hasTime  = computed(() => selStart.value !== null && selEnd.value !== null)
const hasDays  = computed(() => selectedDay.value !== null)
const isActive = computed(() => hasTime.value || hasDays.value)

const selectedHours = computed((): number[] => {
  if (!hasTime.value) return []
  const hours: number[] = []
  for (let i = selStart.value!; i <= selEnd.value!; i++) hours.push(HOURS[i]!)
  return hours
})

function volunteerPasses(volunteerId: string, dayIndex: number | null): boolean {
  if (dayIndex !== null) {
    const avail = availableHours(volunteerId, dayIndex)
    return hasTime.value ? selectedHours.value.every(h => avail.has(h)) : avail.size > 0
  }
  return festivalDays.value.every(day => {
    const avail = availableHours(volunteerId, day.dayIndex)
    return hasTime.value ? selectedHours.value.every(h => avail.has(h)) : avail.size > 0
  })
}

const matchingIds = computed((): Set<string> | null => {
  if (!isActive.value) return null
  const ids = new Set<string>()
  const dayIndex = hasDays.value
    ? (festivalDays.value.find(d => d.offset === selectedDay.value)?.dayIndex ?? null)
    : null
  for (const volunteer of props.volunteers) {
    if (volunteerPasses(volunteer.id, dayIndex)) ids.add(volunteer.id)
  }
  return ids
})

watch(matchingIds, ids => emit('filter', ids), { immediate: true })

// ─── Reset ────────────────────────────────────────────────────────────────────

function reset() {
  selectedDay.value = null
  selStart.value    = null
  selEnd.value      = null
}
</script>

<style scoped>
.day-chip {
  border: 0.5px solid;
}
.day-chip--idle {
  border-color: rgba(148, 163, 184, 0.2);
  color: #64748b;
  background: transparent;
}
.day-chip--idle:hover {
  border-color: rgba(148, 163, 184, 0.4);
  color: #94a3b8;
}
.day-chip--active {
  border-color: rgba(99, 102, 241, 0.5);
  color: #a5b4fc;
  background: rgba(99, 102, 241, 0.12);
}
.reset-btn {
  background: rgba(99, 102, 241, 0.08);
  border: 0.5px solid rgba(99, 102, 241, 0.25);
  color: #a5b4fc;
}
.reset-btn:hover {
  background: rgba(99, 102, 241, 0.16);
  border-color: rgba(99, 102, 241, 0.4);
}
.reset-btn:active {
  background: rgba(99, 102, 241, 0.22);
  transform: scale(0.97);
}
</style>