<template>
  <div class=" bg-slate-900 flex flex-col">
    <div class="fixed inset-0 pointer-events-none" aria-hidden="true">
      <div class="absolute top-0 right-0 w-125 h-125 bg-cyan-500/5 rounded-full blur-3xl" />
      <div class="absolute bottom-0 left-0 w-125 h-125 bg-purple-500/5 rounded-full blur-3xl" />
    </div>

    <div class="relative z-10 flex flex-col flex-1 container mx-auto max-w-5xl -mt-6">

      <div v-if="userStore.user" class="flex flex-col flex-1 gap-4">
        <div class="grid grid-cols-1 md:grid-cols-[280px_1fr] gap-4 flex-1">

          <!-- Colonne gauche -->
          <div class="flex flex-col gap-3">
            <div class="bg-slate-800/50 border border-white/10 rounded-2xl p-5 backdrop-blur-sm flex flex-col items-center gap-4">
              <AvatarUpload
                :current-url="userStore.user.profile_picture_url!"
                :initial="userStore.displayInitial"
                @uploaded="handleAvatarUploaded"
              />
              <div class="text-center w-full">
                <p class="text-base font-bold text-white">{{ userStore.user.username }}</p>
                <p class="text-xs text-slate-400 mt-0.5 truncate">{{ userStore.user.email }}</p>
                <span
                  class="inline-flex items-center gap-1.5 mt-3 text-xs px-2.5 py-1 rounded-full font-medium border"
                  :class="userStore.user.role === 'admin'
                    ? 'bg-purple-500/15 text-purple-400 border-purple-500/20'
                    : 'bg-cyan-500/15 text-cyan-400 border-cyan-500/20'"
                >
                  <span class="w-1.5 h-1.5 rounded-full"
                    :class="userStore.user.role === 'admin' ? 'bg-purple-400' : 'bg-cyan-400'"
                  />
                  {{ userStore.user.role === 'admin' ? 'Administrateur' : 'EKIP' }}
                </span>
              </div>
            </div>

            <!-- Notification juste sous la carte avatar -->
            <Transition
              enter-active-class="transition-all duration-300 ease-out"
              enter-from-class="opacity-0 -translate-y-1"
              leave-active-class="transition-all duration-200 ease-in"
              leave-to-class="opacity-0 -translate-y-1"
            >
              <div
                v-if="notification.message"
                class="flex items-center gap-2 px-3 py-2.5 rounded-xl text-xs font-medium border"
                :class="notification.type === 'error'
                  ? 'bg-red-500/10 border-red-500/20 text-red-400'
                  : 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'"
              >
                <svg v-if="notification.type === 'error'" class="w-3.5 h-3.5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                <svg v-else class="w-3.5 h-3.5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                {{ notification.message }}
              </div>
            </Transition>
          </div>

          <!-- Colonne droite -->
          <div class="bg-slate-800/50 border border-white/10 rounded-2xl p-5 backdrop-blur-sm flex flex-col gap-5 h-fit">

            <ProfileInfoSection
              :username="form.username"
              :email="userStore.user.email"
              :role="userStore.user.role"
              @update:username="form.username = $event"
            />

            <div class="h-px bg-white/5" />

            <ProfilePasswordSection
              ref="passwordSectionRef"
              @update:password="form.password = $event"
            />
            <div class="flex-1" />

            <div class="flex items-center justify-end gap-3 pt-2 border-t border-white/5">
              <button
                type="button"
                class="px-4 py-2.5 rounded-xl border border-white/10 bg-transparent text-slate-400 text-sm font-medium hover:bg-white/5 hover:text-white transition-all duration-200 cursor-pointer"
                :disabled="isSaving"
                @click="resetForm"
              >
                Annuler
              </button>
              <button
                type="button"
                :disabled="isSaving || !hasChanges"
                class="interactive relative px-5 py-2.5 rounded-xl bg-linear-to-r from-cyan-500 to-blue-600 text-white text-sm font-semibold transition-all duration-200 cursor-pointer border-none shadow-lg shadow-cyan-500/20 hover:shadow-cyan-500/30 hover:-translate-y-px active:translate-y-0 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0 overflow-hidden group"
                @click="handleSave"
              >
                <span class="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
                <span v-if="!isSaving" class="flex items-center gap-2">
                  <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
                    <polyline points="17 21 17 13 7 13 7 21"/>
                    <polyline points="7 3 7 8 15 8"/>
                  </svg>
                  Enregistrer les modifications
                </span>
                <span v-else class="flex items-center gap-2">
                  <svg class="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" stroke-linecap="round"/>
                  </svg>
                  Enregistrement…
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-[280px_1fr] gap-4 animate-pulse">
        <div class="bg-slate-800/50 border border-white/10 rounded-2xl p-5 flex flex-col items-center gap-4">
          <div class="w-24 h-24 rounded-2xl bg-slate-700" />
          <div class="h-4 w-28 rounded-lg bg-slate-700" />
          <div class="h-3 w-36 rounded-lg bg-slate-700" />
          <div class="h-5 w-20 rounded-full bg-slate-700" />
        </div>
        <div class="bg-slate-800/50 border border-white/10 rounded-2xl p-5 h-80" />
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useUserStore } from '../../stores/useUserStore'
import { useProfile } from '../../composables/useProfile'
import AvatarUpload from './AvatarUpload.vue'
import ProfileInfoSection from './ProfileInfoSection.vue'
import ProfilePasswordSection from './ProfilePasswordSection.vue'

const userStore = useUserStore()
const { updateProfile, isSaving } = useProfile()
const passwordSectionRef = ref<InstanceType<typeof ProfilePasswordSection> | null>(null)

const form = reactive({
  username: userStore.user?.username ?? '',
  password: '',
  profile_picture_url: userStore.user?.profile_picture_url ?? '',
})

const notification = reactive({ message: '', type: 'error' as 'error' | 'success' })

const hasChanges = computed(() => {
  const u = userStore.user
  if (!u) return false
  return (
    form.username.trim() !== u.username ||
    form.password !== '' ||
    form.profile_picture_url !== (u.profile_picture_url ?? '')
  )
})


function handleAvatarUploaded(url: string) {
  form.profile_picture_url = url
  save({ profile_picture_url: url })
}

function resetForm() {
  const u = userStore.user
  if (!u) return
  form.username = u.username
  form.password = ''
  form.profile_picture_url = u.profile_picture_url ?? ''
  passwordSectionRef.value?.reset()
}

async function save(overrides?: Partial<typeof form>) {
  const payload = overrides ?? {
    username: form.username.trim() !== userStore.user?.username ? form.username.trim() : undefined,
    password: form.password || undefined,
    profile_picture_url: form.profile_picture_url !== (userStore.user?.profile_picture_url ?? '')
      ? form.profile_picture_url
      : undefined,
  }
  const result = await updateProfile(payload)
  if (result.success) {
    showNotif('Profil mis à jour avec succès.', 'success')
    form.password = ''
    passwordSectionRef.value?.reset()
  } else {
    showNotif(result.error ?? 'Erreur lors de la sauvegarde')
  }
}

async function handleSave() { await save() }

function showNotif(message: string, type: 'error' | 'success' = 'error') {
  notification.message = message
  notification.type = type
  if (type === 'success') setTimeout(() => (notification.message = ''), 3500)
}

onMounted(() => {
  if (!userStore.user) userStore.fetchCurrentUser()
  else resetForm()
})
</script>