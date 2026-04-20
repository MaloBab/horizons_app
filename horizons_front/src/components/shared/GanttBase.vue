<template>
  <div class="bg-slate-800/50 backdrop-blur-sm border border-white/10 rounded-2xl overflow-hidden w-full">
    <div class="flex w-full" style="min-width: 0">

      <!-- ═══ COLONNES FIXES GAUCHE ═══ -->
      <div
        class="sticky left-0 z-30 shrink-0 flex flex-col bg-slate-800 border-r-2 border-slate-600/80"
        :style="{ width: `${leftWidth}px` }"
      >
        <!-- En-tête colonnes fixes -->
        <div class="flex flex-col border-b-2 border-slate-600/80">
          <div class="h-10 flex items-center px-4 border-b border-white/5 bg-slate-800">
            <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              {{ leftHeaderLabel }}
            </span>
          </div>
          <!-- Slot pour sous-en-têtes supplémentaires (ex: Responsable / Poste / Type) -->
          <slot name="left-subheader" />
        </div>

        <!-- Slot pour le contenu des lignes fixes gauche -->
        <slot name="left-rows" :displayed-days="displayedDays" />
      </div>

      <!-- ═══ ZONE SCROLLABLE DROITE ═══ -->
      <div
        class="overflow-x-auto flex-1 custom-scrollbar"
        ref="scrollContainer"
        @mouseenter="isHovered = true"
        @mouseleave="isHovered = false"
      >
        <div :style="{ width: `${totalWidth}px` }">

          <!-- En-tête jours -->
          <div class="flex border-b border-white/10 bg-slate-800/80 sticky top-0 z-20">
            <template v-for="(day, dIdx) in displayedDays" :key="day.date">
              <div
                class="flex items-center justify-center h-10 shrink-0"
                :class="dIdx > 0 ? 'border-l-2 border-cyan-500/40' : ''"
                :style="{ width: `${HOURS_PER_DAY * columnWidth}px` }"
              >
                <span class="text-xs font-semibold text-white/80 truncate px-2">{{ day.label }}</span>
              </div>
            </template>
          </div>

          <!-- En-tête heures -->
          <div class="flex border-b-2 border-slate-600/80 bg-slate-800/60 sticky top-10 z-20">
            <template v-for="(day, dIdx) in displayedDays" :key="day.date">
              <div
                v-for="(hour, hIdx) in GANTT_HOURS"
                :key="`${day.date}-${hour}`"
                class="flex items-center justify-center h-8 shrink-0"
                :class="[
                  isNightHour(hour) ? 'bg-slate-900/40' : '',
                  hIdx === 0 && dIdx > 0 ? 'border-l-2 border-cyan-500/40' : 'border-r border-white/5',
                ]"
                :style="{ width: `${columnWidth}px` }"
              >
                <span class="text-[10px] font-medium text-slate-500">{{ hour }}h</span>
              </div>
            </template>
          </div>

          <!-- Slot pour les lignes de données (blocs Gantt) -->
          <slot
            name="rows"
            :displayed-days="displayedDays"
            :column-width="columnWidth"
            :row-height="rowHeight"
            :category-header-height="categoryHeaderHeight"
            :total-width="totalWidth"
            :is-night-hour="isNightHour"
            :is-job-on-day="isJobOnDay"
            :get-block-position="getBlockPosition"
            :grouped-jobs="groupedJobs"
            :grouped-by-responsible="groupedByResponsible"
          />

        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useFestivalDays } from '../../composables/useFestivalDays'
import { type JobWithRelations, GANTT_HOURS, HOURS_PER_DAY } from '../../types/planning.types'

interface Props {
  visibleDays?:          number[]
  leftHeaderLabel?:      string
  leftWidth?:            number
  columnWidth?:          number
  rowHeight?:            number
  categoryHeaderHeight?: number
}

const props = withDefaults(defineProps<Props>(), {
  leftHeaderLabel:      'Pôle / Tâche',
  leftWidth:            380,   // COL_MANAGER + COL_JOB + COL_TYPE
  columnWidth:          36,
  rowHeight:            44,
  categoryHeaderHeight: 32,
})

const { festivalDays } = useFestivalDays()

const displayedDays = computed(() =>
  props.visibleDays && props.visibleDays.length > 0
    ? festivalDays.value.filter(d => props.visibleDays!.includes(d.day))
    : festivalDays.value
)

const totalWidth = computed(() =>
  displayedDays.value.length * HOURS_PER_DAY * props.columnWidth
)

// ── Scroll horizontal via molette ─────────────────────────────────────────────

const scrollContainer = ref<HTMLElement | null>(null)
const isHovered       = ref(false)

const handleWheel = (e: WheelEvent) => {
  if (!isHovered.value || !scrollContainer.value) return
  
  const hasHorizontalScroll = scrollContainer.value.scrollWidth > scrollContainer.value.clientWidth
  
  if (hasHorizontalScroll && Math.abs(e.deltaY) > Math.abs(e.deltaX)) {
    e.preventDefault()
    scrollContainer.value.scrollLeft += e.deltaY
  }
}

onMounted(()   => window.addEventListener('wheel', handleWheel, { passive: false }))
onUnmounted(() => window.removeEventListener('wheel', handleWheel))

// ── Helpers exposés aux slots ──────────────────────────────────────────────────

function isNightHour(hour: number): boolean {
  return hour <= 6 || hour >= 22
}

function isJobOnDay(job: JobWithRelations, dIdx: number): boolean {
  return job.slot.day_index === displayedDays.value[dIdx]?.day
}

function getBlockPosition(job: JobWithRelations, dayIndex: number): Record<string, string> {
  const normalizedStart = job.slot.start_time > 23 ? job.slot.start_time - 24 : job.slot.start_time
  const hourColIndex    = GANTT_HOURS.indexOf(normalizedStart)
  const colOffset       = hourColIndex === -1 ? 0 : hourColIndex
  const left            = dayIndex * HOURS_PER_DAY * props.columnWidth + colOffset * props.columnWidth + 2
  return { left: `${left}px` }
}

function groupedJobs(jobs: JobWithRelations[]): { name: string; slots: JobWithRelations[] }[] {
  const map = new Map<string, JobWithRelations[]>()
  for (const job of jobs) {
    const key      = `${job.name}__${job.recruitment_type}`  // ← clé composite
    const existing = map.get(key)
    if (existing) existing.push(job)
    else map.set(key, [job])
  }
  return Array.from(map.entries()).map(([_key, slots]) => ({
    name: slots[0]!.name,
    slots,
  }))
}

function groupedByResponsible(
  jobs: JobWithRelations[]
): { responsible: string | null; jobs: { name: string; slots: JobWithRelations[] }[] }[] {
  const byName = groupedJobs(jobs)
  const result: { responsible: string | null; jobs: { name: string; slots: JobWithRelations[] }[] }[] = []
  for (const jobGroup of byName) {
    const responsible = jobGroup.slots[0]?.responsible ?? null
    const last = result[result.length - 1]
    if (last && last.responsible === responsible) {
      last.jobs.push(jobGroup)
    } else {
      result.push({ responsible, jobs: [jobGroup] })
    }
  }
  return result
}
</script>