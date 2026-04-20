<template>
  <div>
    <!-- Progress -->
    <div v-if="subtasks.length" class="mb-4">
      <div class="flex items-center justify-between mb-2">
        <span class="text-xs text-slate-400">{{ done }}/{{ subtasks.length }} terminées</span>
        <span class="text-xs font-medium" :class="progress === 100 ? 'text-emerald-400' : 'text-slate-400'">{{ progress }}%</span>
      </div>
      <div class="h-1.5 bg-slate-700 rounded-full overflow-hidden">
        <div
          class="h-full rounded-full transition-all duration-500 ease-out"
          :class="progress === 100 ? 'bg-emerald-400' : 'bg-cyan-500'"
          :style="{ width: `${progress}%` }"
        />
      </div>
    </div>

    <!-- List -->
    <div class="flex flex-col gap-0.5">
      <div
        v-for="(sub, index) in localSubtasks" :key="sub.id"
        draggable="true"
        class="group flex items-center gap-2 py-2 rounded-lg transition-colors select-none"
        :class="[
          dragOverIndex === index ? 'bg-white/10 border border-dashed border-cyan-500/40' : 'hover:bg-white/5 border border-transparent',
          draggingIndex === index ? 'opacity-40' : 'opacity-100',
        ]"
        @dragstart="onDragStart(index, $event)"
        @dragend="onDragEnd"
        @dragover.prevent="onDragOver(index)"
        @dragleave="onDragLeave"
        @drop.prevent="onDrop(index)"
      >
        <!-- Drag handle -->
        <span
          class="shrink-0 cursor-grab active:cursor-grabbing text-slate-600 transition-opacity"
          title="Réordonner"
        >
          <GripVertical class="w-3.5 h-3.5" />
        </span>

        <button
          class="w-4 h-4 rounded border shrink-0 flex items-center justify-center transition-all duration-150"
          :class="sub.completed ? 'bg-emerald-500/20 border-emerald-500/40' : 'border-white/20 hover:border-white/40'"
          @click="emit('toggle', sub.id)"
        ><Check v-if="sub.completed" class="w-2.5 h-2.5 text-emerald-400" /></button>

        <span
          class="text-sm flex-1 transition-all duration-150"
          :class="sub.completed ? 'text-slate-500 line-through' : 'text-slate-300'"
        >{{ sub.title }}</span>

        <button
          class="opacity-0 pr-1 group-hover:opacity-100 text-slate-600 hover:text-red-400 transition-all"
          @click="emit('delete', sub.id)"
        ><X class="w-3.5 h-3.5" /></button>
      </div>
    </div>

    <!-- Add row -->
    <div class="mt-2 flex items-center gap-3 px-3 py-2 border border-dashed border-white/10 rounded-lg hover:border-white/20 transition-colors">
      <div class="w-4 h-4 rounded border border-dashed border-white/20 shrink-0" />
      <input id="add-subtask"
        v-model="newTitle" type="text" placeholder="Ajouter une sous-tâche..."
        class="flex-1 bg-transparent text-sm text-slate-300 placeholder-slate-600 outline-none"
        @keydown.enter="add" @keydown.escape="newTitle = ''"
      />
      <button v-if="newTitle.trim()" @click="add" class="text-xs text-cyan-400 hover:text-cyan-300 transition-colors font-medium">↵ Ajouter</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Check, X, GripVertical } from 'lucide-vue-next'
import type { SubTask } from '../../types/task.types'

const props = defineProps<{ subtasks: SubTask[] }>()
const emit = defineEmits<{
  toggle: [id: number]
  delete: [id: number]
  add: [title: string]
  reorder: [subtasks: SubTask[]]
}>()

const localSubtasks = ref<SubTask[]>([...props.subtasks])

watch(() => props.subtasks, (val) => {
  localSubtasks.value = [...val]
}, { deep: true })

const newTitle = ref('')
const done = computed(() => localSubtasks.value.filter(s => s.completed).length)
const progress = computed(() => localSubtasks.value.length ? Math.round(done.value / localSubtasks.value.length * 100) : 0)

const add = () => {
  if (newTitle.value.trim()) { emit('add', newTitle.value.trim()); newTitle.value = '' }
}

// ── Drag & drop state ──────────────────────────────────────────────────────
const draggingIndex = ref<number | null>(null)
const dragOverIndex = ref<number | null>(null)

const onDragStart = (index: number, event: DragEvent) => {
  draggingIndex.value = index
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move'
    // Required for Firefox
    event.dataTransfer.setData('text/plain', String(index))
  }
}

const onDragEnd = () => {
  draggingIndex.value = null
  dragOverIndex.value = null
}

const onDragOver = (index: number) => {
  if (draggingIndex.value !== null && draggingIndex.value !== index) {
    dragOverIndex.value = index
  }
}

const onDragLeave = () => {
  dragOverIndex.value = null
}

const onDrop = (toIndex: number) => {
  if (draggingIndex.value === null || draggingIndex.value === toIndex) return

  const updated = [...localSubtasks.value]
  const [moved] = updated.splice(draggingIndex.value, 1)
  updated.splice(toIndex, 0, moved!)

  localSubtasks.value = updated
  emit('reorder', updated)

  draggingIndex.value = null
  dragOverIndex.value = null
}
</script>