<template>
  <Transition
    enter-active-class="transition-all duration-300 ease-out"
    enter-from-class="opacity-0 -translate-y-1"
    leave-active-class="transition-all duration-200 ease-in"
    leave-to-class="opacity-0"
  >
    <div v-if="password" class="flex items-center gap-2.5 mt-2">
      <div class="flex gap-1 flex-1">
        <div
          v-for="i in 4"
          :key="i"
          class="h-0.75 flex-1 rounded-full transition-all duration-400"
          :style="i <= strength.score
            ? { background: strength.color }
            : { background: 'rgba(255,255,255,0.08)' }"
        />
      </div>
      <span
        class="text-xs font-medium min-w-8 text-right transition-all duration-300"
        :style="{ color: strength.color }"
      >
        {{ strength.label }}
      </span>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { PasswordStrength } from '../../types/auth.types'

const props = defineProps<{ password: string }>()

const strength = computed<PasswordStrength>(() => {
  const pwd = props.password
  if (!pwd) return { score: 0, label: '', color: '' }
  let score = 0
  if (pwd.length >= 8) score++
  if (/[A-Z]/.test(pwd)) score++
  if (/[0-9]/.test(pwd)) score++
  if (/[^A-Za-z0-9]/.test(pwd)) score++

  const levels: PasswordStrength[] = [
    { score: 0, label: '', color: '' },
    { score: 1, label: 'Faible', color: '#ef4444' },
    { score: 2, label: 'Moyen', color: '#f59e0b' },
    { score: 3, label: 'Bon', color: '#3b82f6' },
    { score: 4, label: 'Fort', color: '#10b981' },
  ]
  return levels[score] || { score: 0, label: '', color: '' }
})
</script>