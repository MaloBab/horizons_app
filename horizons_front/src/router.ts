import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useUserStore } from './stores/useUserStore'

function isTokenExpired(token: string): boolean {
  try {
    const parts = token.split('.')
    if (parts.length !== 3) return true
    const payload = JSON.parse(atob(parts[1]!))
    return payload.exp * 1000 < Date.now()
  } catch {
    return true
  }
}

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('./components/auth/AuthPage.vue'),
    meta: { requiresGuest: true },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('./components/profile/ProfilePage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/',
    name: 'Home',
    component: () => import('./components/home/HomePage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/job',
    name: 'Job',
    component: () => import('./components/jobs/PlanningView.vue'),
    meta: { requiresAuth: true, fullWidth: true },
  },
  {
    path: '/volunteers',
    name: 'Volunteers',
    component: () => import('./components/benevoles/BenevoleManagement.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: () => import('./components/tasks/ActivityDashboard.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/communication',
    name : 'Communication',
    component: () => import('./components/communicationPage/VolunteerMailPage.vue'),
    meta: { requiresAuth: true, fillHeight: true },
  },
  {
    path: '/assignments',
    name: 'Assignments',
    component: () => import('./components/assignments/AssignmentView.vue'),
    meta: { requiresAuth: true, fullWidth: true, fillHeight: true },
  },
  {
    path: '/auth/callback',
    component: () => import('./components/auth/AuthCallbackView.vue'),
    meta: { public: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const userStore = useUserStore()
  if (to.meta.public) return true

  const token = localStorage.getItem('access_token')

  if (!token) {
    if (to.meta.requiresAuth) return { name: 'Login' }
    return true
  }

  if (isTokenExpired(token)) {
    userStore.clearUser()
    if (to.meta.requiresAuth) return { name: 'Login' }
    return true
  }

  if (!userStore.user) {
    const success = await userStore.fetchCurrentUser()
    if (!success) {
      if (to.meta.requiresAuth) return { name: 'Login' }
      return true
    }
  }

  if (to.meta.requiresAuth && !userStore.isAuthenticated) {
    return { name: 'Login' }
  }

  if (to.meta.requiresGuest && userStore.isAuthenticated) {
    return { name: 'Home' }
  }
})

export default router