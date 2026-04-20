<template>
  <div
    class="bg-slate-900 text-white"
    :class="route.meta.fillHeight ? 'flex flex-col h-dvh overflow-hidden' : 'min-h-screen'"
  >
    <NavBar
      :user="currentUser"
      @logout="handleLogout"
      @logo-click="goToHome"
      @profile-click="goToProfile"
    />

    <main
      :class="route.meta.fillHeight
        ? 'flex-1 overflow-hidden'
        : route.meta.fullWidth
          ? 'w-full'
          : 'container mx-auto px-6 py-8 max-w-7xl'"
    >
      <router-view v-slot="{ Component }">
        <transition
          mode="out-in"
          enter-active-class="transition duration-200 ease-out"
          enter-from-class="opacity-0 translate-y-4"
          enter-to-class="opacity-100 translate-y-0"
          leave-active-class="transition duration-150 ease-in"
          leave-from-class="opacity-100 translate-y-0"
          leave-to-class="opacity-0 -translate-y-4"
        >
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import NavBar from './components/shared/NavBar.vue'
import { useAuth } from './composables/useAuth'
import { useUserStore } from './stores/useUserStore'

const userStore = useUserStore()
const currentUser = userStore.user

const router = useRouter()
const route  = useRoute()
const { logout } = useAuth()

const handleLogout = () => {
  logout()
  router.push('/login')
}

const goToHome    = () => router.push('/')
const goToProfile = () => router.push('/profile')
</script>