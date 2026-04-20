import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserResponse } from '../types/user.types'
import { mapUser } from '../composables/useUsers'
import type { User as TaskUser } from '../types/task.types'
import { apiFetch } from '../api'

export const useUserStore = defineStore('user', () => {

  const user       = ref<UserResponse | null>(null)
  const isFetching = ref(false)
  const fetchError = ref<string | null>(null)

  const isAuthenticated = computed(() => user.value !== null)
  const isAdmin         = computed(() => user.value?.role === 'admin')
  const displayInitial  = computed(() => user.value?.username.charAt(0).toUpperCase() ?? '?')

  const asTaskUser = computed((): TaskUser | null => {
    if (!user.value) return null
    return mapUser(user.value)
  })

  async function fetchCurrentUser(): Promise<boolean> {
    const token = localStorage.getItem('access_token')
    if (!token) return false

    isFetching.value = true
    fetchError.value = null

    try {
      const response = await apiFetch('/users/me')

      if (!response.ok) {
        clearUser()
        throw new Error('Session expirée, veuillez vous reconnecter.')
      }

      user.value = (await response.json()) as UserResponse
      return true
    } catch (err) {
      fetchError.value = err instanceof Error ? err.message : 'Erreur inconnue'
      return false
    } finally {
      isFetching.value = false
    }
  }

  function clearUser(): void {
    user.value = null
    localStorage.removeItem('access_token')
  }

  return {
    user,
    isFetching,
    fetchError,
    isAuthenticated,
    isAdmin,
    displayInitial,
    asTaskUser,
    fetchCurrentUser,
    clearUser,
  }
})