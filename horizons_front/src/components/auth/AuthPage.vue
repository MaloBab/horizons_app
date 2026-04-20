<template>
  <div class="relative flex items-center justify-center bg-slate-900 overflow-hidden px-4 py-8 -mt-11">
    <div class="relative z-10 w-full max-w-110 animate-[cardIn_0.5s_ease-out_both]">

      <div class="flex items-center gap-3 mb-5">
        <div class="w-10 h-10 rounded-xl bg-black flex items-center justify-center shadow-lg shadow-black/40">
          <img src="../../assets/logo-horizons.png" alt="Logo Horizons" class="w-full h-full object-contain" />
        </div>
        <div class="flex flex-col">
          <span class="font-bold text-lg tracking-tight text-white">Horizons</span>
          <span class="text-xs text-slate-400 -mt-0.5">Gestion des bénévoles</span>
        </div>
      </div>

      <div
        class="relative flex bg-slate-800/50 border border-white/10 rounded-xl p-1 mb-5"
        role="tablist"
      >
        <div
          class="absolute top-1 bottom-1 w-[calc(50%-4px)] bg-linear-to-r from-cyan-500 to-blue-600 border border-cyan-500/20 rounded-[9px] transition-transform duration-300 ease-[cubic-bezier(0.34,1.56,0.64,1)] shadow-lg shadow-cyan-500/20"
          :class="mode === 'register' ? 'translate-x-[calc(100%+4px)]' : 'translate-x-0'"
        />
        <button
          role="tab"
          :aria-selected="mode === 'login'"
          class="relative flex-1 py-2 text-sm font-medium rounded-[9px] transition-colors duration-200 cursor-pointer bg-transparent border-none"
          :class="mode === 'login' ? 'text-white' : 'text-slate-400 hover:text-slate-300'"
          @click="switchMode('login')"
        >Connexion</button>
        <button
          role="tab"
          :aria-selected="mode === 'register'"
          class="relative flex-1 py-2 text-sm font-medium rounded-[9px] transition-colors duration-200 cursor-pointer bg-transparent border-none"
          :class="mode === 'register' ? 'text-white' : 'text-slate-400 hover:text-slate-300'"
          @click="switchMode('register')"
        >Inscription</button>
      </div>

      <div v-if="notification.message" class="mb-4">
        <AuthNotification
          :visible="!!notification.message"
          :message="notification.message"
          :type="notification.type"
        />
      </div>

      <div class="bg-slate-800/50 border border-white/10 rounded-2xl p-5 backdrop-blur-sm shadow-xl">
        <Transition :name="transitionName" mode="out-in">

          <form v-if="mode === 'login'" key="login" class="flex flex-col gap-3" @submit.prevent="handleLogin" novalidate>

            <AuthInput
              id="login-username"
              v-model="loginForm.username"
              label="Nom d'utilisateur / Email"
              placeholder="entrez votre nom d'utilisateur ou email"
              autocomplete="username"
              :error="loginErrors.username"
            >
              <template #icon>
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
                </svg>
              </template>
            </AuthInput>

            <AuthInput
              id="login-password"
              v-model="loginForm.password"
              label="Mot de passe"
              type="password"
              placeholder="••••••••"
              autocomplete="current-password"
              :error="loginErrors.password"
            >
              <template #icon>
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
              </template>
            </AuthInput>


            <button
              type="submit"
              :disabled="isLoading"
              class="interactive relative w-full py-3 rounded-xl bg-linear-to-r from-cyan-500 to-blue-600 text-white text-sm font-semibold transition-all duration-200 cursor-pointer border-none shadow-lg shadow-cyan-500/20 hover:shadow-cyan-500/30 hover:-translate-y-px active:translate-y-0 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0 overflow-hidden group"
            >
              <span class="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
              <span v-if="!isLoading">Se connecter</span>
              <span v-else class="flex items-center justify-center gap-2">
                <svg class="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" stroke-linecap="round"/>
                </svg>
                Connexion…
              </span>
            </button>
            <GoogleAuthButton />
          </form>

          <!-- ── REGISTER ──────────────────────────────────────────────────── -->
          <form v-else key="register" class="flex flex-col gap-3" @submit.prevent="handleRegister" novalidate>

            <AuthInput
              id="reg-username"
              v-model="registerForm.username"
              label="Nom d'utilisateur"
              placeholder="entrez votre nom d'utilisateur"
              autocomplete="username"
              :error="registerErrors.username"
            >
              <template #icon>
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
                </svg>
              </template>
            </AuthInput>

            <AuthInput
              id="reg-email"
              v-model="registerForm.email"
              label="Adresse email"
              type="email"
              placeholder="fake.address@example.com"
              autocomplete="email"
              :error="registerErrors.email"
            >
              <template #icon>
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/>
                </svg>
              </template>
            </AuthInput>

            <div>
              <AuthInput
                id="reg-password"
                v-model="registerForm.password"
                label="Mot de passe"
                type="password"
                placeholder="••••••••"
                autocomplete="new-password"
                :error="registerErrors.password"
              >
                <template #icon>
                  <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                  </svg>
                </template>
              </AuthInput>
              <PasswordStrengthBar :password="registerForm.password" />
            </div>

            <AuthInput
              id="reg-confirm"
              v-model="registerForm.confirmPassword"
              label="Confirmer le mot de passe"
              type="password"
              placeholder="••••••••"
              autocomplete="new-password"
              :error="registerErrors.confirmPassword"
            >
              <template #icon>
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                </svg>
              </template>
            </AuthInput>

            <!-- Submit -->
            <button
              type="submit"
              :disabled="isLoading"
              class="interactive relative w-full py-3 rounded-xl bg-linear-to-r from-cyan-500 to-blue-600 text-white text-sm font-semibold transition-all duration-200 cursor-pointer border-none shadow-lg shadow-cyan-500/20 hover:shadow-cyan-500/30 hover:-translate-y-px active:translate-y-0 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0 overflow-hidden group"
            >
              <span class="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
              <span v-if="!isLoading">Créer mon compte</span>
              <span v-else class="flex items-center justify-center gap-2">
                <svg class="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" stroke-linecap="round"/>
                </svg>
                Création…
              </span>
            </button>
            <GoogleAuthButton />
          </form>

        </Transition>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import AuthInput from './AuthInput.vue'
import AuthNotification from './AuthNotification.vue'
import PasswordStrengthBar from './PasswordStrengthBar.vue'
import { useAuth } from '../../composables/useAuth'
import { useFormValidation } from '../../composables/useFormValidation'
import type { AuthMode, AuthNotification as IAuthNotification } from '../../types/auth.types'
import { useRouter } from 'vue-router'
import GoogleAuthButton from './GoogleAuthButton.vue'

const router = useRouter()

const mode = ref<AuthMode>('login')
const transitionName = ref<'slide-left' | 'slide-right'>('slide-left')
const notification = reactive<IAuthNotification>({ message: '', type: 'error' })

const { login, register, isLoading } = useAuth()
const {
  loginForm, registerForm,
  loginErrors, registerErrors,
  validateLogin, validateRegister,
  clearErrors,
} = useFormValidation()


function switchMode(target: AuthMode) {
  transitionName.value = target === 'register' ? 'slide-left' : 'slide-right'
  mode.value = target
  notification.message = ''
  clearErrors()
}

function showNotif(message: string, type: IAuthNotification['type'] = 'error') {
  notification.message = message
  notification.type = type
  if (type === 'success') setTimeout(() => (notification.message = ''), 3500)
}

async function handleLogin() {
  if (!validateLogin()) return
  const result = await login({ username: loginForm.username, password: loginForm.password })
  if (result.success) {
    showNotif('Connexion réussie ! Redirection…', 'success')
    setTimeout(() => {
        router.push('/') 
    }, 1000)
  } else {
    showNotif(result.error ?? 'Erreur de connexion')
  }
}

async function handleRegister() {
  if (!validateRegister()) return
  const result = await register({
    username: registerForm.username,
    email: registerForm.email,
    password: registerForm.password,
  })
  if (result.success) {
    showNotif('Compte créé avec succès ! Vous pouvez vous connecter.', 'success')
    setTimeout(() => switchMode('login'), 2000)
  } else {
    showNotif(result.error ?? "Erreur lors de l'inscription")
  }
}

</script>

<style>
@keyframes cardIn {
  from { opacity: 0; transform: translateY(20px) scale(0.98); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}

.slide-left-enter-active,
.slide-left-leave-active,
.slide-right-enter-active,
.slide-right-leave-active {
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.slide-left-enter-from  { opacity: 0; transform: translateX(20px); }
.slide-left-leave-to    { opacity: 0; transform: translateX(-20px); }
.slide-right-enter-from { opacity: 0; transform: translateX(-20px); }
.slide-right-leave-to   { opacity: 0; transform: translateX(20px); }

/* Scrollbar ultra fine et élégante */
@keyframes glowPulse {
  0%, 100% { text-shadow: 0 0 8px rgba(34, 211, 238, 0.3); }
  50% { text-shadow: 0 0 16px rgba(34, 211, 238, 0.6); }
}
</style>
