import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/useUserStore'
import type { LoginPayload, RegisterPayload, AuthToken } from '../types/auth.types'
import { apiFetch } from '../api'

interface AuthResult<T = unknown> {
  success: boolean
  data?: T
  error?: string
}

export function useAuth() {
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const router = useRouter()
  const userStore = useUserStore()

  async function login(payload: LoginPayload): Promise<AuthResult<AuthToken>> {
    isLoading.value = true
    error.value = null
    try {
      const formData = new URLSearchParams()
      formData.append('username', payload.username)
      formData.append('password', payload.password)

      const response = await apiFetch(`/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData,
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail ?? 'Identifiants incorrects')
      }

      const data: AuthToken = await response.json()
      localStorage.setItem('access_token', data.access_token)
      await userStore.fetchCurrentUser()

      return { success: true, data }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erreur inconnue'
      error.value = message
      return { success: false, error: message }
    } finally {
      isLoading.value = false
    }
  }

  async function register(payload: RegisterPayload): Promise<AuthResult> {
    isLoading.value = true
    error.value = null
    try {
      const response = await apiFetch(`/users/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail ?? "Échec de l'inscription")
      }

      return { success: true, data: await response.json() }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erreur inconnue'
      error.value = message
      return { success: false, error: message }
    } finally {
      isLoading.value = false
    }
  }

  function logout(): void {
    userStore.clearUser()
    router.push('/login')
  }

  return { login, register, logout, isLoading, error }
}