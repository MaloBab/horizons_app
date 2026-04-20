import { reactive, computed } from 'vue'
import type { Ref } from 'vue'
import type { JobWithRelations, Category } from '../../types/planning.types'
import type { GanttFilters } from '../../components/assignments/GanttFilters.vue'

/**
 * Gère l'état des filtres et le calcul des groupes filtrés.
 * Séparé du composant pour être réutilisable et testable.
 */
export function useGanttFilters(
  jobs: Ref<JobWithRelations[]>,
  assignmentsByJob: Ref<Map<number, { job_id: number }[]>>,
  assignmentsByVolunteer: Ref<Map<string, { job_id: number }[]>>,
) {
  // ── État des filtres ──────────────────────────────────────────────────────

  const filters = reactive<GanttFilters>({
    search:      '',
    fillStatus:  '',
    dayIndex:    null,
    volunteerId: '',
  })

  function resetFilters() {
    filters.search      = ''
    filters.fillStatus  = ''
    filters.dayIndex    = null
    filters.volunteerId = ''
  }

  function applyFilters(newFilters: GanttFilters) {
    Object.assign(filters, newFilters)
  }

  const hasActiveFilters = computed(() =>
    filters.search      !== '' ||
    filters.fillStatus  !== '' ||
    filters.dayIndex    !== null ||
    filters.volunteerId !== ''
  )

  // ── Helpers de remplissage ────────────────────────────────────────────────

  function getFillStatus(job: JobWithRelations): 'empty' | 'partial' | 'full' {
    const count = assignmentsByJob.value.get(job.id)?.length ?? 0
    if (count === 0) return 'empty'
    if (count >= job.required_volunteers) return 'full'
    return 'partial'
  }

  function groupFillCount(slots: JobWithRelations[]): number {
    return slots.reduce((sum, job) => sum + (assignmentsByJob.value.get(job.id)?.length ?? 0), 0)
  }

  function groupFillRequired(slots: JobWithRelations[]): number {
    return slots.reduce((sum, job) => sum + job.required_volunteers, 0)
  }

  function fillBadgeText(slots: JobWithRelations[]): string {
    return `${groupFillCount(slots)}/${groupFillRequired(slots)}`
  }

  function fillBadgeColor(slots: JobWithRelations[]): string {
    const count    = groupFillCount(slots)
    const required = groupFillRequired(slots)
    if (count === 0)       return 'text-red-400'
    if (count >= required) return 'text-green-400'
    return 'text-amber-400'
  }

  // ── Groupes filtrés ───────────────────────────────────────────────────────

  const filteredGroups = computed(() => {
    const normalJobs = jobs.value.filter(j => j.recruitment_type === 'Normal')
    const categoryMap = new Map<number, { category: Category; jobs: JobWithRelations[] }>()

    for (const job of normalJobs) {
      if (filters.search && !job.name.toLowerCase().includes(filters.search.toLowerCase())) continue
      if (filters.fillStatus && getFillStatus(job) !== filters.fillStatus) continue
      if (filters.dayIndex !== null && job.slot.day_index !== filters.dayIndex) continue

      if (filters.volunteerId) {
        const volunteerJobs = assignmentsByVolunteer.value.get(filters.volunteerId) ?? []
        const isAssigned = volunteerJobs.some(a => a.job_id === job.id)
        if (!isAssigned) continue
      }

      const existing = categoryMap.get(job.category_id)
      if (existing) existing.jobs.push(job)
      else categoryMap.set(job.category_id, { category: job.category, jobs: [job] })
    }

    return [...categoryMap.values()]
  })

  // ── Groupement par nom de poste ───────────────────────────────────────────

  function groupedJobsFn(jobs: JobWithRelations[]) {
    const map = new Map<string, { name: string; slots: JobWithRelations[] }>()
    for (const job of jobs) {
      const ex = map.get(job.name)
      if (ex) ex.slots.push(job)
      else map.set(job.name, { name: job.name, slots: [job] })
    }
    return [...map.values()]
  }

  return {
    filters,
    hasActiveFilters,
    filteredGroups,
    resetFilters,
    applyFilters,
    groupedJobsFn,
    fillBadgeText,
    fillBadgeColor,
  }
}