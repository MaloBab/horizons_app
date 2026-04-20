<template>
  <div class="flex flex-col gap-3">
    <h3 class="text-xs font-semibold text-slate-400 uppercase tracking-widest">Informations générales</h3>

    <!-- Username -->
    <div class="flex flex-col gap-1.5">
      <label class="text-xs font-medium text-slate-400">Nom d'utilisateur</label>
      <div
        class="flex items-center gap-2.5 px-3.5 rounded-xl border bg-slate-800/50 transition-all duration-200"
        :class="isFocused
          ? 'border-cyan-500/50 shadow-[0_0_0_3px_rgba(6,182,212,0.08)]'
          : 'border-white/10 hover:border-white/20'"
      >
        <svg class="w-4 h-4 shrink-0 transition-colors" :class="isFocused ? 'text-cyan-400/70' : 'text-slate-500'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
        </svg>
        <input id="edit-username"
          v-model="localUsername"
          type="text"
          placeholder="john_doe"
          autocomplete="username"
          class="flex-1 bg-transparent border-none outline-none text-white text-sm placeholder:text-slate-600 py-3 caret-cyan-400"
          @focus="isFocused = true"
          @blur="isFocused = false"
        />
      </div>
      <p v-if="usernameError" class="text-xs text-red-400">{{ usernameError }}</p>
    </div>

    <!-- Email (read-only) -->
    <div class="flex flex-col gap-1.5">
      <label class="text-xs font-medium text-slate-400 flex items-center gap-1.5">
        Adresse email
        <span class="text-[10px] px-1.5 py-0.5 rounded-md bg-slate-700 text-slate-500 border border-white/10">Non modifiable</span>
      </label>
      <div class="flex items-center gap-2.5 px-3.5 rounded-xl border border-white/5 bg-slate-900/50">
        <svg class="w-4 h-4 shrink-0 text-slate-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/>
        </svg>
        <span class="flex-1 text-sm text-slate-500 py-3 select-none">{{ email }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { UserRole } from '../../types/user.types'

const props = defineProps<{
  username: string
  email: string
  role: UserRole
}>()

const emit = defineEmits<{
  'update:username': [value: string]
}>()

const localUsername = ref(props.username)
const isFocused = ref(false)
const usernameError = ref('')

watch(localUsername, (val) => {
  usernameError.value = val.trim().length < 3 && val.trim().length > 0 ? 'Min. 3 caractères' : ''
  emit('update:username', val)
})

watch(() => props.username, (val) => { localUsername.value = val })
</script>