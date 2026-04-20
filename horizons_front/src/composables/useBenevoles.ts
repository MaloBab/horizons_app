import { ref, computed } from 'vue'
import type { Volunteer, VolunteerTableRow } from '../types/benevole.types'
import type { VolunteerImportReport } from '../types/import.types'
import { apiFetch } from '../api'

async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await apiFetch(`${path}`, {
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

// ── État partagé (singleton) ──────────────────────────────────────────────────
const volunteers        = ref<Volunteer[]>([])
const isLoading         = ref(false)
const selectedVolunteer = ref<Volunteer | null>(null)

export const useBenevoles = () => {

  const volunteersTableData = computed<VolunteerTableRow[]>(() =>
    volunteers.value.map(v => ({
      ...v,
      fullName:   `${v.first_name} ${v.last_name}`,
      slotsCount: v.slots.length,
    }))
  )

  const stats = computed(() => ({
    total: volunteers.value.length,
    avgSlots: volunteers.value.length > 0
      ? (volunteers.value.reduce((s, v) => s + v.slots.length, 0) / volunteers.value.length).toFixed(1)
      : '0',
    withMates: volunteers.value.filter(v => v.mates.length > 0).length,
  }))

  const fetchVolunteers = async () => {
    isLoading.value = true
    try {
      volunteers.value = await api<Volunteer[]>('/volunteers/')
    } finally {
      isLoading.value = false
    }
  }

  const selectVolunteer = (id: string) => {
    selectedVolunteer.value = volunteers.value.find(v => v.id === id) ?? null
  }

  const getVolunteerById = (id: string) => volunteers.value.find(v => v.id === id)

  const deleteVolunteer = async (id: string) => {
    await api(`/volunteers/${id}`, { method: 'DELETE' })
    volunteers.value = volunteers.value.filter(v => v.id !== id)
    if (selectedVolunteer.value?.id === id) selectedVolunteer.value = null
  }

  const deleteAllVolunteers = async () => {
    await api('/volunteers/', { method: 'DELETE' })
    volunteers.value = []
    selectedVolunteer.value = null
  }

  const updateEmail = async (id: string, email: string) => {
    const updated = await api<Volunteer>(`/volunteers/${id}/email`, {
      method: 'PATCH',
      body:   JSON.stringify({ email }),
    })
    _replaceInList(updated)
    return updated
  }

  const updatePhone = async (id: string, phone_number: string) => {
    const updated = await api<Volunteer>(`/volunteers/${id}/phone`, {
      method: 'PATCH',
      body:   JSON.stringify({ phone_number }),
    })
    _replaceInList(updated)
    return updated
  }

  const addAvailability = async (
    volunteerId: string,
    day_index: number,
    start_time: number,
    end_time: number,
  ) => {
    const updated = await api<Volunteer>(`/volunteers/${volunteerId}/slots`, {
      method: 'POST',
      body:   JSON.stringify({ day_index, start_time, end_time }),
    })
    _replaceInList(updated)
    return updated
  }

  const removeSlot = async (volunteerId: string, slotId: number) => {
    const updated = await api<Volunteer>(`/volunteers/${volunteerId}/slots/${slotId}`, {
      method: 'DELETE',
    })
    _replaceInList(updated)
    return updated
  }

  const addMate = async (volunteerId: string, mateId: string) => {
    const updated = await api<Volunteer>(`/volunteers/${volunteerId}/mates`, {
      method: 'POST',
      body:   JSON.stringify({ mate_id: mateId }),
    })
    _replaceInList(updated)
    return updated
  }

  const removeMate = async (volunteerId: string, mateId: string) => {
    const updated = await api<Volunteer>(`/volunteers/${volunteerId}/mates/${mateId}`, {
      method: 'DELETE',
    })
    _replaceInList(updated)
    return updated
  }

  const reorderPreferences = async (volunteerId: string, orderedPreferenceIds: number[]) => {
    const payload = orderedPreferenceIds.map((preferenceId, index) => ({
      preference_id: preferenceId,
      rank: index + 1,
    }))
    const updated = await api<Volunteer>(`/volunteers/${volunteerId}/preferences`, {
      method: 'PATCH',
      body:   JSON.stringify(payload),
    })
    _replaceInList(updated)
    return updated
  }

  // ── Import ────────────────────────────────────────────────────────────────
  // Retourne le rapport complet tel que reçu du back, sans reconstruction manuelle.

const importFromExcel = async (file: File): Promise<{
  success:  boolean
  message:  string
  report:   VolunteerImportReport | null
}> => {
  isLoading.value = true
  try {
    const form = new FormData()
    form.append('file', file)

    const res = await apiFetch(`/volunteers/import`, { method: 'POST', body: form })

    if (!res.ok) {
      const detail = await res.json().catch(() => ({ detail: res.statusText }))
      console.log('422 detail:', JSON.stringify(detail, null, 2))
      const message = Array.isArray(detail.detail)
        ? detail.detail.map((e: any) => e.msg).join(', ')
        : detail.detail ?? `Erreur ${res.status}`
      return { success: false, message, report: null }
    }

    const report: VolunteerImportReport = await res.json()

    await fetchVolunteers()

    const hasErrors   = report.total_errors > 0
    const hasWarnings = report.total_warnings > 0
    let message = `${report.total_persisted} bénévole(s) importé(s) avec succès`
    if (hasErrors)   message += ` — ${report.total_errors} erreur(s)`
    if (hasWarnings) message += ` — ${report.total_warnings} avertissement(s)`

    return { success: true, message, report }

  } catch (e) {
    return { success: false, message: (e as Error).message, report: null }
  } finally {
    isLoading.value = false
  }
}


  const processVolunteers = async (): Promise<{ success: boolean; message: string }> => {
    isLoading.value = true
    try {
      const data = await api<{ message: string }>('/volunteers/process', { method: 'POST' })
      return { success: true, message: data.message }
    } catch (e) {
      return { success: false, message: (e as Error).message }
    } finally {
      isLoading.value = false
    }
  }

  const _replaceInList = (updated: Volunteer) => {
    const idx = volunteers.value.findIndex(v => v.id === updated.id)
    if (idx !== -1) {
      volunteers.value.splice(idx, 1, updated)
    }
    if (selectedVolunteer.value?.id === updated.id) {
      selectedVolunteer.value = updated
    }
  }

  return {
    volunteers, volunteersTableData, isLoading, selectedVolunteer, stats,
    fetchVolunteers, selectVolunteer, getVolunteerById,
    deleteVolunteer, deleteAllVolunteers, updateEmail, updatePhone,
    addAvailability, removeSlot, addMate, removeMate,
    reorderPreferences,
    importFromExcel, processVolunteers,
  }
}