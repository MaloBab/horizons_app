<template>
  <div class="flex flex-col rounded-xl border border-white/10 bg-slate-800/50 transition-all duration-200">
    <!-- Header -->
    <div class="flex items-center justify-between px-4 py-3.5 border-b border-white/10">
      <div class="flex items-center gap-2.5">
        <div class="w-2 h-2 rounded-full shrink-0" :style="{ background: color }" />
        <span class="text-sm font-semibold text-white">{{ title }}</span>
        <span class="text-xs px-2 py-0.5 rounded-full bg-white/5 text-slate-400 border border-white/10">{{ tasks.length }}</span>
      </div>

      <div class="flex items-center gap-1">
        <!-- Select all / deselect all — closed column only -->
        <button
          v-if="status === 'closed' && tasks.length > 0"
          @click="toggleSelectAll"
          class="w-7 h-7 rounded-lg flex items-center justify-center transition-all duration-150"
          :class="allSelected
            ? 'text-red-400 bg-red-500/10 hover:bg-red-500/20'
            : 'text-slate-500 hover:text-slate-300 hover:bg-white/10'"
          :title="allSelected ? 'Tout désélectionner' : 'Tout sélectionner'"
        >
          <CheckSquare v-if="allSelected" class="w-4 h-4" />
          <Square v-else class="w-4 h-4" />
        </button>

        <!-- Add task — open column only -->
        <button
          v-if="status === 'open'"
          @click="emit('add')"
          class="w-7 h-7 rounded-lg flex items-center justify-center text-slate-500 hover:text-cyan-400 hover:bg-cyan-500/10 transition-all duration-150"
          title="Nouvelle tâche"
        ><Plus class="w-4 h-4" /></button>
      </div>
    </div>

    <!-- Cards -->
    <div class="flex flex-col gap-2 p-3 flex-1">
      <TaskCard
        v-for="task in sortedTasks"
        :key="task.id"
        :task="task"
        :selectable="status === 'closed'"
        :selected="selectedIds?.has(task.id)"
        @click="emit('open', task)"
        @toggle-select="emit('toggleSelect', $event)"
      />

      <div v-if="tasks.length === 0" class="flex flex-col items-center justify-center py-10 gap-2">
        <component :is="emptyIcon" class="w-6 h-6 text-slate-600" />
        <span class="text-xs text-slate-500">Aucune tâche</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Plus, Inbox, Eye, CheckCheck, Square, CheckSquare } from 'lucide-vue-next'
import type { Task, TaskStatus } from '../../types/task.types'
import TaskCard from './TaskCard.vue'

const PRIORITY_ORDER: Record<string, number> = { critical: 0, high: 1, medium: 2, low: 3 }

const props = defineProps<{
  title:        string
  status:       TaskStatus
  color:        string
  tasks:        Task[]
  selectedIds?: Set<string>
}>()

const emit = defineEmits<{
  add:          []
  open:         [task: Task]
  toggleSelect: [id: string]
}>()

const sortedTasks = computed(() =>
  [...props.tasks].sort((a, b) => (PRIORITY_ORDER[a.priority] ?? 99) - (PRIORITY_ORDER[b.priority] ?? 99))
)

const emptyIcon = computed(() => ({ open: Inbox, review: Eye, closed: CheckCheck }[props.status]))

const allSelected = computed(() =>
  props.tasks.length > 0 && props.tasks.every(t => props.selectedIds?.has(t.id))
)

const toggleSelectAll = () => {
  if (allSelected.value) {
    props.tasks.forEach(t => { if (props.selectedIds?.has(t.id))  emit('toggleSelect', t.id) })
  } else {
    props.tasks.forEach(t => { if (!props.selectedIds?.has(t.id)) emit('toggleSelect', t.id) })
  }
}
</script>