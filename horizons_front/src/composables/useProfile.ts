import { ref } from 'vue'
import { useUserStore } from '../stores/useUserStore'
import type { UserUpdate } from '../types/user.types'
import { apiFetch } from '../api'

export interface UpdateResult {
  success: boolean
  error?: string
}

export function useProfile() {
  const isSaving   = ref(false)
  const saveError  = ref<string | null>(null)
  const userStore  = useUserStore()

  async function updateProfile(payload: UserUpdate): Promise<UpdateResult> {
    isSaving.value  = true
    saveError.value = null

    const token = localStorage.getItem('access_token')
    if (!token) return { success: false, error: 'Non authentifié' }

    const body: UserUpdate = {}
    if (payload.username?.trim())       body.username             = payload.username.trim()
    if (payload.password)               body.password             = payload.password
    if (payload.profile_picture_url)    body.profile_picture_url  = payload.profile_picture_url

    try {
      const response = await apiFetch(`/users/me`, {
        method:  'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail ?? 'Échec de la mise à jour')
      }

      await userStore.fetchCurrentUser()
      return { success: true }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erreur inconnue'
      saveError.value = message
      return { success: false, error: message }
    } finally {
      isSaving.value = false
    }
  }

  return { updateProfile, isSaving, saveError }
}