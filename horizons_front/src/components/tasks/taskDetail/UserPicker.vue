<template>
  <div class="relative" ref="rootRef">
    <button
      @click="toggle"
      class="flex items-center gap-2 hover:bg-white/5 rounded-lg px-1.5 py-1 transition-colors"
    >
      <template v-if="value">
        <div
          class="w-6 h-6 rounded-lg shrink-0 overflow-hidden ring-1 ring-white/10"
          :style="{ background: value.color + '33' }"
        >
          <img v-if="value.avatar_url" :src="value.avatar_url" class="w-full h-full object-cover" />
          <div v-else class="w-full h-full flex items-center justify-center text-[10px] font-semibold"
            :style="{ color: value.color }">{{ value.initials }}</div>
        </div>
        <span class="text-xs text-white font-medium">{{ value.username }}</span>
      </template>
      <span v-else class="text-xs text-slate-500 italic">Non assigné</span>
    </button>

    <Teleport to="body">
      <div
        v-if="open"
        class="fixed z-9999 bg-slate-800 border border-white/10 rounded-xl shadow-2xl p-1.5 min-w-44"
        :style="dropdownPos"
        @mousedown.stop
      >
        <div
          class="flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer text-slate-500 hover:bg-white/5 text-xs italic mb-0.5"
          @click="select(null)"
        >Retirer</div>

        <div
          v-for="u in users" :key="u.id"
          class="flex items-center gap-2.5 px-3 py-2 rounded-lg cursor-pointer transition-colors"
          :class="u.id === disabledId ? 'opacity-30 cursor-not-allowed' : 'hover:bg-white/8'"
          @click="u.id !== disabledId && select(u)"
        >
          <div class="w-7 h-7 rounded-lg shrink-0 overflow-hidden" :style="{ background: u.color + '33' }">
            <img v-if="u.avatar_url" :src="u.avatar_url" class="w-full h-full object-cover" />
            <div v-else class="w-full h-full flex items-center justify-center text-xs font-semibold"
              :style="{ color: u.color }">{{ u.initials }}</div>
          </div>
          <span class="text-sm text-white">{{ u.username }}</span>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, onUnmounted } from 'vue'
import type { User } from '../../../types/task.types'

const props = defineProps<{
  users: User[]
  value?: User
  disabledId?: string
}>()

const emit = defineEmits<{ select: [user: User | null] }>()

const open        = ref(false)
const rootRef     = ref<HTMLElement | null>(null)
const dropdownPos = ref({ top: '0px', left: '0px' })

const updatePos = () => {
  if (!rootRef.value) return
  const r = rootRef.value.getBoundingClientRect()
  dropdownPos.value = {
    top:  `${r.bottom + 6}px`,
    left: `${r.left}px`,
  }
}

const toggle = () => {
  if (!open.value) updatePos()
  open.value = !open.value
}

const select = (u: User | null) => {
  emit('select', u)
  open.value = false
}

const handleClickOutside = (e: MouseEvent) => {
  if (!open.value) return
  if (rootRef.value?.contains(e.target as Node)) return
  open.value = false
}

document.addEventListener('mousedown', handleClickOutside)
onUnmounted(() => document.removeEventListener('mousedown', handleClickOutside))
</script>