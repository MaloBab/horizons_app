<template>
  <div ref="containerRef" class="flex flex-col gap-3">

    <GanttBase
      :visible-days="visibleDays"
      left-header-label="Pôle / Tâche"
      :left-width="COL_MANAGER_WIDTH + COL_JOB_WIDTH + COL_TYPE_WIDTH"
      :column-width="COLUMN_WIDTH"
      :row-height="ROW_HEIGHT"
      :category-header-height="CATEGORY_HEADER_HEIGHT"
    >

      <!-- ── Sous-en-tête colonnes fixes ── -->
      <template #left-subheader>
        <div class="h-8 flex bg-slate-800/80">
          <div
            class="flex items-center justify-center px-3 border-r border-white/5 shrink-0"
            :style="{ width: `${COL_MANAGER_WIDTH}px` }"
          >
            <span class="text-[10px] text-slate-500 truncate">Responsable(s)</span>
          </div>
          <div
            class="flex items-center justify-center px-3 border-r border-white/5 shrink-0"
            :style="{ width: `${COL_JOB_WIDTH}px` }"
          >
            <span class="text-[10px] text-slate-500 truncate">Poste</span>
          </div>
          <div
            class="flex items-center justify-center px-3 shrink-0"
            :style="{ width: `${COL_TYPE_WIDTH}px` }"
          >
            <span class="text-[10px] text-slate-500 truncate">Recrutement</span>
          </div>
        </div>
      </template>

      <!-- ── Lignes fixes gauche ── -->
      <template #left-rows>
        <div>
          <template v-for="group in categoryGroups" :key="group.category.id">

            <!-- Header catégorie -->
            <div
              class="flex items-center gap-2 px-4 border-b border-white/5"
              :style="{ height: `${CATEGORY_HEADER_HEIGHT}px`, background: getCategoryBg(group.category.id) }"
            >
              <div class="w-2 h-2 rounded-full shrink-0" :style="{ background: getCategoryColor(group.category.id) }" />
              <span class="text-xs font-bold text-white/90 truncate">{{ group.category.label }}</span>
            </div>

            <!-- Lignes jobs groupées par responsable -->
            <template v-for="(responsableGroup, rgIdx) in groupedByResponsible(group.jobs)" :key="`rg-${rgIdx}`">
              <div
                class="relative flex"
                :class="rgIdx > 0 ? 'border-t border-white/8' : ''"
              >
                <!-- Colonne responsable -->
                <div
                  class="relative border-r border-white/5 shrink-0 border-b"
                  :style="{ width: `${COL_MANAGER_WIDTH}px`, height: `${responsableGroup.jobs.length * ROW_HEIGHT}px` }"
                >
                  <div class="absolute inset-0 flex items-center px-3">
                    <span
                      v-if="responsableGroup.responsible"
                      class="text-[10px] text-slate-300 leading-tight whitespace-pre-line"
                    >
                      {{ responsableGroup.responsible.replace(/,\s*/g, '\n') }}
                    </span>
                    <span v-else class="text-[10px] text-slate-600">—</span>
                  </div>
                </div>

                <!-- Colonne poste + recrutement -->
                <div class="flex flex-col flex-1">
                  <template v-for="({ name, slots }) in responsableGroup.jobs" :key="name">
                    <div class="flex" :style="{ height: `${ROW_HEIGHT}px` }">
                      <div
                        class="flex items-center px-3 border-r border-b border-white/5 hover:bg-white/3 transition-colors shrink-0"
                        :style="{ width: `${COL_JOB_WIDTH}px` }"
                      >
                        <span class="text-xs text-slate-200 truncate" :title="name">{{ name }}</span>
                      </div>
                      <div
                        class="flex items-center px-3 border-b border-white/5 hover:bg-white/3 transition-colors shrink-0"
                        :style="{ width: `${COL_TYPE_WIDTH}px` }"
                      >
                        <span
                          class="px-2 py-0.5 rounded-full text-[10px] font-medium border leading-tight"
                          :class="slots[0]?.recruitment_type === 'Specialise'
                            ? 'bg-amber-500/20 text-amber-300 border-amber-500/30'
                            : 'bg-slate-600/50 text-slate-400 border-white/10'"
                        >
                          {{ slots[0]?.recruitment_type === 'Specialise' ? '⭐ Spécialisé' : 'Normal' }}
                        </span>
                      </div>
                    </div>
                  </template>
                </div>

              </div>
            </template>

          </template>

          <div
            v-if="categoryGroups.length === 0"
            class="flex items-center justify-center h-32 text-slate-500 text-sm"
          >
            Aucun poste à afficher
          </div>
        </div>
      </template>

      <!-- ── Lignes Gantt droite ── -->
      <template #rows="{ displayedDays, isNightHour, isJobOnDay, getBlockPosition, groupedJobs }">
        <template v-for="group in categoryGroups" :key="group.category.id">

          <!-- Spacer catégorie -->
          <div
            class="flex border-b border-white/5"
            :style="{ height: `${CATEGORY_HEADER_HEIGHT}px` }"
          >
            <template v-for="(day, dIdx) in displayedDays" :key="day.date">
              <div
                v-for="(hour, hIdx) in GANTT_HOURS"
                :key="`spacer-${day.date}-${hour}`"
                class="shrink-0"
                :class="[
                  isNightHour(hour) ? 'bg-slate-900/20' : '',
                  hIdx === 0 && dIdx > 0 ? 'border-l-2 border-cyan-500/40' : 'border-r border-white/3'
                ]"
                :style="{
                  width: `${COLUMN_WIDTH}px`,
                  height: `${CATEGORY_HEADER_HEIGHT}px`,
                  background: getCategoryBg(group.category.id)
                }"
              />
            </template>
          </div>

          <!-- Lignes jobs -->
          <template v-for="({ name, slots }) in groupedJobs(group.jobs)" :key="name">
            <div
              class="relative flex border-b border-white/5 hover:bg-white/2 transition-colors"
              :style="{ height: `${ROW_HEIGHT}px` }"
            >
              <!-- Fond grille -->
              <template v-for="(day, dIdx) in displayedDays" :key="day.date">
                <div
                  v-for="(hour, hIdx) in GANTT_HOURS"
                  :key="`cell-${day.date}-${hour}`"
                  class="shrink-0"
                  :class="[
                    isNightHour(hour) ? 'bg-slate-900/20' : '',
                    hIdx === 0 && dIdx > 0 ? 'border-l-2 border-cyan-500/40' : 'border-r border-white/3'
                  ]"
                  :style="{ width: `${COLUMN_WIDTH}px`, height: `${ROW_HEIGHT}px` }"
                />
              </template>

              <!-- Blocs -->
              <template v-for="job in slots" :key="job.id">
                <template v-for="(day, dIdx) in displayedDays" :key="`block-${day.date}-${job.id}`">
                  <div
                    v-if="isJobOnDay(job, dIdx)"
                    class="absolute top-1/2 -translate-y-1/2 z-10"
                    :style="getBlockPosition(job, dIdx)"
                  >
                    <GanttSlotBlock
                      :job="job"
                      :slot="job.slot"
                      :column-width="COLUMN_WIDTH"
                      :recruitment-type="job.recruitment_type"
                      :category-id="group.category.id" 
                      @click="openDetail(job)"
                    />
                  </div>
                </template>
              </template>

            </div>
          </template>

        </template>
      </template>
    </GanttBase>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import GanttBase from '../shared/GanttBase.vue'
import GanttSlotBlock from './GanttSlotBlock.vue'
import { type CategoryGroup, type JobWithRelations, GANTT_HOURS, HOURS_PER_DAY } from '../../types/planning.types'
import { getCategoryColor, getCategoryBg } from '../../utils/CategoryColor'

interface Props {
  categoryGroups: CategoryGroup[]
  visibleDays?:   number[]
}

const props = defineProps<Props>()

const ROW_HEIGHT             = 44
const CATEGORY_HEADER_HEIGHT = 32
const COL_MANAGER_WIDTH      = 110
const COL_JOB_WIDTH          = 170
const COL_TYPE_WIDTH         = 100
const LEFT_WIDTH             = COL_MANAGER_WIDTH + COL_JOB_WIDTH + COL_TYPE_WIDTH
const MIN_COLUMN_WIDTH       = 36
const BASE_COLUMN_WIDTH      = 36

// ── Calcul dynamique de la largeur des colonnes ───────────────────────────────

const containerWidth = ref(0)
const containerRef   = ref<HTMLElement | null>(null)

const visibleDayCount = computed(() =>
  props.visibleDays && props.visibleDays.length > 0 ? props.visibleDays.length : 1
)

const COLUMN_WIDTH = computed(() => {
  if (!containerWidth.value) return BASE_COLUMN_WIDTH
  const available   = containerWidth.value - LEFT_WIDTH
  const totalCols   = visibleDayCount.value * HOURS_PER_DAY
  const computed    = Math.floor(available / totalCols)
  return Math.max(computed, MIN_COLUMN_WIDTH)
})

let resizeObserver: ResizeObserver | null = null

onMounted(() => {
  // On observe le parent direct pour récupérer la largeur disponible
  const el = containerRef.value?.closest('.flex-col') as HTMLElement | null
    ?? containerRef.value?.parentElement
  if (!el) return
  resizeObserver = new ResizeObserver(entries => {
    containerWidth.value = entries[0]?.contentRect.width ?? 0
  })
  resizeObserver.observe(el)
  containerWidth.value = el.getBoundingClientRect().width
})

onUnmounted(() => resizeObserver?.disconnect())

// ─────────────────────────────────────────────────────────────────────────────

const selectedJob = ref<JobWithRelations | null>(null)
const openDetail = (job: JobWithRelations) => { selectedJob.value = job }

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