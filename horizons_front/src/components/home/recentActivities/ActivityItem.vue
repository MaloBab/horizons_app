<template>
  <div
    class="relative flex items-center gap-3 px-4 py-3 border-b border-white/5 cursor-pointer transition-colors duration-200 hover:bg-cyan-500/4 group"
    @mouseenter="hovered = true"
    @mouseleave="hovered = false"
  >

    <div
      class="absolute left-0 top-0 bottom-0 w-0.5 rounded-full bg-linear-to-b from-transparent via-cyan-400 to-transparent transition-transform duration-300 ease-[cubic-bezier(0.34,1.56,0.64,1)] origin-center"
      :class="hovered ? 'scale-y-100' : 'scale-y-0'"
    />

    <div class="relative shrink-0 w-9 h-9 rounded-[10px] overflow-visible transition-transform duration-250 ease-[cubic-bezier(0.34,1.56,0.64,1)] group-hover:scale-110">
      <img
        v-if="activity.author.profile_picture_url"
        :src="activity.author.profile_picture_url"
        :alt="activity.author.username" 
        class="w-full h-full rounded-[10px] object-cover"
      />
      <div
        v-else
        class="w-full h-full rounded-[10px] flex items-center justify-center bg-linear-to-br from-cyan-800 to-indigo-500 text-[0.7rem] font-bold text-white font-mono"
      >
        {{ getInitials(activity.author.username) }}
      </div>
      <div
        class="absolute -inset-0.5 rounded-xl border pointer-events-none transition-all duration-200"
        :class="hovered ? 'border-cyan-400/40 shadow-[0_0_10px_rgba(34,211,238,0.15)]' : 'border-transparent'"
      />
    </div>

    <div class="flex-1 min-w-0">
      <p class="text-[0.82rem] leading-snug text-slate-300" v-html="formatTitle(activity.title)" />

      <div class="mt-1">
        <span class="text-[0.70rem] text-slate-500 font-mono">{{ activity.author.username }}</span>
      </div>
    </div>

    <div
      class="shrink-0 font-mono text-[0.72rem] text-cyan-400 tracking-wide transition-all duration-200"
      :class="hovered ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-1'"
    >
      {{ formatTimestamp(new Date(activity.created_at)) }}
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { Activity } from '../../../types/activity.types'
import { getInitials } from '../../../utils/stringUtils'
import { formatTitle, formatTimestamp } from '../../../composables/Activity/useActivityLogger'

const props = defineProps<{ activity: Activity; isLast?: boolean }>()

const hovered = ref(false)

</script>

<style scoped>

:deep(.task-chip) {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 1px 7px;
  border-radius: 6px;
  margin: 0 2px;
  font-size: 0.72rem;
  font-weight: 600;
  background: rgba(6, 182, 212, 0.1);
  color: #67e8f9;
  border: 1px solid rgba(6, 182, 212, 0.2);
}

:deep(.metric-pill) {
  display: inline-flex;
  flex-direction: row;
  align-items: baseline;
  gap: 5px;
  padding: 2px 8px;
  border-radius: 6px;
  margin: 0 2px;
  background: rgba(6, 182, 212, 0.1);
  border: 1px solid rgba(6, 182, 212, 0.2);
  vertical-align: middle;
}

:deep(.metric-pill__value) {
  font-family: 'Courier New', monospace;
  font-size: 0.78rem;
  font-weight: 700;
  color: #e2e8f0;
}

:deep(.metric-pill__label) {
  font-size: 0.68rem;
  font-weight: 500;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
</style>