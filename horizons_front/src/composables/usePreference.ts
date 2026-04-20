import type { Preference, Category } from '../types/planning.types'
import { apiFetch as coreFetch } from '../api'

async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await coreFetch(path, {
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

// ── Preferences ──────────────────────────────────────────────────────────────

export async function fetchPreferences(): Promise<Preference[]> {
  return api<Preference[]>('/preferences/')
}

export async function createPreference(label: string): Promise<Preference> {
  return api<Preference>('/preferences/', {
    method: 'POST',
    body: JSON.stringify({ label }),
  })
}

export async function renamePreference(id: number, label: string): Promise<Preference> {
  return api<Preference>(`/preferences/${id}`, {
    method: 'PATCH',
    body: JSON.stringify({ label }),
  })
}

export async function deletePreference(id: number): Promise<void> {
  return api<void>(`/preferences/${id}`, { method: 'DELETE' })
}

// ── Categories ────────────────────────────────────────────────────────────────

export async function fetchAllCategories(): Promise<Category[]> {
  return api<Category[]>('/categories/')
}

export async function attachCategory(id: number, preferenceId: number): Promise<Category> {
  return api<Category>(`/categories/${id}`, {
    method: 'PATCH',
    body: JSON.stringify({ preference_id: preferenceId }),
  })
}

export async function createCategory(
  label:        string,
  preferenceId: number,
  poleId?:      number | null,
): Promise<Category> {
  return api<Category>('/categories/', {
    method: 'POST',
    body: JSON.stringify({
      label,
      preference_id: preferenceId,
      pole_id: poleId ?? null,
    }),
  })
}

export async function updateCategory(
  id:      number,
  label:   string,
  poleId?: number | null,
): Promise<Category> {
  return api<Category>(`/categories/${id}`, {
    method: 'PATCH',
    body: JSON.stringify({
      label,
      pole_id: poleId ?? null,
    }),
  })
}

export async function deleteCategory(id: number): Promise<void> {
  return api<void>(`/categories/${id}`, { method: 'DELETE' })
}