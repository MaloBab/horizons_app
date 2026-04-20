<template>
  <div
    :draggable="true"
    @dragstart="onDragStart"
    @dragend="onDragEnd"
    @click="onClick"
    @dblclick="onDblClick"
    class="group relative rounded-xl border px-3 py-2.5 cursor-grab active:cursor-grabbing transition-all duration-200 select-none"
    :class="[
      isDragging ? 'opacity-40 scale-95' : 'hover:-translate-y-0.5 hover:shadow-lg',
      isAssigned
        ? 'bg-slate-800/60 border-orange-400/25 hover:border-orange-400/40'
        : 'bg-slate-800/60 border-green-400/25 hover:border-green-400/40',
    ]"
  >
    <!-- Ligne principale -->
    <div class="flex items-center gap-2.5">
      <!-- Avatar -->
      <div
        class="w-8 h-8 rounded-lg shrink-0 flex items-center justify-center text-xs font-bold text-white"
        :class="volunteer.volunteer_type === 'Specialise'
          ? 'bg-linear-to-br from-amber-500/40 to-orange-600/40 border border-amber-500/30'
          : 'bg-linear-to-br from-slate-600/60 to-slate-700/60 border border-white/10'"
      >
        {{ initials }}
      </div>

      <!-- Nom + badges -->
      <div class="flex-1 min-w-0">
        <p class="text-sm font-medium text-white truncate leading-tight">
          {{ volunteer.first_name }} {{ volunteer.last_name }}
        </p>
        <div class="flex items-center gap-1.5 mt-0.5">
          <span class="text-[10px] font-semibold px-1.5 py-0.5 rounded border"
            :class="volunteer.volunteer_type === 'Specialise'
              ? 'bg-amber-500/15 text-amber-400 border-amber-500/25'
              : 'bg-slate-600/40 text-slate-400 border-white/10'">
            {{ volunteer.volunteer_type === 'Specialise' ? 'Spéc.' : 'Normal' }}
          </span>
          <span v-if="metrics?.daily_limit_exceeded"
            class="text-[10px] font-semibold px-1.5 py-0.5 rounded border bg-red-500/15 text-red-400 border-red-500/25"
            title="Limite horaire journalière dépassée">
            ⚠ Limite
          </span>
        </div>
      </div>

      <!-- Statut -->
      <div class="shrink-0 text-right">
        <p class="text-xs font-mono font-bold" :class="isAssigned ? 'text-cyan-400' : 'text-slate-500'">
          {{ isAssigned ? `${metrics?.total_hours ?? 0}h` : '' }}
        </p>
        <p class="text-[12px] text-slate-500 leading-tight">{{ isAssigned ? 'affecté' : 'Libre' }}</p>
      </div>
    </div>

    <!-- Métriques secondaires (si affecté) -->
    <div v-if="isAssigned && metrics" class="flex items-center gap-3 mt-2 pt-2 border-t border-white/5">
      <div class="flex items-center gap-1.5 flex-1">
        <div class="h-1 flex-1 bg-slate-700 rounded-full overflow-hidden">
          <div class="h-full rounded-full transition-all duration-500"
            :class="satisfactionBarColor"
            :style="{ width: `${Math.round((metrics.satisfaction_score ?? 0) * 100)}%` }" />
        </div>
        <span class="text-[10px] font-mono text-slate-400 w-7 text-right">
          {{Math.round((metrics.satisfaction_score ?? 0) * 100)}}%
        </span>
      </div>
      <div v-if="volunteer.mates.length > 0"
        class="flex items-center gap-1 text-[10px]"
        :class="metrics.slots_with_mate > 0 ? 'text-pink-400' : 'text-slate-500'"
        :title="`${metrics.slots_with_mate} créneaux avec compagnon`">
        <Heart class="w-3 h-3" />
        <span>{{ metrics.slots_with_mate }}/{{ metrics.slots_with_mate + metrics.slots_without_mate }}</span>
      </div>
    </div>

    <!-- Heures par jour -->
    <div v-if="isAssigned && metrics && Object.keys(metrics.hours_per_day).length > 0"
      class="flex items-center gap-1 mt-1.5">
      <div v-for="(hours, day) in metrics.hours_per_day" :key="day"
        class="flex flex-col items-center gap-0.5" :title="`Jour ${Number(day) + 1} : ${hours}h`">
        <div class="w-5 h-1 rounded-full" :class="isOverLimit(hours) ? 'bg-red-400' : 'bg-cyan-500/60'" />
        <span class="text-[9px] font-mono text-slate-500">{{ hours }}h</span>
      </div>
    </div>

    <!-- Préférence #1 -->
    <div v-if="topPreference" class="mt-1.5">
      <span class="text-[10px] text-slate-500">
        Pref : <span class="text-slate-300">{{ topPreference }}</span>
      </span>
    </div>

    <!-- Élément invisible pour supprimer le ghost drag natif du navigateur -->
    <div ref="ghostKillerRef" class="fixed -left-2499 -top-2499 w-1 h-1 opacity-0 pointer-events-none" aria-hidden="true" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Heart } from 'lucide-vue-next'
import { useDragState } from '../../composables/useDragState'
import type { Volunteer } from '../../types/benevole.types'
import type { VolunteerMetrics } from '../../types/assignment.types'
import { DAILY_HOUR_LIMITS } from '../../types/assignment.types'
import { getInitials } from '../../utils/stringUtils'

const props = defineProps<{ volunteer: Volunteer; metrics: VolunteerMetrics | undefined }>()
const emit  = defineEmits<{
  click:     [volunteer: Volunteer]
  dblclick: [volunteer: Volunteer]
  dragstart: [volunteerId: string]
  dragend:   []
}>()

const { startDrag, endDrag } = useDragState()
const isDragging     = ref(false)
const ghostKillerRef = ref<HTMLElement | null>(null)

const clickTimer = ref<ReturnType<typeof setTimeout> | null>(null)
const initials      = computed(() => getInitials(`${props.volunteer.first_name} ${props.volunteer.last_name}`))
const isAssigned    = computed(() => (props.metrics?.assignment_count ?? 0) > 0)
const topPreference = computed(() => {
  if (!props.volunteer.preferences.length) return null
  return [...props.volunteer.preferences].sort((a, b) => a.rank - b.rank)[0]?.preference.label ?? null
})

const satisfactionBarColor = computed(() => {
  const s = props.metrics?.satisfaction_score ?? 0
  if (s >= 0.75) return 'bg-green-400'
  if (s >= 0.4)  return 'bg-amber-400'
  return 'bg-red-400'
})

function isOverLimit(hours: number): boolean {
  const limit = DAILY_HOUR_LIMITS[props.volunteer.volunteer_type as keyof typeof DAILY_HOUR_LIMITS] ?? 6
  return hours > limit
}

function onDragStart(e: DragEvent) {
  isDragging.value = true
  e.dataTransfer?.setData('volunteer_id', props.volunteer.id)
  if (e.dataTransfer) e.dataTransfer.effectAllowed = 'move'

  // Remplacer le ghost natif du navigateur par un pixel invisible —
  // c'est le seul moyen fiable avec l'API HTML5 native (pas vue-draggable).
  // Notre DragGhostCard suit le curseur via l'événement dragover sur document.
  if (e.dataTransfer && ghostKillerRef.value) {
    try {
      e.dataTransfer.setDragImage(ghostKillerRef.value, 0, 0)
    } catch (_) {
      // Safari peut ignorer setDragImage dans certaines conditions — on tolère
    }
  }

  startDrag(props.volunteer.id, 'sidebar')
  emit('dragstart', props.volunteer.id)
}


function onClick() {
  if (clickTimer.value) {
    clearTimeout(clickTimer.value)
    clickTimer.value = null
    return
  }
  clickTimer.value = setTimeout(() => {
    clickTimer.value = null
    emit('click', props.volunteer)
  }, 200)
}

function onDblClick() {
  if (clickTimer.value) {
    clearTimeout(clickTimer.value)
    clickTimer.value = null
  }
  emit('dblclick', props.volunteer)
}


function onDragEnd() {
  isDragging.value = false
  endDrag()
  emit('dragend')
}
</script>