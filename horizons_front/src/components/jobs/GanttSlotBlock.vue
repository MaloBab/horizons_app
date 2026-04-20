<template>
<div
  class="gantt-block group relative flex items-center justify-center rounded-lg cursor-pointer select-none transition-all duration-200 hover:scale-y-105 hover:z-20 hover:shadow-lg"
  :style="{ ...blockStyle, ...blockColor }"
    ref="blockRef"
    @click="$emit('click', job)"
    @mouseenter="showTooltip"
    @mouseleave="hideTooltip"
    :title="`${job.name} — ${slot.start_time}h→${slot.end_time}h (${job.required_volunteers} bénévoles requis)`"
  >
    <!-- Volunteer count badge -->
    <div class="flex items-center gap-1.5 px-2">
      <span class="text-xs font-bold text-white drop-shadow">
        {{ job.required_volunteers }}
      </span>
      <Users class="w-3 h-3 text-white/80 shrink-0" />
    </div>

    <!-- Teleported tooltip -->
    <Teleport to="body">
      <Transition name="tooltip">
        <div
          v-if="tooltipVisible"
          class="fixed z-9999 pointer-events-none"
          :style="tooltipStyle"
        >
          <div class="bg-slate-900 border border-white/20 rounded-lg px-3 py-2 shadow-xl whitespace-nowrap">
            <p class="text-xs font-semibold text-white">{{ job.name }}</p>
            <p class="text-xs text-slate-400 mt-0.5">
              {{ slot.start_time >= 24 ? slot.start_time - 24 : slot.start_time }}h → {{ slot.end_time >= 24 ? slot.end_time - 24 : slot.end_time }}h
              · {{ job.required_volunteers }} bénévoles
            </p>
            <p class="text-xs text-cyan-400 mt-0.5">{{ recruitmentType }}</p>
          </div>
          <!-- Arrow -->
          <div class="w-2 h-2 bg-slate-900 border-r border-b border-white/20 rotate-45 mx-auto -mt-1"></div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Users } from 'lucide-vue-next'
import type { Job, Slot } from '../../types/planning.types'

interface Props {
  job: Job
  slot: Slot
  columnWidth: number
  recruitmentType: 'Normal' | 'Specialise'
  categoryId: number
}

const props = defineProps<Props>()
defineEmits<{ click: [job: Job] }>()

const blockRef = ref<HTMLElement | null>(null)
const tooltipVisible = ref(false)
const tooltipStyle = ref<Record<string, string>>({})

const showTooltip = () => {
  if (!blockRef.value) return
  const rect = blockRef.value.getBoundingClientRect()
  tooltipStyle.value = {
    top:  `${rect.top - 8}px`,         
    left: `${rect.left + rect.width / 2}px`,
    transform: 'translate(-50%, -100%)',
  }
  tooltipVisible.value = true
}

const hideTooltip = () => {
  tooltipVisible.value = false
}

const durationHours = computed(() => {
  const start = props.slot.start_time > 23 ? props.slot.start_time - 24 : props.slot.start_time
  const end   = props.slot.end_time   > 23 ? props.slot.end_time   - 24 : props.slot.end_time
  return end > start ? end - start : 24 - start + end
})

const blockStyle = computed(() => ({
  width: `${durationHours.value * props.columnWidth - 4}px`,
  height: '32px',
}))


const blockColor = computed(() => {
  const hue = (props.categoryId * 137.508) % 360
  return {
    background: `hsla(${hue}, 70%, 60%, 0.80)`,
    boxShadow:  `0 2px 8px hsla(${hue}, 70%, 60%, 0.25)`,
  }
})

</script>

<style scoped>
.tooltip-enter-active,
.tooltip-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.tooltip-enter-from,
.tooltip-leave-to {
  opacity: 0;
  transform: translate(-50%, calc(-100% + 4px));
}
</style>