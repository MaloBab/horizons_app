<template>
  <div
    class="interactive group relative bg-slate-800/50 backdrop-blur-sm hover:bg-slate-800 border border-white/10 hover:border-white/20 rounded-xl p-4 cursor-pointer select-none transition-all duration-200 hover:shadow-md"
    :class="selected && 'border-red-500/30 bg-red-500/5'"
    @click="emit('click', task)"
  >
    <!-- Priority accent bar -->
    <div
      class="absolute left-0 top-3 bottom-3 w-0.5 rounded-r-full"
      :class="{
        'bg-slate-500':  task.priority === 'low',
        'bg-blue-400':   task.priority === 'medium',
        'bg-amber-400':  task.priority === 'high',
        'bg-red-400':    task.priority === 'critical',
      }"
    />

    <!-- Selection checkbox — top-right, closed tasks only -->
    <button
      v-if="selectable"
      @click.stop="emit('toggleSelect', task.id)"
      class="absolute top-2.5 right-2.5 z-10 w-5 h-5 rounded-md border-2 flex items-center justify-center transition-all duration-150"
      :class="selected
        ? 'bg-red-500/25 border-red-400 opacity-100'
        : 'bg-slate-900/80 border-white/20 opacity-0 group-hover:opacity-100 hover:border-red-400/60'"
    >
      <Check v-if="selected" class="w-3 h-3 text-red-300" />
    </button>

    <!-- Top row: priority + type badge (with right padding when selectable) -->
    <div class="flex items-center justify-between mb-2.5 pl-3" :class="selectable ? 'pr-7' : ''">
      <PriorityBadge :priority="task.priority" show-label :icon-size="13" />
      <span
        v-if="task.type === 'needs_review'"
        class="text-[10px] font-medium px-1.5 py-0.5 rounded-md bg-violet-500/15 text-violet-300 border border-violet-500/25"
      >Vérification</span>
    </div>

    <!-- Title -->
    <p class="text-2xl font-medium text-white leading-snug mb-3 pl-3 line-clamp-2" style="font-family: 'Instrument Serif', serif">
      {{ task.title }}
    </p>

    <!-- Tags -->
    <div v-if="task.tags.length" class="flex flex-wrap gap-1.5 mb-3 pl-3">
      <TagChip v-for="tag in task.tags.slice(0, 3)" :key="tag.id" :tag="tag" />
      <span v-if="task.tags.length > 3" class="text-xs text-slate-500 self-center">+{{ task.tags.length - 3 }}</span>
    </div>

    <!-- Subtasks progress -->
    <div v-if="task.subtasks.length" class="mb-3 pl-3">
      <div class="h-1 bg-slate-700 rounded-full overflow-hidden">
        <div
          class="h-full rounded-full transition-all duration-500"
          :class="progress === 100 ? 'bg-emerald-400' : 'bg-cyan-500'"
          :style="{ width: `${progress}%` }"
        />
      </div>
      <span class="text-xs text-slate-500 mt-1 block">{{ done }}/{{ task.subtasks.length }} sous-tâches</span>
    </div>

    <!-- Footer: assignee + due date -->
    <div class="flex items-center justify-between pl-3">
      <div v-if="task.assignee" class="flex items-center gap-2">
        <div
          class="w-6 h-6 rounded-lg flex items-center justify-center text-[10px] font-semibold shrink-0 overflow-hidden transition-transform duration-150 group-hover:scale-105"
          :style="{ background: task.assignee.color + '33', color: task.assignee.color }"
        >
          <img v-if="task.assignee.avatar_url" :src="task.assignee.avatar_url" :alt="task.assignee.username" class="w-full h-full object-cover" />
          <span v-else>{{ task.assignee.initials }}</span>
        </div>
        <span class="text-xs text-slate-400">{{ task.assignee.username }}</span>
      </div>
      <div v-else class="w-6 h-6 rounded-lg border border-dashed border-white/15" />

      <div v-if="task.due_date" class="flex items-center gap-1.5" :class="isOverdue && task.status != 'closed'  ? 'text-red-400' : 'text-slate-500'">
        <Calendar class="w-3 h-3" />
        <span class="text-xs">{{ fmt(task.due_date) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Calendar, Check } from 'lucide-vue-next'
import type { Task } from '../../types/task.types'
import PriorityBadge from './PriorityBadge.vue'
import TagChip from './tags/TagChip.vue'

const props = defineProps<{
  task:       Task
  selectable?: boolean 
  selected?:  boolean  
}>()

const emit = defineEmits<{
  click:        [task: Task]
  toggleSelect: [id: string]
}>()

const done      = computed(() => props.task.subtasks.filter(s => s.completed).length)
const progress  = computed(() => props.task.subtasks.length ? Math.round(done.value / props.task.subtasks.length * 100) : 0)

const isOverdue = computed(() => {
  if (!props.task.due_date) return false
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return new Date(props.task.due_date) < today
})

const fmt = (iso: string) => new Date(iso).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })
</script>