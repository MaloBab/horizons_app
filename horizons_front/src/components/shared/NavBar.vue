<template>
  <header class="sticky top-0 z-50 bg-slate-900/80 backdrop-blur-xl border-b border-white/10">
    <div class="container mx-auto px-6 py-4 max-w-7xl">
      <div class="flex items-center justify-between">

        <!-- Brand — ouvre le dropdown festival -->
        <div
          ref="brandRef"
          class="flex items-center gap-4 cursor-pointer select-none"
          @click.stop="openFestivalMenu"
        >
          <div class="w-10 h-10 rounded-xl bg-black flex items-center justify-center shadow-lg shadow-gray-700/30">
            <img src="../../assets/logo-horizons.png" alt="Logo Horizons" class="w-full h-full object-contain" />
          </div>
          <div class="flex flex-col gap-0.5">
            <span class="font-black text-xl uppercase tracking-widest text-white leading-none">HORIZONS</span>
            <span class="text-[9px] tracking-[0.35em] uppercase text-slate-500 font-medium pl-0.5">open sea festival</span>
          </div>
        </div>

        <!-- Nav -->
        <nav v-if="navItems.length > 0" class="hidden md:flex items-center gap-2">
          <router-link
            v-for="item in navItems"
            :key="item.route"
            :to="item.route"
            class="px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex items-center gap-2"
            :class="isActiveRoute(item.route)
              ? 'bg-white/10 text-white shadow-lg'
              : 'text-slate-400 hover:text-white hover:bg-white/5'"
          >
            <component :is="item.icon" class="w-4 h-4 text-cyan-500" />
            <span>{{ item.label }}</span>
          </router-link>
        </nav>

        <!-- User menu -->
        <div class="flex items-center gap-3 relative" v-click-outside="closeUserMenu">
          <div v-if="userStore.isFetching" class="flex items-center gap-3 px-3 py-2">
            <div class="w-24 h-4 rounded bg-white/10 animate-pulse" />
            <div class="w-9 h-9 rounded-lg bg-white/10 animate-pulse" />
          </div>

          <div
            v-else-if="userStore.user"
            class="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-white/5 transition-all duration-200 cursor-pointer group"
            @click="toggleUserMenu"
          >
            <div class="flex flex-col items-end">
              <span class="text-sm font-medium">{{ userStore.user.username }}</span>
              <span class="text-xs text-slate-400 -mt-0.5 capitalize">{{ userStore.user.role }}</span>
            </div>
            <div class="w-9 h-9 rounded-lg overflow-hidden shrink-0 shadow-lg">
              <img
                v-if="userStore.user.profile_picture_url"
                :src="userStore.user.profile_picture_url"
                :alt="userStore.user.username"
                class="w-full h-full object-cover"
              />
              <div
                v-else
                class="w-full h-full bg-linear-to-br from-purple-500 to-pink-500 flex items-center justify-center"
              >
                <span class="text-sm font-semibold">{{ userStore.displayInitial }}</span>
              </div>
            </div>
            <span
              class="text-slate-400 transition-transform duration-200 text-xs"
              :class="{ 'rotate-180': showUserMenu }"
            >▼</span>
          </div>

          <Transition
            enter-active-class="transition duration-200 ease-out"
            enter-from-class="opacity-0 -translate-y-2"
            enter-to-class="opacity-100 translate-y-0"
            leave-active-class="transition duration-150 ease-in"
            leave-from-class="opacity-100 translate-y-0"
            leave-to-class="opacity-0 -translate-y-2"
          >
            <div
              v-if="showUserMenu"
              class="absolute right-0 top-full mt-2 w-64 bg-slate-800 border border-white/10 rounded-xl shadow-2xl overflow-hidden"
            >
              <div class="p-4 border-b border-white/10">
                <div class="text-sm font-medium">{{ userStore.user?.username }}</div>
                <div class="text-xs text-slate-400 mt-0.5 truncate">{{ userStore.user?.email }}</div>
              </div>
              <div class="p-2">
                <router-link
                  v-for="item in userMenuItems"
                  :key="item.route"
                  :to="item.route"
                  class="w-full flex items-center gap-3 px-4 py-2.5 rounded-lg hover:bg-white/5 transition-colors"
                  @click="closeUserMenu"
                >
                  <component :is="item.icon" class="w-4 h-4 shrink-0 text-cyan-500" />
                  <span class="text-sm">{{ item.label }}</span>
                </router-link>
                <div class="h-px bg-white/10 my-2" />
                <button
                  class="w-full flex items-center gap-3 px-4 py-2.5 rounded-lg hover:bg-red-500/10 text-red-400 transition-colors text-left cursor-pointer bg-transparent border-none"
                  @click="handleLogout"
                >
                  <component :is="LogOut" class="w-4 h-4" />
                  <span class="text-sm">Déconnexion</span>
                </button>
              </div>
            </div>
          </Transition>
        </div>

      </div>
    </div>
  </header>

  <!-- Festival dropdown (Teleport géré dans le composant) -->
  <FestivalDropdown v-model="showFestivalMenu" :dropdown-style="festivalDropdownStyle" />
</template>

<script lang="ts">
export default { inheritAttrs: false }
</script>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '../../stores/useUserStore'
import { useAuth } from '../../composables/useAuth'
import { vClickOutside } from '../../directives/clickOutside'
import FestivalDropdown from '../home/FestivalDropdown.vue'
import type { NavItem } from '../../types/navItem.types'
import type { CSSProperties } from 'vue'
import { LayoutDashboard, Users, Briefcase, CalendarDays, CheckSquare, UserCircle, LogOut } from 'lucide-vue-next'

const userStore = useUserStore()
const { logout } = useAuth()
const route = useRoute()

// ── User menu ────────────────────────────────────────────────
const showUserMenu = ref(false)
const toggleUserMenu = () => { showUserMenu.value = !showUserMenu.value }
const closeUserMenu  = () => { showUserMenu.value = false }

// ── Festival dropdown ────────────────────────────────────────
const showFestivalMenu      = ref(false)
const brandRef              = ref<HTMLElement | null>(null)
const festivalDropdownStyle = ref<CSSProperties>({})

function computePosition() {
  if (!brandRef.value) return
  const rect = brandRef.value.getBoundingClientRect()
  const spaceBelow = window.innerHeight - rect.bottom

  if (spaceBelow >= 520 || spaceBelow > window.innerHeight / 2) {
    festivalDropdownStyle.value = {
      top: `${rect.bottom + 10}px`,
      left: `${rect.left}px`,
      transformOrigin: 'top left',
    }
  } else {
    festivalDropdownStyle.value = {
      bottom: `${window.innerHeight - rect.top + 10}px`,
      left: `${rect.left}px`,
      transformOrigin: 'bottom left',
    }
  }
}

async function openFestivalMenu() {
  showFestivalMenu.value = !showFestivalMenu.value
  if (showFestivalMenu.value) {
    await nextTick()
    computePosition()
  }
}

// ── Nav ──────────────────────────────────────────────────────
const navItems: NavItem[] = [
  { label: 'Accueil',    route: '/',           icon: LayoutDashboard },
  { label: 'Bénévoles',  route: '/volunteers',  icon: Users },
  { label: 'Postes',     route: '/job',         icon: Briefcase },
  { label: 'Affectations', route: '/assignments', icon: CalendarDays },
  { label: 'Tâches',     route: '/tasks',       icon: CheckSquare },
]

const userMenuItems = [
  { label: 'Mon Profil', route: '/profile', icon: UserCircle },
]

const isActiveRoute = (path: string) => route.path === path

function handleLogout() {
  closeUserMenu()
  logout()
}
</script>