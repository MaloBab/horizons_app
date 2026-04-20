<template>
  <div class="flex items-center justify-center min-h-screen bg-slate-900">
    <div class="flex flex-col items-center gap-4 text-slate-400">
      <svg class="w-8 h-8 animate-spin text-cyan-400" viewBox="0 0 24 24" fill="none"
        stroke="currentColor" stroke-width="2.5">
        <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"
          stroke-linecap="round" />
      </svg>
      <p class="text-sm">Connexion en cours…</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../../stores/useUserStore'
import { apiFetch } from '../../api'

const router   = useRouter()
const route    = useRoute()
const userStore = useUserStore()

onMounted(async () => {
  const code = route.query.code as string | undefined

  if (!code) {
    router.replace('/login?error=oauth_failed')
    return
  }

  try {
    const response = await apiFetch('/auth/google/exchange', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code }),
    })

    if (!response.ok) throw new Error()

    const { access_token } = await response.json()
    localStorage.setItem('access_token', access_token)

    const ok = await userStore.fetchCurrentUser()
    if (ok) {
      router.replace('/')
    } else {
      throw new Error()
    }
  } catch {
    localStorage.removeItem('access_token')
    router.replace('/login?error=oauth_failed')
  }
})
</script>