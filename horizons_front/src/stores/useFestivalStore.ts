// stores/useFestivalStore.ts
import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { FestivalResponse, FestivalCreate, FestivalUpdate } from '../types/festival.types'
import { apiFetch } from '../api'


export const useFestivalStore = defineStore('festival', () => {
  const festival = ref<FestivalResponse | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function fetchFestival(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const response = await apiFetch(`/festival/`)
      if (response.status === 404) { festival.value = null; return }
      if (!response.ok) throw new Error('Erreur lors de la récupération du festival.')
      festival.value = await response.json()
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Erreur inconnue'
    } finally {
      isLoading.value = false
    }
  }

  async function createFestival(data: FestivalCreate): Promise<boolean> {
    isLoading.value = true
    error.value = null
    try {
      const response = await apiFetch(`/festival/`, {
        method: 'POST', body: JSON.stringify(data),
      })
      if (!response.ok) { const b = await response.json(); throw new Error(b.detail ?? 'Erreur.') }
      festival.value = await response.json()
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Erreur inconnue'
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function updateFestival(data: FestivalUpdate): Promise<boolean> {
    isLoading.value = true
    error.value = null
    try {
      const response = await apiFetch(`/festival/`, {
        method: 'PATCH', body: JSON.stringify(data),
      })
      if (!response.ok) { const b = await response.json(); throw new Error(b.detail ?? 'Erreur.') }
      festival.value = await response.json()
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Erreur inconnue'
      return false
    } finally {
      isLoading.value = false
    }
  }

  return { festival, isLoading, error, fetchFestival, createFestival, updateFestival }
})