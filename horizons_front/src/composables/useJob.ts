/**
 * composables/useJob.ts
 * Service API pour les postes — remplace les mockdata de PlanningView.vue
 */
import type { CategoryGroup, CategoryGroupResponse, JobWithRelations } from '../types/planning.types'
import type { ImportReport } from '../types/import.types'
import { apiFetch } from '../api'


export function getTotalNormalVolunteers(groups: CategoryGroup[]): number {
  return groups.reduce((total, group) => {
    // On filtre les jobs du groupe par type 'Normal'
    const normalJobs = group.jobs.filter(job => job.recruitment_type === 'Normal')
    
    // On additionne les required_volunteers de ces jobs filtrés
    const groupTotal = normalJobs.reduce((sum, job) => sum + job.required_volunteers, 0)
    
    return total + groupTotal
  }, 0)
}

async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await apiFetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const detail = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(detail.detail ?? `Erreur ${res.status}`)
  }
  if (res.status === 204) return undefined as T
  return res.json()
}

// ── Import ──────────────────────────────────────────────────────────────────

export async function importJobs(file: File): Promise<ImportReport> {
  const form = new FormData()
  form.append('file', file)

  const res = await apiFetch('/jobs/import', { method: 'POST', body: form })

  if (!res.ok) {
    const detail = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(detail.detail ?? `Erreur ${res.status}`)
  }

  return res.json()
}

// ── Jobs ────────────────────────────────────────────────────────────────────

export async function fetchCategoryGroups(): Promise<CategoryGroup[]> {
  const raw = await api<CategoryGroupResponse[]>('/jobs/grouped')
  return raw.map(group => ({
    category: group.category,
    jobs: group.jobs.flatMap(jobGroup => jobGroup.slots),
  }))
}

export async function fetchJob(id: number): Promise<JobWithRelations> {
  return api<JobWithRelations>(`/jobs/${id}`)
}

export interface JobCreatePayload {
  name: string
  required_volunteers: number
  recruitment_type: 'Normal' | 'Specialise'
  category_id: number
  slot: {
    day_index: number
    start_time: number
    end_time: number
  }
}

export async function createJob(payload: JobCreatePayload): Promise<JobWithRelations> {
  return api<JobWithRelations>('/jobs/', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function updateJob(
  id: number,
  payload: Partial<JobCreatePayload>,
): Promise<JobWithRelations> {
  return api<JobWithRelations>(`/jobs/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

export async function deleteJob(id: number): Promise<void> {
  return api<void>(`/jobs/${id}`, { method: 'DELETE' })
}

export async function deleteAllJobs(groups: CategoryGroup[]): Promise<void> {
  const ids = groups.flatMap(g => g.jobs.map(j => j.id))
  await Promise.all(ids.map(id => deleteJob(id)))
}

// ── Categories ──────────────────────────────────────────────────────────────

export interface CategoryPayload { name: string }

export async function fetchCategories() {
  return api<{ id: number; name: string }[]>('/categories/')
}

export async function createCategory(payload: CategoryPayload) {
  return api<{ id: number; name: string }>('/categories/', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

// ── Slots ───────────────────────────────────────────────────────────────────

export interface SlotPayload {
  day: number
  start_hour: number
  end_hour: number
}

export async function fetchSlots() {
  return api<{ id: number; day: number; start_hour: number; end_hour: number }[]>('/slots/')
}

export async function createSlot(payload: SlotPayload) {
  return api<{ id: number; day: number; start_hour: number; end_hour: number }>('/slots/', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}