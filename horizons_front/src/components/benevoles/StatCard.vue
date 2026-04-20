<template>
  <div
    class="stat-card group relative overflow-hidden rounded-xl border bg-slate-950/80 backdrop-blur-md transition-all duration-300 hover:-translate-y-0.5 hover:scale-[1.02]"
    :class="borderClass"
  >
    <StatCardBackground :color="color" />

    <div class="relative z-10 flex items-center justify-between px-4 py-3">
      <div class="flex flex-col gap-0.5">
        <p class="text-[11px] font-medium uppercase tracking-widest text-slate-300">{{ title }}</p>
        <div class="flex items-end gap-1.5">
          <p class="text-2xl font-bold leading-none" :class="valueClass">{{ value }}</p>
          <span v-if="suffix" class="mb-0.5 text-xs text-slate-300">{{ suffix }}</span>
        </div>
        <p v-if="sub" class="text-[11px] text-slate-300">{{ sub }}</p>
      </div>
      <div
        class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border transition-all duration-300 group-hover:scale-110"
        :class="iconClass"
      >
        <component :is="iconComponent" class="h-5 w-5" :class="valueClass" />
      </div>
    </div>

    <div v-if="progress !== undefined" class="relative z-10 px-4 pb-3">
      <div class="h-0.5 w-full overflow-hidden rounded-full bg-white/5">
        <div class="h-full rounded-full transition-all duration-700" :class="progressClass" :style="{ width: `${progress}%` }" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Users, Calendar, Heart } from 'lucide-vue-next'
import StatCardBackground from '../style/StatCardBackground.vue'

interface Props {
  title: string; value: string
  icon: 'users' | 'calendar' | 'heart'
  color: 'cyan' | 'purple' | 'pink'
  suffix?: string; sub?: string; progress?: number
}
const props = defineProps<Props>()

const iconComponent = computed(() => ({ users: Users, calendar: Calendar, heart: Heart }[props.icon]))

const borderClass = computed(() => ({
  cyan:   'border-cyan-500/15   hover:border-cyan-500/35   hover:shadow-[0_0_24px_rgba(34,211,238,0.1)]',
  purple: 'border-purple-500/15 hover:border-purple-500/35 hover:shadow-[0_0_24px_rgba(168,85,247,0.1)]',
  pink:   'border-pink-500/15   hover:border-pink-500/35   hover:shadow-[0_0_24px_rgba(236,72,153,0.1)]',
}[props.color]))

const valueClass = computed(() => ({
  cyan: 'text-cyan-400', purple: 'text-purple-400', pink: 'text-pink-400',
}[props.color]))

const iconClass = computed(() => ({
  cyan:   'border-cyan-500/20   bg-cyan-500/8   group-hover:border-cyan-500/40   group-hover:bg-cyan-500/15',
  purple: 'border-purple-500/20 bg-purple-500/8 group-hover:border-purple-500/40 group-hover:bg-purple-500/15',
  pink:   'border-pink-500/20   bg-pink-500/8   group-hover:border-pink-500/40   group-hover:bg-pink-500/15',
}[props.color]))

const progressClass = computed(() => ({
  cyan:   'bg-gradient-to-r from-cyan-500 to-blue-500',
  purple: 'bg-gradient-to-r from-purple-500 to-pink-500',
  pink:   'bg-gradient-to-r from-pink-500 to-rose-500',
}[props.color]))
</script>