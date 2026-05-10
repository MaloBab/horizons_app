import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useBenevoles } from '../composables/useBenevoles'
import { fetchCategoryGroups } from '../composables/useJob'
import type { JobWithRelations } from '../types/planning.types'
import type { Volunteer } from '../types/benevole.types'
import type {
  Assignment,
  AssignmentResponse,
  AssignmentKey,
  HistoryCommand,
  VolunteerMetrics,
  GlobalMetrics,
  SaveState,
} from '../types/assignment.types'
import {
  makeAssignmentKey,
  DAILY_HOUR_LIMITS,
  SATISFACTION_WEIGHTS,
  SCHEDULE_SUBWEIGHTS,
  NIGHT_HOUR_START,
  CONSECUTIVE_NIGHT_THRESHOLD,
} from '../types/assignment.types'
import { apiFetch } from '../api'

// ─────────────────────────────────────────────────────────────────────────────
// Notation des heures
//
// Une journée va de 8h à 6h du matin (30h en notation décalée).
// Les heures sont des entiers LINÉAIRES : 8, 9, ..., 23, 24, 25, ..., 30
//   24 = minuit, 25 = 1h, 26 = 2h, 27 = 3h, 28 = 4h, 29 = 5h, 30 = 6h
//
// JAMAIS de modulo — la boucle est toujours for (h = start; h < end; h++).
// ─────────────────────────────────────────────────────────────────────────────

const algorithmPhase    = ref<'idle' | 'running' | 'success' | 'error'>('idle')
const algorithmProgress = ref(0)
const algorithmMessage  = ref('')
const algorithmLog      = ref<string[]>([])

const algorithmStats = ref<{
  generation:   string
  satisfaction: string
  postes:       string
  benevoles:    string
} | null>(null)

const algorithmAlert = ref('')

/**
 * Retourne la liste des heures décalées couvertes par un créneau.
 * Ex: start=9,  end=12  → [9, 10, 11]
 *     start=23, end=28  → [23, 24, 25, 26, 27]
 */
function hoursInSlot(start_time: number, end_time: number): number[] {
  const hours: number[] = []
  for (let h = start_time; h < end_time; h++) hours.push(h)
  return hours
}

// ─────────────────────────────────────────────────────────────────────────────
// Mapping réseau → frontend
// ─────────────────────────────────────────────────────────────────────────────

function mapAssignment(raw: AssignmentResponse): Assignment {
  const volunteer_id = raw.volunteer.id
  const job_id       = raw.job_id
  return { volunteer_id, job_id, key: makeAssignmentKey(volunteer_id, job_id) }
}

// ─────────────────────────────────────────────────────────────────────────────
// Calcul des métriques par bénévole
// ─────────────────────────────────────────────────────────────────────────────

function computeVolunteerMetrics(
  volunteer:      Volunteer,
  allAssignments: Assignment[],
  allJobs:        JobWithRelations[],
): VolunteerMetrics {
  const myAssignments = allAssignments.filter(a => a.volunteer_id === volunteer.id)

  // ── Heures par jour ────────────────────────────────────────────────────────
  const hours_per_day: Record<number, number> = {}
  for (const a of myAssignments) {
    const job = allJobs.find(j => j.id === a.job_id)
    if (!job) continue
    const duration = job.slot.end_time - job.slot.start_time
    hours_per_day[job.slot.day_index] = (hours_per_day[job.slot.day_index] ?? 0) + duration
  }

  const total_hours          = Object.values(hours_per_day).reduce((s, h) => s + h, 0)
  const limit                = DAILY_HOUR_LIMITS[volunteer.volunteer_type as keyof typeof DAILY_HOUR_LIMITS] ?? 6
  const daily_limit_exceeded = Object.values(hours_per_day).some(h => h > limit)

  // ── Créneaux avec/sans compagnon ───────────────────────────────────────────
  const mateIds = new Set(volunteer.mates.map(m => m.id))
  let slots_with_mate    = 0
  let slots_without_mate = 0
  for (const a of myAssignments) {
    const coWorkers = allAssignments.filter(x => x.job_id === a.job_id && x.volunteer_id !== volunteer.id)
    coWorkers.some(x => mateIds.has(x.volunteer_id)) ? slots_with_mate++ : slots_without_mate++
  }

  // ── Score de satisfaction ──────────────────────────────────────────────────
  const satisfaction_score = myAssignments.length === 0
    ? null
    : computeSatisfactionScore(volunteer, myAssignments, allJobs, allAssignments, hours_per_day)

  return {
    volunteer_id: volunteer.id,
    total_hours,
    hours_per_day,
    daily_limit_exceeded,
    slots_with_mate,
    slots_without_mate,
    satisfaction_score,
    assignment_count: myAssignments.length,
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Calcul de la chaîne de postes nocturnes consécutifs
// ─────────────────────────────────────────────────────────────────────────────

interface NightJobInterval {
  start: number
  end:   number
}

function longestConsecutiveNightJobChain(intervals: NightJobInterval[]): number {
  if (intervals.length === 0) return 0

  const nightJobs = intervals.filter(iv => iv.end > NIGHT_HOUR_START)
  if (nightJobs.length === 0) return 0

  nightJobs.sort((a, b) => a.start - b.start)

  let maxChain = 1
  let curChain = 1

  for (let i = 1; i < nightJobs.length; i++) {
    const prev = nightJobs[i - 1]!
    const curr = nightJobs[i]!
    if (curr.start === prev.end) {
      curChain++
      if (curChain > maxChain) maxChain = curChain
    } else {
      curChain = 1
    }
  }

  return maxChain
}

function computeSatisfactionScore(
  volunteer:      Volunteer,
  myAssignments:  Assignment[],
  allJobs:        JobWithRelations[],
  allAssignments: Assignment[],
  hours_per_day:  Record<number, number>,
): number {
  const hasMates = volunteer.mates.length > 0
  const hasPrefs = volunteer.preferences.length > 0
  const mateIds  = new Set(volunteer.mates.map(m => m.id))
  const nbPrefs  = volunteer.preferences.length
  const limit    = DAILY_HOUR_LIMITS[volunteer.volunteer_type as keyof typeof DAILY_HOUR_LIMITS] ?? 6

  // ── Poids actifs, renormalisés selon les critères applicables ─────────────
  const rawWeights = {
    mates:       hasMates ? SATISFACTION_WEIGHTS.MATES       : 0,
    schedule:                SATISFACTION_WEIGHTS.SCHEDULE,
    preferences: hasPrefs ? SATISFACTION_WEIGHTS.PREFERENCES : 0,
  }
  const weightSum = rawWeights.mates + rawWeights.schedule + rawWeights.preferences
  const w = {
    mates:       rawWeights.mates       / weightSum,
    schedule:    rawWeights.schedule    / weightSum,
    preferences: rawWeights.preferences / weightSum,
  }

  // ── Score D : calculé une fois par jour ───────────────────────────────────
  const nightJobsPerDay: Record<number, NightJobInterval[]> = {}
  for (const assignment of myAssignments) {
    const job = allJobs.find(j => j.id === assignment.job_id)
    if (!job) continue
    if (job.slot.end_time <= NIGHT_HOUR_START) continue
    const day = job.slot.day_index
    if (!nightJobsPerDay[day]) nightJobsPerDay[day] = []
    nightJobsPerDay[day].push({ start: job.slot.start_time, end: job.slot.end_time })
  }

  const d_score_per_day: Record<number, number> = {}
  for (const [dayStr, totalHours] of Object.entries(hours_per_day)) {
    const day      = Number(dayStr)
    const chain    = longestConsecutiveNightJobChain(nightJobsPerDay[day] ?? [])

    const d_nuit = chain < CONSECUTIVE_NIGHT_THRESHOLD
      ? 1
      : Math.max(0, 1 - (chain - CONSECUTIVE_NIGHT_THRESHOLD + 1) / CONSECUTIVE_NIGHT_THRESHOLD)

    const excess = Math.max(0, totalHours - limit)
    const d_charge = 1 - Math.min(excess / limit, 1)

    d_score_per_day[day] = SCHEDULE_SUBWEIGHTS.NIGHT_PENALTY * d_nuit
                         + SCHEDULE_SUBWEIGHTS.DAILY_LOAD    * d_charge
  }

  // ── Score par poste ───────────────────────────────────────────────────────
  let scoreSum = 0

  for (const assignment of myAssignments) {
    const job = allJobs.find(j => j.id === assignment.job_id)
    if (!job) continue

    const score_c = hasMates
      ? (allAssignments.some(x =>
          x.job_id       === job.id &&
          x.volunteer_id !== volunteer.id &&
          mateIds.has(x.volunteer_id)
        ) ? 1 : 0)
      : 0

    const score_d = d_score_per_day[job.slot.day_index] ?? 1

    const score_b = hasPrefs
      ? (() => {
          const pref = volunteer.preferences.find(p =>
            p.preference.id === job.category.preference_id
          )
          return pref ? (nbPrefs - pref.rank + 1) / nbPrefs : 0
        })()
      : 0

    scoreSum += w.mates * score_c + w.schedule * score_d + w.preferences * score_b
  }

  return scoreSum / myAssignments.length
}

// ─────────────────────────────────────────────────────────────────────────────
// Store
// ─────────────────────────────────────────────────────────────────────────────

export const useAssignmentStore = defineStore('assignment', () => {

  const { volunteers, fetchVolunteers } = useBenevoles()

  // ── État ───────────────────────────────────────────────────────────────────

  const assignmentsMap = ref<Map<AssignmentKey, Assignment>>(new Map())
  const isLoading      = ref(false)
  const error          = ref<string | null>(null)
  const saveState      = ref<SaveState>('saved')
  const jobs           = ref<JobWithRelations[]>([])

  const _consumedSlotKeys = ref<Set<string>>(new Set())

  // ── Historique Undo/Redo ───────────────────────────────────────────────────
  const history      = ref<HistoryCommand[]>([])
  const historyIndex = ref(-1)

  // ── Computed ───────────────────────────────────────────────────────────────

  const assignments = computed<Assignment[]>(() => [...assignmentsMap.value.values()])

  const assignmentsByJob = computed<Map<number, Assignment[]>>(() => {
    const map = new Map<number, Assignment[]>()
    for (const a of assignmentsMap.value.values()) {
      const list = map.get(a.job_id) ?? []; list.push(a); map.set(a.job_id, list)
    }
    return map
  })

  const assignmentsByVolunteer = computed<Map<string, Assignment[]>>(() => {
    const map = new Map<string, Assignment[]>()
    for (const a of assignmentsMap.value.values()) {
      const list = map.get(a.volunteer_id) ?? []; list.push(a); map.set(a.volunteer_id, list)
    }
    return map
  })

  const metricsMap = computed<Map<string, VolunteerMetrics>>(() => {
    const map  = new Map<string, VolunteerMetrics>()
    const allA = [...assignmentsMap.value.values()]
    for (const v of volunteers.value) {
      map.set(v.id, computeVolunteerMetrics(v, allA, jobs.value))
    }
    return map
  })

  const globalMetrics = computed<GlobalMetrics>(() => {
    const normalJobs          = jobs.value.filter(j => j.recruitment_type === 'Normal')
    const jobs_total          = normalJobs.length
    const jobs_filled         = normalJobs.filter(j => (assignmentsByJob.value.get(j.id)?.length ?? 0) >= j.required_volunteers).length
    const volunteers_total    = volunteers.value.length
    const volunteers_assigned = volunteers.value.filter(v => (assignmentsByVolunteer.value.get(v.id)?.length ?? 0) > 0).length

    const metrics = [...metricsMap.value.values()]

    const scoredMetrics    = metrics.filter(m => m.satisfaction_score !== null)
    const avg_satisfaction = scoredMetrics.length > 0
      ? scoredMetrics.reduce((s, m) => s + (m.satisfaction_score ?? 0), 0) / scoredMetrics.length
      : 0

    const hoursAcc: Record<number, number> = {}
    for (const m of metrics) {
      for (const [day, h] of Object.entries(m.hours_per_day)) {
        hoursAcc[Number(day)] = (hoursAcc[Number(day)] ?? 0) + h
      }
    }
    const dayVals           = Object.values(hoursAcc)
    const avg_hours_per_day = dayVals.length > 0 && volunteers_total > 0
      ? dayVals.reduce((s, h) => s + h, 0) / dayVals.length / volunteers_total
      : 0

    return { jobs_filled, jobs_total, volunteers_assigned, volunteers_total, avg_satisfaction, avg_hours_per_day }
  })

  const canUndo         = computed(() => historyIndex.value >= 0)
  const canRedo         = computed(() => historyIndex.value < history.value.length - 1)
  const historyPosition = computed(() => ({ current: historyIndex.value + 1, total: history.value.length }))

  // ── Chargement ─────────────────────────────────────────────────────────────

  async function fetchAll(): Promise<void> {
    isLoading.value = true
    error.value     = null
    try {
      await Promise.all([fetchVolunteers(), _fetchJobs()])
      await _fetchAssignments()
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Erreur inconnue'
    } finally {
      isLoading.value = false
    }
  }

  async function _fetchJobs(): Promise<void> {
    const groups = await fetchCategoryGroups()
    jobs.value   = groups.flatMap(g => g.jobs)
  }

  async function _fetchAssignments(): Promise<void> {
    const res = await apiFetch(`/assignments/`)
    if (!res.ok) throw new Error(`Erreur ${res.status} lors du chargement des affectations`)

    const raw: AssignmentResponse[] = await res.json()
    const map      = new Map<AssignmentKey, Assignment>()
    const consumed = new Set<string>()

    for (const item of raw) {
      const a = mapAssignment(item)
      map.set(a.key, a)
      const job = jobs.value.find(j => j.id === a.job_id)
      if (job) {
        for (const h of hoursInSlot(job.slot.start_time, job.slot.end_time)) {
          consumed.add(`${a.volunteer_id}__${job.slot.day_index}__${h}`)
        }
      }
    }

    assignmentsMap.value    = map
    _consumedSlotKeys.value = consumed
  }

  // ── Gestion des slots consommés (mémoire uniquement) ──────────────────────

  function _consumeSlots(volunteerId: string, job: JobWithRelations): void {
    const { day_index, start_time, end_time } = job.slot
    const next = new Set(_consumedSlotKeys.value)
    for (const h of hoursInSlot(start_time, end_time)) {
      next.add(`${volunteerId}__${day_index}__${h}`)
    }
    _consumedSlotKeys.value = next
  }

  function _releaseSlots(volunteerId: string, job: JobWithRelations): void {
    const { day_index, start_time, end_time } = job.slot
    const next = new Set(_consumedSlotKeys.value)
    for (const h of hoursInSlot(start_time, end_time)) {
      next.delete(`${volunteerId}__${day_index}__${h}`)
    }
    _consumedSlotKeys.value = next
  }

  // ── Mutations locales (optimistic update) ──────────────────────────────────

  function _applyAssign(a: Assignment): void {
    assignmentsMap.value = new Map(assignmentsMap.value).set(a.key, a)
    const job = jobs.value.find(j => j.id === a.job_id)
    if (job) _consumeSlots(a.volunteer_id, job)
    saveState.value = 'unsaved'
  }

  function _applyUnassign(a: Assignment): void {
    const map = new Map(assignmentsMap.value)
    map.delete(a.key)
    assignmentsMap.value = map
    const job = jobs.value.find(j => j.id === a.job_id)
    if (job) _releaseSlots(a.volunteer_id, job)
    saveState.value = 'unsaved'
  }

  // ── Historique ─────────────────────────────────────────────────────────────

  function _pushHistory(cmd: HistoryCommand): void {
    history.value = history.value.slice(0, historyIndex.value + 1)
    history.value.push(cmd)
    historyIndex.value = history.value.length - 1
  }

  // ── Actions publiques ──────────────────────────────────────────────────────

  function assign(volunteerId: string, jobId: number): void {
    const key = makeAssignmentKey(volunteerId, jobId)
    if (assignmentsMap.value.has(key)) return
    const assignment: Assignment = { volunteer_id: volunteerId, job_id: jobId, key }
    _applyAssign(assignment)
    _pushHistory({ type: 'assign', assignment })
  }

  function unassign(volunteerId: string, jobId: number): void {
    const key        = makeAssignmentKey(volunteerId, jobId)
    const assignment = assignmentsMap.value.get(key)
    if (!assignment) return
    _applyUnassign(assignment)
    _pushHistory({ type: 'unassign', assignment })
  }

  function reassign(volunteerId: string, fromJobId: number, toJobId: number): void {
    const fromKey = makeAssignmentKey(volunteerId, fromJobId)
    const from    = assignmentsMap.value.get(fromKey)
    if (!from) return
    const toKey = makeAssignmentKey(volunteerId, toJobId)
    if (assignmentsMap.value.has(toKey)) return
    const to: Assignment = { volunteer_id: volunteerId, job_id: toJobId, key: toKey }
    _applyUnassign(from)
    _applyAssign(to)
    _pushHistory({ type: 'reassign', from, to })
  }

  async function clearAll(): Promise<boolean> {
    isLoading.value = true
    error.value     = null
    try {
      const res = await apiFetch(`/assignments/`, { method: 'DELETE' })
      if (!res.ok) throw new Error(`Erreur ${res.status}`)
      assignmentsMap.value    = new Map()
      _consumedSlotKeys.value = new Set()
      history.value           = []
      historyIndex.value      = -1
      saveState.value         = 'saved'
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Erreur lors de la suppression'
      return false
    } finally {
      isLoading.value = false
    }
  }

  // ── Undo / Redo ────────────────────────────────────────────────────────────

  function undo(): void {
    if (!canUndo.value) return
    const cmd = history.value[historyIndex.value]!
    historyIndex.value--
    switch (cmd.type) {
      case 'assign':   _applyUnassign(cmd.assignment);                  break
      case 'unassign': _applyAssign(cmd.assignment);                    break
      case 'reassign': _applyUnassign(cmd.to); _applyAssign(cmd.from);  break
    }
  }

  function redo(): void {
    if (!canRedo.value) return
    historyIndex.value++
    const cmd = history.value[historyIndex.value]!
    switch (cmd.type) {
      case 'assign':   _applyAssign(cmd.assignment);                    break
      case 'unassign': _applyUnassign(cmd.assignment);                  break
      case 'reassign': _applyUnassign(cmd.from); _applyAssign(cmd.to);  break
    }
  }

  // ── Persistance ────────────────────────────────────────────────────────────

  async function save(): Promise<boolean> {
    saveState.value = 'saving'
    try {
      const res = await apiFetch(`/assignments/bulk`, {
        method: 'PUT',
        body:   JSON.stringify({
          assignments: assignments.value.map(a => ({
            volunteer_id: a.volunteer_id,
            job_id:       a.job_id,
          })),
        }),
      })
      if (!res.ok) throw new Error(`Erreur ${res.status} lors de la sauvegarde des affectations`)
      saveState.value = 'saved'
      return true
    } catch (err) {
      saveState.value = 'error'
      error.value     = err instanceof Error ? err.message : 'Erreur lors de la sauvegarde'
      return false
    }
  }

  const POLL_INTERVAL_MS = 4_000

  async function runAlgorithm(): Promise<boolean> {
    algorithmPhase.value    = 'running'
    algorithmProgress.value = 0
    algorithmMessage.value  = 'Initialisation…'
    algorithmLog.value      = []
    algorithmStats.value    = null
    algorithmAlert.value    = ''
    isLoading.value         = true
    error.value             = null

    // 1. Lancer la tâche — répond immédiatement avec un task_id
    let taskId: string
    try {
      const launchRes = await apiFetch('/assignments/run-algorithm', { method: 'POST' })
      if (!launchRes.ok) {
        const detail = await launchRes.text()
        throw new Error(`Erreur ${launchRes.status} au lancement : ${detail}`)
      }
      const launchData = await launchRes.json()
      taskId = launchData.task_id
    } catch (err) {
      algorithmPhase.value   = 'error'
      algorithmMessage.value = err instanceof Error ? err.message : 'Erreur au lancement'
      algorithmAlert.value   = algorithmMessage.value
      algorithmLog.value     = [`ERREUR : ${algorithmMessage.value}`]
      isLoading.value        = false
      return false
    }

    // 2. Boucle de polling — chaque requête dure < 10 ms
    return new Promise((resolve) => {
      const intervalId = setInterval(async () => {
        try {
          const pollRes = await apiFetch(`/assignments/run-algorithm/${taskId}`)

          if (!pollRes.ok) {
            // La tâche a expiré (3h) ou l'ID est invalide
            clearInterval(intervalId)
            algorithmPhase.value   = 'error'
            algorithmMessage.value = `Tâche introuvable (${pollRes.status})`
            algorithmAlert.value   = algorithmMessage.value
            isLoading.value        = false
            resolve(false)
            return
          }

          const data = await pollRes.json()

          // ── Mise à jour de la progression ─────────────────────────────────
          if (data.pct !== undefined) algorithmProgress.value = data.pct
          if (data.msg) {
            algorithmMessage.value = data.msg
            // N'ajoute au log que si le message est nouveau (évite le spam)
            const lastLog = algorithmLog.value[algorithmLog.value.length - 1]
            if (data.msg !== lastLog) {
              algorithmLog.value = [...algorithmLog.value, data.msg]
            }
          }

          // ── Métriques live (si l'algo les fournit) ────────────────────────
          if (data.postes_total !== undefined) {
            const genMatch = data.msg?.match(/Génération (\d+)\/(\d+)/)
            algorithmStats.value = {
              generation:   genMatch ? `${genMatch[1]}/${genMatch[2]}` : (algorithmStats.value?.generation ?? '—'),
              satisfaction: data.satisfaction !== undefined ? `${data.satisfaction.toFixed(1)}%` : '—',
              postes:       `${data.postes_pourvus ?? '—'}/${data.postes_total}`,
              benevoles:    `${data.benevoles_affectes ?? '—'}/${data.benevoles_total}`,
            }
          }

          // ── Erreur métier remontée par l'algo ─────────────────────────────
          if (data.status === 'error' || data.error) {
            clearInterval(intervalId)
            algorithmPhase.value   = 'error'
            algorithmMessage.value = data.error ?? 'Erreur inconnue'
            algorithmAlert.value   = algorithmMessage.value
            algorithmLog.value     = [...algorithmLog.value, `ERREUR : ${algorithmMessage.value}`]
            isLoading.value        = false
            console.error("Erreur de l'algorithme :", data.error)
            resolve(false)
            return
          }

          // ── Succès ────────────────────────────────────────────────────────
          if (data.status === 'done') {
            clearInterval(intervalId)

            const map      = new Map<AssignmentKey, Assignment>()
            const consumed = new Set<string>()

            for (const item of data.assignments as { volunteer_id: string; job_id: number }[]) {
              const key = makeAssignmentKey(item.volunteer_id, item.job_id)
              const a: Assignment = { volunteer_id: item.volunteer_id, job_id: item.job_id, key }
              map.set(key, a)
              const job = jobs.value.find(j => j.id === item.job_id)
              if (job) {
                for (const h of hoursInSlot(job.slot.start_time, job.slot.end_time)) {
                  consumed.add(`${item.volunteer_id}__${job.slot.day_index}__${h}`)
                }
              }
            }

            assignmentsMap.value    = map
            _consumedSlotKeys.value = consumed
            history.value           = []
            historyIndex.value      = -1
            saveState.value         = 'saved'

            algorithmPhase.value    = 'success'
            algorithmProgress.value = 100
            algorithmMessage.value  = `${data.assignments.length} affectations générées`
            algorithmAlert.value    = `${data.assignments.length} affectations générées`
            algorithmLog.value      = [...algorithmLog.value, 'Affectations persistées en base']
            isLoading.value         = false
            resolve(true)
          }

        } catch (err) {
          // Erreur réseau ponctuelle — on laisse la boucle continuer
          // (l'algo tourne toujours côté serveur ; on réessaiera dans 4s)
          console.warn('Erreur de polling (réessai dans 4s) :', err)
        }
      }, POLL_INTERVAL_MS)
    })
  }

  // ── Validation (utilisée par le Gantt pour les zones de drop) ─────────────

  function getIncompatibilityReason(
    volunteerId: string,
    job:         JobWithRelations,
  ): string | null {
    const volunteer = volunteers.value.find(v => v.id === volunteerId)
    if (!volunteer) return 'Bénévole introuvable'

    if (job.recruitment_type === 'Specialise' && volunteer.volunteer_type === 'Normal') {
      return 'Ce poste est réservé aux bénévoles spécialisés'
    }

    const { day_index, start_time, end_time } = job.slot
    const required = hoursInSlot(start_time, end_time)

    const available = new Set<number>()
    for (const vs of volunteer.slots) {
      if (vs.slot.day_index !== day_index) continue
      const key = `${volunteerId}__${day_index}__${vs.slot.start_time}`
      if (!_consumedSlotKeys.value.has(key)) {
        available.add(vs.slot.start_time)
      }
    }

    const missing = required.filter(h => !available.has(h))
    if (missing.length > 0) {
      const fmt = (h: number) => h < 24 ? `${h}h` : `${h - 24}h`
      return `Indisponible sur ce créneau (manque : ${missing.map(fmt).join(', ')})`
    }

    const count = assignmentsByJob.value.get(job.id)?.length ?? 0
    if (count >= job.required_volunteers) return 'Ce poste est déjà complet'

    if (assignmentsMap.value.has(makeAssignmentKey(volunteerId, job.id))) {
      return 'Ce bénévole est déjà affecté à ce poste'
    }

    return null
  }

  function isCompatible(volunteerId: string, job: JobWithRelations): boolean {
    return getIncompatibilityReason(volunteerId, job) === null
  }

  // ── Export ─────────────────────────────────────────────────────────────────

  return {
    assignments,
    assignmentsByJob,
    assignmentsByVolunteer,
    metricsMap,
    globalMetrics,
    jobs,
    isLoading,
    error,
    saveState,
    consumedSlotKeys: _consumedSlotKeys,

    canUndo,
    canRedo,
    historyPosition,

    fetchAll,
    assign,
    unassign,
    reassign,
    clearAll,
    undo,
    redo,
    save,
    runAlgorithm,

    algorithmProgress,
    algorithmPhase,
    algorithmMessage,
    algorithmLog,
    algorithmStats,
    algorithmAlert,

    isCompatible,
    getIncompatibilityReason,
  }
})