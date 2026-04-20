const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

let isRedirecting = false

export async function apiFetch(path: string, options: RequestInit = {}): Promise<Response> {
  const token = localStorage.getItem('access_token')

  const isFormData = options.body instanceof FormData

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  })

  if (response.status === 401 && !isRedirecting) {
    isRedirecting = true
    localStorage.removeItem('access_token')

    const { useUserStore } = await import('../stores/useUserStore')
    const { default: router } = await import('../router')

    const userStore = useUserStore()
    userStore.clearUser()
    await router.push({ name: 'Login' })
    isRedirecting = false
  }

  return response
}