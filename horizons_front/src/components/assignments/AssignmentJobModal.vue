<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        @click.self="$emit('update:modelValue', false)"
      >
        <!-- Backdrop -->
        <div
          class="absolute inset-0 bg-slate-950/80 backdrop-blur-sm"
          @click="$emit('update:modelValue', false)"
        />

        <!-- Carte modale -->
        <div
          class="modal-card relative z-10 w-full max-w-md rounded-2xl overflow-hidden border border-white/10 shadow-2xl"
          style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 60%, #0f172a 100%)"
        >
          <!-- En-tête -->
          <div
            class="relative px-5 py-4 border-b border-white/8"
            :style="{ background: `linear-gradient(135deg, ${categoryColor}18 0%, transparent 60%)` }"
          >
            <div class="flex items-center gap-2.5 mb-3">
              <div class="w-2 h-2 rounded-full shrink-0" :style="{ background: categoryColor }" />
              <span class="text-[10px] font-semibold text-slate-400 uppercase tracking-widest">
                {{ job.category?.label ?? 'Poste' }}
              </span>
            </div>

            <h2 class="text-lg font-bold text-white leading-snug mb-1">{{ job.name }}</h2>

            <p class="text-xs text-slate-400 flex items-center gap-1.5">
              <Clock class="w-3 h-3 shrink-0" />
              {{ dayLabel }} ·
              {{ formatHour(job.slot.start_time) }} → {{ formatHour(job.slot.end_time) }}
              <span class="text-slate-500">({{ durationHours }}h)</span>
            </p>

            <button
              class="absolute top-4 right-4 p-1.5 rounded-lg text-slate-500 hover:text-white hover:bg-white/10 transition-all"
              @click="$emit('update:modelValue', false)"
            >
              <X class="w-4 h-4" />
            </button>
          </div>

          <!-- Corps -->
          <div class="px-5 py-4 space-y-4 max-h-[60vh] overflow-y-auto custom-scrollbar">

            <!-- Jauge -->
            <div>
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs text-slate-400">Remplissage</span>
                <span class="text-xs font-mono font-bold" :class="fillTextColor">
                  {{ assignedCount }}/{{ job.required_volunteers }}
                </span>
              </div>
              <div class="h-1.5 w-full bg-slate-700/60 rounded-full overflow-hidden">
                <div
                  class="h-full rounded-full transition-all duration-700"
                  :class="fillBarColor"
                  :style="{ width: `${fillPercent}%` }"
                />
              </div>
            </div>

            <!-- Bénévoles affectés -->
            <div v-if="assignedList.length > 0">
              <p class="text-[10px] font-semibold text-slate-500 uppercase tracking-widest mb-2.5">
                Bénévoles affectés
              </p>
              <TransitionGroup name="list" tag="div" class="space-y-1.5">
                <div
                  v-for="a in assignedList"
                  :key="a.volunteer_id"
                  class="flex items-center gap-3 px-3 py-2 rounded-lg border transition-all duration-150 cursor-pointer group
                         bg-slate-800/50 border-white/5
                         hover:bg-red-500/10 hover:border-red-500/25"
                  title="Cliquer pour désaffecter"
                  @click.stop="$emit('unassign', a.volunteer_id, job.id)"
                >
                  <div
                    class="w-7 h-7 rounded-lg shrink-0 flex items-center justify-center text-[9px] font-bold text-white transition-all"
                    :style="{ background: chipColor(a.volunteer_id) }"
                  >
                    {{ getVolunteerInitials(a.volunteer_id) }}
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="text-xs font-medium text-slate-200 truncate group-hover:text-red-300 transition-colors">
                      {{ getVolunteerName(a.volunteer_id) }}
                    </p>
                    <p class="text-[10px] text-slate-500 leading-tight">
                      {{ getVolunteerType(a.volunteer_id) }}
                    </p>
                  </div>
                  <UserMinus class="w-3.5 h-3.5 text-slate-600 opacity-0 group-hover:text-red-400 group-hover:opacity-100 transition-colors shrink-0" />
                </div>
              </TransitionGroup>
            </div>

            <!-- Badge complet -->
            <div
              v-if="isFull"
              class="flex items-center gap-2 px-3 py-2.5 rounded-lg bg-green-500/10 border border-green-500/20"
            >
              <CheckCircle2 class="w-4 h-4 text-green-400 shrink-0" />
              <span class="text-xs text-green-300 font-medium">Poste complet</span>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { X, Clock, UserMinus, CheckCircle2 } from 'lucide-vue-next'
import { storeToRefs } from 'pinia'
import { useAssignmentStore } from '../../stores/useAssignmentStore'
import { useBenevoles } from '../../composables/useBenevoles'
import { getCategoryColor } from '../../utils/CategoryColor'
import { useFestivalDays } from '../../composables/useFestivalDays'
import type { JobWithRelations } from '../../types/planning.types'
import type { Assignment } from '../../types/assignment.types'
import { getInitials } from '../../utils/stringUtils'

const props = defineProps<{
  modelValue: boolean
  job:        JobWithRelations
  colorIndex: number
}>()

defineEmits<{
  'update:modelValue': [value: boolean]
  unassign:            [volunteerId: string, jobId: number]
}>()

const store = useAssignmentStore()
const { assignmentsByJob } = storeToRefs(store)
const { volunteers }       = useBenevoles()

// ── Données ────────────────────────────────────────────────────────────────────
const assignedList  = computed<Assignment[]>(() => assignmentsByJob.value.get(props.job.id) ?? [])
const assignedCount = computed(() => assignedList.value.length)
const fillPercent   = computed(() =>
  props.job.required_volunteers > 0 ? (assignedCount.value / props.job.required_volunteers) * 100 : 0
)
const isFull  = computed(() => assignedCount.value >= props.job.required_volunteers)
const isEmpty = computed(() => assignedCount.value === 0)

// ── Bénévoles ──────────────────────────────────────────────────────────────────
function getVolunteer(id: string) { return volunteers.value.find(v => v.id === id) }
function getVolunteerName(id: string): string {
  const v = getVolunteer(id)
  return v ? `${v.first_name} ${v.last_name}` : id.slice(0, 8)
}
function getVolunteerInitials(id: string): string {
  const v = getVolunteer(id)
  return v ? getInitials(`${v.first_name} ${v.last_name}`) : '?'
}
function getVolunteerType(id: string): string {
  const v = getVolunteer(id)
  return v?.volunteer_type === 'Specialise' ? 'Spécialisé' : 'Normal'
}
function chipColor(id: string): string {
  const hue = id.split('').slice(0, 4).reduce((acc, c) => acc + c.charCodeAt(0), 0) % 360
  return `hsl(${hue}, 50%, 38%)`
}

// ── Catégorie & horaire ────────────────────────────────────────────────────────
const categoryColor = computed(() => getCategoryColor(props.colorIndex))
const durationHours = computed(() => props.job.slot.end_time - props.job.slot.start_time)
const { festivalDays } = useFestivalDays()

// Nom du jour depuis festivalDays — day_index correspond directement à FestivalDay.day
const dayLabel = computed(() => {
  const fd = festivalDays.value.find(d => d.day === props.job.slot.day_index)
  return fd ? fd.label : `Jour ${props.job.slot.day_index}`
})

function formatHour(h: number): string {
  return `${h > 23 ? h - 24 : h}h`
}

// ── Couleurs ───────────────────────────────────────────────────────────────────
const fillTextColor = computed(() => isEmpty.value ? 'text-red-400'  : isFull.value ? 'text-green-400' : 'text-amber-400')
const fillBarColor  = computed(() => isEmpty.value ? 'bg-red-400'    : isFull.value ? 'bg-green-400'   : 'bg-amber-400')
</script>

<style scoped>
.modal-enter-active { transition: opacity 0.2s ease; }
.modal-leave-active { transition: opacity 0.15s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }

.modal-enter-active .modal-card { transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1); }
.modal-leave-active .modal-card { transition: transform 0.15s ease; }
.modal-enter-from .modal-card   { transform: scale(0.95) translateY(8px); }
.modal-leave-to   .modal-card   { transform: scale(0.97) translateY(4px); }

.list-enter-active { transition: all 0.2s ease; }
.list-leave-active { transition: all 0.15s ease; }
.list-enter-from   { opacity: 0; transform: translateX(-8px); }
.list-leave-to     { opacity: 0; transform: translateX(8px); height: 0; margin: 0; padding: 0; }
</style>