<template>
  <div class="flex flex-col gap-2 ">
    <h3 class="text-xs font-semibold text-slate-400 uppercase tracking-widest">Mot de passe</h3>

    <!-- Nouveau mot de passe -->
    <div class="flex flex-col gap-1.5">
      <label class="text-xs font-medium text-slate-400">Nouveau mot de passe</label>
      <div
        class="flex items-center gap-2.5 px-3.5 rounded-xl border bg-slate-800/50 transition-all duration-200"
        :class="focusedField === 'new'
          ? 'border-cyan-500/50 shadow-[0_0_0_3px_rgba(6,182,212,0.08)]'
          : 'border-white/10 hover:border-white/20'"
      >
        <svg class="w-4 h-4 shrink-0 transition-colors" :class="focusedField === 'new' ? 'text-cyan-400/70' : 'text-slate-500'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>
        </svg>
        <input id="edit-password"
          v-model="newPassword"
          :type="showNew ? 'text' : 'password'"
          placeholder="Laisser vide pour ne pas modifier"
          autocomplete="new-password"
          class="flex-1 bg-transparent border-none outline-none text-white text-sm placeholder:text-slate-600 py-3 caret-cyan-400"
          @focus="focusedField = 'new'"
          @blur="focusedField = null"
          @input="emitIfValid"
        />
        <button type="button" tabindex="-1" class="text-slate-500 hover:text-slate-300 transition-colors cursor-pointer p-0 bg-transparent border-none" @click="showNew = !showNew">
          <svg v-if="!showNew" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
          <svg v-else class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
        </button>
      </div>
      <PasswordStrengthBar v-if="newPassword" :password="newPassword" />
    </div>

    <!-- Confirmation -->
    <div class="flex flex-col gap-1.5">
      <label class="text-xs font-medium text-slate-400">Confirmer le mot de passe</label>
      <div
        class="flex items-center gap-2.5 px-3.5 rounded-xl border bg-slate-800/50 transition-all duration-200"
        :class="[
          confirmError ? 'border-red-500/50' :
          focusedField === 'confirm'
            ? 'border-cyan-500/50 shadow-[0_0_0_3px_rgba(6,182,212,0.08)]'
            : 'border-white/10 hover:border-white/20'
        ]"
      >
        <svg class="w-4 h-4 shrink-0 transition-colors" :class="focusedField === 'confirm' ? 'text-cyan-400/70' : 'text-slate-500'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
        </svg>
        <input id="confirm-password"
          v-model="confirmPassword"
          :type="showConfirm ? 'text' : 'password'"
          placeholder="••••••••"
          autocomplete="new-password"
          class="flex-1 bg-transparent border-none outline-none text-white text-sm placeholder:text-slate-600 py-3 caret-cyan-400"
          @focus="focusedField = 'confirm'"
          @blur="focusedField = null"
          @input="emitIfValid"
        />
        <button type="button" tabindex="-1" class="text-slate-500 hover:text-slate-300 transition-colors cursor-pointer p-0 bg-transparent border-none" @click="showConfirm = !showConfirm">
          <svg v-if="!showConfirm" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
          <svg v-else class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
        </button>
      </div>
      <p v-if="confirmError" class="text-xs text-red-400">{{ confirmError }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import PasswordStrengthBar from '../auth/PasswordStrengthBar.vue'

const emit = defineEmits<{
  'update:password': [value: string]
}>()

const newPassword = ref('')
const confirmPassword = ref('')
const showNew = ref(false)
const showConfirm = ref(false)
const focusedField = ref<'new' | 'confirm' | null>(null)

const confirmError = computed(() =>
  confirmPassword.value && newPassword.value !== confirmPassword.value
    ? 'Les mots de passe ne correspondent pas'
    : ''
)

function emitIfValid() {
  if (newPassword.value.length >= 8 && newPassword.value === confirmPassword.value) {
    emit('update:password', newPassword.value)
  } else {
    emit('update:password', '')
  }
}

function reset() {
  newPassword.value = ''
  confirmPassword.value = ''
}
defineExpose({ reset })
</script>