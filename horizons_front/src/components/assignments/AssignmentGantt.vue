<template>
  <div class="flex flex-col gap-3" ref="ganttContainerRef">

    <!-- ── Barre de filtres ─────────────────────────────────────────────── -->
    <GanttFilters
      :filters="filters"
      :festival-days="festivalDays"
      :volunteers="volunteers"
      @update:filters="applyFilters"
      @reset="resetFilters"
    />

    <!-- ── Grille Gantt ─────────────────────────────────────────────────── -->
    <GanttBase
      :visible-days="filters.dayIndex !== null ? [filters.dayIndex] : undefined"
      left-header-label="Poste"
      :left-width="COL_LEFT_TOTAL"
      :column-width="columnWidth"
      :category-header-height="CATEGORY_HEADER_HEIGHT"
    >

      <!-- En-tête gauche -->
      <template #left-subheader>
        <div class="h-8 flex bg-slate-800/80 border-b-2 border-slate-600/80">
          <div
            class="flex items-center justify-center px-3 border-r border-white/5 shrink-0"
            :style="{ width: `${COL_JOB_WIDTH}px` }"
          >
            <span class="text-[10px] text-slate-500">Poste</span>
          </div>
          <div
            class="flex items-center justify-center px-3 shrink-0"
            :style="{ width: `${COL_FILL_WIDTH}px` }"
          >
            <span class="text-[10px] text-slate-500">Remplissage</span>
          </div>
        </div>
      </template>

      <!-- Lignes gauche (labels + remplissage) -->
      <template #left-rows>
        <template v-for="group in filteredGroups" :key="group.category.id">
          <!-- En-tête catégorie -->
          <div
            class="flex items-center gap-2 px-4 border-b border-white/5"
            :style="{ height: `${CATEGORY_HEADER_HEIGHT}px`, background: getCategoryBg(group.category.id) }"
          >
            <div
              class="w-2 h-2 rounded-full shrink-0"
              :style="{ background: getCategoryColor(group.category.id) }"
            />
            <span class="text-xs font-bold text-white/90 truncate">{{ group.category.label }}</span>
          </div>

          <!-- Lignes postes -->
          <template v-for="({ name, slots: jobSlots }) in groupedJobsFn(group.jobs)" :key="name">
            <div class="flex border-b border-white/5" :style="{ height: `${ROW_HEIGHT}px` }">
              <div
                class="flex items-center px-3 border-r border-white/5 shrink-0"
                :style="{ width: `${COL_JOB_WIDTH}px` }"
              >
                <span class="text-xs text-slate-200 truncate" :title="name">{{ name }}</span>
              </div>
              <div class="flex items-center px-3 shrink-0" :style="{ width: `${COL_FILL_WIDTH}px` }">
                <span class="text-xs font-mono font-bold" :class="fillBadgeColor(jobSlots)">
                  {{ fillBadgeText(jobSlots) }}
                </span>
              </div>
            </div>
          </template>
        </template>

        <div v-if="filteredGroups.length === 0"
          class="flex items-center justify-center h-32 text-slate-500 text-sm">
          Aucun poste à afficher
        </div>
      </template>

      <!-- Grille temporelle + blocs d'assignation -->
      <template #rows="{ displayedDays: dd, isNightHour, isJobOnDay, getBlockPosition, groupedJobs: gj }">
        <template v-for="group in filteredGroups" :key="group.category.id">

          <!-- Spacer catégorie -->
          <div class="flex border-b border-white/5" :style="{ height: `${CATEGORY_HEADER_HEIGHT}px` }">
            <template v-for="(day, dIdx) in dd" :key="day.date">
              <div
                v-for="(hour, hIdx) in GANTT_HOURS"
                :key="`spacer-${day.date}-${hour}`"
                class="shrink-0"
                :class="[
                  isNightHour(hour) ? 'bg-slate-900/20' : '',
                  hIdx === 0 && dIdx > 0 ? 'border-l-2 border-cyan-500/40' : 'border-r border-white/3',
                ]"
                :style="{
                  width: `${columnWidth}px`,
                  height: `${CATEGORY_HEADER_HEIGHT}px`,
                  background: getCategoryBg(group.category.id),
                }"
              />
            </template>
          </div>

          <!-- Lignes postes avec blocs -->
          <template v-for="({ name, slots: jobSlots }) in gj(group.jobs)" :key="name">
            <div
              class="relative flex border-b border-white/5 hover:bg-white/2 transition-colors"
              :style="{ height: `${ROW_HEIGHT}px` }"
            >
              <!-- Cellules de grille -->
              <template v-for="(day, dIdx) in dd" :key="day.date">
                <div
                  v-for="(hour, hIdx) in GANTT_HOURS"
                  :key="`cell-${day.date}-${hour}`"
                  class="shrink-0"
                  :class="[
                    isNightHour(hour) ? 'bg-slate-900/20' : '',
                    hIdx === 0 && dIdx > 0 ? 'border-l-2 border-cyan-500/40' : 'border-r border-white/3',
                  ]"
                  :style="{ width: `${columnWidth}px`, height: `${ROW_HEIGHT}px` }"
                />
              </template>

              <!-- Blocs d'assignation -->
              <template v-for="job in jobSlots" :key="job.id">
                <template v-for="(day, dIdx) in dd" :key="`block-${day.date}-${job.id}`">
                  <div
                    v-if="isJobOnDay(job, dIdx)"
                    class="absolute top-1/2 -translate-y-1/2 z-10"
                    :style="getBlockPosition(job, dIdx)"
                  >
                    <AssignmentGanttBlock
                      :job="job"
                      :column-width="columnWidth"
                      :row-height="ROW_HEIGHT"
                      :color-index="group.category.id"
                      :highlight-volunteer-id="filters.volunteerId || undefined"
                      @assign="handleAssign"
                      @unassign="handleUnassign"
                      @open-volunteer="$emit('open-volunteer', $event)"
                      @drag-chip-start="onChipDragStart"
                      @drag-chip-end="onChipDragEnd"
                    />
                  </div>
                </template>
              </template>
            </div>
          </template>
        </template>
      </template>
    </GanttBase>

    <DragGhostCard />

    <Toast
      v-if="toast.show"
      :show="toast.show"
      :message="toast.message"
      :type="toast.type"
      @close="hideToast"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useAssignmentStore } from '../../stores/useAssignmentStore'
import { useFestivalDays } from '../../composables/useFestivalDays'
import { useBenevoles } from '../../composables/useBenevoles'
import { useDragState } from '../../composables/useDragState'
import { getCategoryColor, getCategoryBg } from '../../utils/CategoryColor'
import { GANTT_HOURS } from '../../types/planning.types'

import GanttBase            from '../shared/GanttBase.vue'
import GanttFilters         from './GanttFilters.vue'
import AssignmentGanttBlock from './AssignmentGanttBlock.vue'
import DragGhostCard        from './DragGhostCard.vue'
import Toast                from '../shared/Toast.vue'

import { useGanttFilters }      from '../../composables/Assignment/useGanttFilters'
import { useGanttLayout }       from '../../composables/Assignment/useGanttLayout'
import { useAssignmentActions } from '../../composables/Assignment/useAssignmentActions'

// ── Constantes de mise en page ────────────────────────────────────────────────

const CATEGORY_HEADER_HEIGHT = 36
const ROW_HEIGHT             = 52
const COL_JOB_WIDTH          = 130
const COL_FILL_WIDTH         = 80
const COL_LEFT_TOTAL         = COL_JOB_WIDTH + COL_FILL_WIDTH

// ── Emits ─────────────────────────────────────────────────────────────────────

defineEmits<{ 'open-volunteer': [volunteerId: string] }>()
defineExpose({ setVolunteerFilter })

// ── Store & données ───────────────────────────────────────────────────────────

const store = useAssignmentStore()
const { jobs, assignmentsByJob, assignmentsByVolunteer } = storeToRefs(store)
const { festivalDays } = useFestivalDays()
const { volunteers }   = useBenevoles()
useDragState()

// ── Filtres + groupes filtrés ─────────────────────────────────────────────────

const {
  filters,
  filteredGroups,
  resetFilters,
  applyFilters,
  groupedJobsFn,
  fillBadgeText,
  fillBadgeColor,
} = useGanttFilters(jobs, assignmentsByJob, assignmentsByVolunteer)

// ── Layout (largeur colonnes + ResizeObserver) ────────────────────────────────

const ganttContainerRef = ref<HTMLElement | null>(null)

const visibleDayCount = computed(() =>
  filters.dayIndex !== null ? 1 : festivalDays.value.length
)

const { columnWidth } = useGanttLayout(ganttContainerRef, visibleDayCount, COL_LEFT_TOTAL)

function setVolunteerFilter(volunteerId: string) {
  applyFilters({ ...filters, volunteerId })
}

// ── Actions d'assignation ─────────────────────────────────────────────────────

const {
  toast,
  hideToast,
  onChipDragStart,
  onChipDragEnd,
  handleAssign,
  handleUnassign,
} = useAssignmentActions(jobs)
</script>