import { ref } from 'vue'
import { useUserStore } from '../../stores/useUserStore'
import type { Activity } from '../../types/activity.types'
import { apiFetch } from '../../api'

export function useActivity() {
  const activities = ref<Activity[]>([])
  const isLoading = ref(false)
  const userStore = useUserStore()

  async function fetchActivities(limit: number = 50) {
    isLoading.value = true
    try {
      const response = await apiFetch(`/activities/?limit=${limit}`)
      if (!response.ok) throw new Error()
      activities.value = await response.json()
    } finally {
      isLoading.value = false
    }
  }

  async function createActivity(payload: any) {
    if (!userStore.isAuthenticated) {
      return { success: false, error: 'Session expirée' }
    }

    try {
      const response = await apiFetch(`/activities/`, {
        method: 'POST',
        body: JSON.stringify(payload)
      })
      
      if (response.status === 401) {
        userStore.clearUser()
        return { success: false, error: 'Session invalide' }
      }

      const newActivity = await response.json()
      activities.value = [newActivity, ...activities.value]
      return { success: true }
    } catch (err) {
      return { success: false, error: 'Erreur serveur' }
    }
  }

  async function bulkDeleteRecent(limit: number = 5) {
    if (!userStore.isAdmin) {
      return { success: false, error: 'Droits insuffisants' }
    }

    try {
      const response = await apiFetch(`/activities/old?limit=${limit}`, {
        method: 'DELETE',
      })

      if (response.ok) await fetchActivities()
      return { success: true }
    } catch (err) {
      return { success: false }
    }
  }

  return {
    activities,
    isLoading,
    fetchActivities,
    createActivity,
    bulkDeleteRecent
  }
}