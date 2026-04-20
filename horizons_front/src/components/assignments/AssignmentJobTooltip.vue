<template>
  <Teleport to="body">
    <Transition name="tip">
      <div
        v-if="show"
        class="fixed z-40 pointer-events-none"
        :style="style"
      >
        <div class="bg-slate-900/95 backdrop-blur-sm border border-white/12 rounded-xl shadow-2xl p-3 min-w-44 max-w-56">

          <!-- Nom du poste -->
          <div class="flex items-center gap-2 mb-2">
            <div class="w-1.5 h-1.5 rounded-full shrink-0" :style="{ background: categoryColor }" />
            <p class="text-xs font-semibold text-white leading-tight truncate">{{ job.name }}</p>
          </div>

          <!-- Horaire + jour -->
          <p class="text-[10px] text-slate-400 mb-2 flex items-center gap-1">
            <Clock class="w-2.5 h-2.5 shrink-0" />
            {{ dayLabel }} · {{ formatHour(job.slot.start_time) }}→{{ formatHour(job.slot.end_time) }}
            <span class="text-slate-500">({{ durationHours }}h)</span>
          </p>

          <!-- Barre remplissage -->
          <div class="flex items-center gap-2">
            <div class="h-1 flex-1 bg-slate-700 rounded-full overflow-hidden">
              <div
                class="h-full rounded-full transition-all"
                :class="fillBarColor"
                :style="{ width: `${fillPercent}%` }"
              />
            </div>
            <span class="text-[10px] font-mono shrink-0" :class="fillTextColor">
              {{ assignedCount }}/{{ job.required_volunteers }}
            </span>
          </div>

          <!-- Liste bénévoles si affectés (max 3 + "et N autres") -->
          <div v-if="assignedList.length > 0" class="mt-2 pt-2 border-t border-white/8 space-y-1">
            <p
              v-for="a in previewList"
              :key="a.volunteer_id"
              class="text-[10px] text-slate-300 flex items-center gap-1.5"
            >
              <span
                class="w-3 h-3 rounded shrink-0 flex items-center justify-center text-[7px] font-bold text-white"
                :style="{ background: chipColor(a.volunteer_id) }"
              >{{ getInitials(getVolunteerName(a.volunteer_id)) }}</span>
              {{ getVolunteerName(a.volunteer_id) }}
            </p>
            <p v-if="assignedList.length > MAX_PREVIEW" class="text-[10px] text-slate-500 italic">
              + {{ assignedList.length - MAX_PREVIEW }} autre{{ assignedList.length - MAX_PREVIEW > 1 ? 's' : '' }}
            </p>
          </div>
          <p v-else class="mt-1.5 text-[10px] text-slate-500 italic">Aucun bénévole affecté</p>
        </div>
        <!-- Flèche -->
        <div class="flex justify-center -mt-px">
          <div class="w-2 h-2 bg-slate-900 border-r border-b border-white/12 rotate-45" />
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Clock } from 'lucide-vue-next'
import { storeToRefs } from 'pinia'
import { useAssignmentStore } from '../../stores/useAssignmentStore'
import { useBenevoles } from '../../composables/useBenevoles'
import { useFestivalDays } from '../../composables/useFestivalDays'
import { getCategoryColor } from '../../utils/CategoryColor'
import { getInitials } from '../../utils/stringUtils'
import type { JobWithRelations } from '../../types/planning.types'
import type { Assignment } from '../../types/assignment.types'

const MAX_PREVIEW = 3

const props = defineProps<{
  show:       boolean
  job:        JobWithRelations
  colorIndex: number
  anchorRect: DOMRect | null
}>()

const store = useAssignmentStore()
const { assignmentsByJob } = storeToRefs(store)
const { volunteers }       = useBenevoles()
const { festivalDays }     = useFestivalDays()

// ── Position — au-dessus du bloc ──────────────────────────────────────────────
const style = computed(() => {
  if (!props.anchorRect) return { display: 'none' }
  const r = props.anchorRect
  return {
    top:       `${r.top - 8}px`,
    left:      `${r.left + r.width / 2}px`,
    transform: 'translate(-50%, -100%)',
  }
})

// ── Données ────────────────────────────────────────────────────────────────────
const assignedList = computed<Assignment[]>(() => assignmentsByJob.value.get(props.job.id) ?? [])
const assignedCount = computed(() => assignedList.value.length)
const previewList   = computed(() => assignedList.value.slice(0, MAX_PREVIEW))
const fillPercent   = computed(() =>
  props.job.required_volunteers > 0 ? (assignedCount.value / props.job.required_volunteers) * 100 : 0
)
const isFull  = computed(() => assignedCount.value >= props.job.required_volunteers)
const isEmpty = computed(() => assignedCount.value === 0)

// ── Jour lisible ──────────────────────────────────────────────────────────────
// On cherche le FestivalDay dont day === job.slot.day_index pour avoir le vrai label
const dayLabel = computed(() => {
  const fd = festivalDays.value.find(d => d.day === props.job.slot.day_index)
  // Label court : "Vendredi 5 Juin 2026" → "Vendredi 5 Juin"
  if (!fd) return `Jour ${props.job.slot.day_index}`
  const parts = fd.label.split(' ')
  return parts.slice(0, 3).join(' ')  // "Vendredi 5 Juin"
})

// ── Bénévoles ──────────────────────────────────────────────────────────────────
function getVolunteerName(id: string): string {
  const v = volunteers.value.find(v => v.id === id)
  return v ? `${v.first_name} ${v.last_name}` : id.slice(0, 8)
}
function chipColor(id: string): string {
  const hue = id.split('').slice(0, 4).reduce((acc, c) => acc + c.charCodeAt(0), 0) % 360
  return `hsl(${hue}, 50%, 38%)`
}

const categoryColor = computed(() => getCategoryColor(props.colorIndex))
const durationHours = computed(() => props.job.slot.end_time - props.job.slot.start_time)

function formatHour(h: number): string {
  return `${h > 23 ? h - 24 : h}h`
}

const fillTextColor = computed(() => isEmpty.value ? 'text-red-400'  : isFull.value ? 'text-green-400' : 'text-amber-400')
const fillBarColor  = computed(() => isEmpty.value ? 'bg-red-400'    : isFull.value ? 'bg-green-400'   : 'bg-amber-400')
</script>

<style scoped>
.tip-enter-active { transition: opacity 0.12s ease, transform 0.12s ease; }
.tip-leave-active { transition: opacity 0.08s ease; }
.tip-enter-from   { opacity: 0; transform: translate(-50%, calc(-100% + 4px)); }
.tip-leave-to     { opacity: 0; }
</style>