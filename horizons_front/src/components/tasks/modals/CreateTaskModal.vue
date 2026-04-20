<template>
  <Transition name="modal">
    <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/70 backdrop-blur-sm" />

      <div class="relative z-10 w-full max-w-2xl bg-slate-900 border border-white/10 rounded-2xl shadow-2xl overflow-hidden flex flex-col">

        <!-- Header -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-white/10 shrink-0">
          <h2 class="text-lg font-semibold text-white" style="font-family: 'Instrument Serif', serif">Nouvelle tâche</h2>
          <button @click="emit('close')" class="p-2 rounded-lg text-slate-500 hover:text-white hover:bg-white/10 transition-all">
            <X class="w-4 h-4" />
          </button>
        </div>

        <!-- Form — scroll container -->
        <div class="flex flex-col gap-5 px-6 py-5 overflow-y-auto max-h-[75vh] custom-scrollbar">

          <!-- Title -->
          <div>
            <input id="add-task-title"
              v-model="form.title" type="text" placeholder="Titre de la tâche..."
              class="w-full bg-transparent text-xl font-semibold text-white placeholder-slate-600 outline-none border-b-2 border-white/10 pb-2 focus:border-cyan-500/50 transition-colors"
              style="font-family: 'Instrument Serif', serif"
              autofocus
            />
          </div>

          <!-- Description -->
          <div>
            <label class="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">Description</label>
            <TextEditorView v-model="form.description" />
          </div>

          <!-- Type + Priority -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">Type</label>
              <div class="flex gap-2">
                <button v-for="t in types" :key="t.value" @click="form.type = t.value"
                  class="flex-1 px-3 py-2 rounded-xl text-sm font-medium border transition-all"
                  :class="form.type === t.value ? t.active : 'border-white/10 text-slate-400 hover:border-white/20 hover:text-white'"
                >{{ t.label }}</button>
              </div>
            </div>
            <div>
              <label class="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">Priorité</label>
              <div class="flex gap-1.5 flex-wrap">
                <button v-for="p in priorities" :key="p.value" @click="form.priority = p.value"
                  class="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium border transition-all"
                  :class="form.priority === p.value ? p.active : 'border-white/10 text-slate-400 hover:border-white/20 hover:text-white'"
                >
                  <component :is="p.icon" class="w-3 h-3" />{{ p.label }}
                </button>
              </div>
            </div>
          </div>

          <!-- Tags + Due date -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">Tags</label>

              <div v-if="tagsLoading" class="flex items-center gap-2 text-xs text-slate-500 py-1">
                <div class="w-3 h-3 rounded-full border-2 border-cyan-500/40 border-t-cyan-400 animate-spin" />
                Chargement…
              </div>

              <div v-else class="flex flex-wrap gap-1.5">
                <button
                  v-for="tag in tags" :key="tag.id"
                  @click="toggleTag(tag)"
                  class="px-2.5 py-1 rounded-lg text-xs font-medium border transition-all"
                  :style="form.tags.some(t => t.id === tag.id)
                    ? { background: tag.color + '22', borderColor: tag.color + '44', color: tag.color }
                    : { background: 'transparent', borderColor: 'rgba(255,255,255,0.10)', color: 'rgb(148,163,184)' }"
                >{{ tag.name }}</button>

                <!-- Inline tag creator -->
                <div class="flex items-center gap-1.5 px-2 py-1 rounded-lg border border-dashed border-white/15">
                  <input id="add-inline-tag"
                    v-model="newTagName" type="text" placeholder="Nouveau…"
                    class="bg-transparent text-xs text-slate-300 placeholder-slate-600 outline-none w-20"
                    @keydown.enter.prevent="submitNewTag"
                  />
                  <input id="color-input1" type="color" v-model="newTagColor"
                    class="w-4 h-4 rounded cursor-pointer bg-transparent border-0 p-0 shrink-0"
                  />
                  <button v-if="newTagName.trim()" @click="submitNewTag"
                    class="text-xs text-cyan-400 hover:text-cyan-300 font-medium transition-colors">↵</button>
                </div>
              </div>
            </div>

            <div>
              <label class="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">Date limite</label>
              <input id="date-input1" type="date" v-model="form.due_date" style="color-scheme: dark;"
                class="w-full bg-slate-800/50 border border-white/10 rounded-xl px-3 py-2 text-sm text-slate-300 outline-none focus:border-cyan-500/50 transition-colors"
              />
            </div>
          </div>

          <!-- Sous-tâches -->
          <div>
            <label class="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">Sous-tâches</label>
            <div class="bg-slate-800/80 border border-white/10 rounded-xl p-3">
              <SubtaskList
                :subtasks="form.subtasks"
                @toggle="toggleSubtask"
                @delete="deleteSubtask"
                @add="addSubtask"
                @reorder="reorderSubtasks"
              />
            </div>
          </div>

          <!-- Assignee -->
          <div>
            <label class="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">Assigné</label>
            <div v-if="usersLoading" class="flex items-center gap-2 text-xs text-slate-500 py-2">
              <div class="w-3 h-3 rounded-full border-2 border-cyan-500/40 border-t-cyan-400 animate-spin" />
              Chargement des utilisateurs…
            </div>
            <div v-else class="flex gap-2 flex-wrap">
              <button
                v-for="u in users" :key="u.id"
                @click="form.assignee = form.assignee?.id === u.id ? undefined : u"
                class="flex items-center gap-2 px-3 py-2 rounded-xl border transition-all text-sm"
                :class="form.assignee?.id === u.id
                  ? 'border-white/20 bg-white/8 text-white'
                  : 'border-white/10 text-slate-400 hover:border-white/20 hover:text-white'"
              >
                <div class="w-6 h-6 rounded-lg flex items-center justify-center text-xs font-semibold shrink-0 overflow-hidden"
                  :style="{ background: u.color + '33', color: u.color }">
                  <img v-if="u.avatar_url" :src="u.avatar_url" class="w-full h-full object-cover" />
                  <span v-else>{{ u.initials }}</span>
                </div>
                {{ u.username }}
              </button>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="flex items-center justify-end gap-3 px-6 py-4 border-t border-white/10 shrink-0">
          <button @click="emit('close')" class="px-4 py-2 rounded-xl text-sm text-slate-400 hover:text-white transition-colors">Annuler</button>
          <button
            @click="submit"
            :disabled="!form.title.trim()"
            class="px-5 py-2 rounded-xl text-sm font-medium bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 hover:bg-cyan-500/25 transition-all disabled:opacity-30 disabled:cursor-not-allowed"
          >Créer la tâche</button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted, onUnmounted } from 'vue'
import { X, ArrowDown, Minus, ArrowUp, Zap } from 'lucide-vue-next'
import type { Task, Tag, TaskStatus, TaskPriority, TaskType, User, SubTask } from '../../../types/task.types'
import { useUsers } from '../../../composables/useUsers'
import { useTags } from '../../../composables/useTags'
import TextEditorView from '../richTextEditor/TextEditorView.vue'
import SubtaskList from '../SubtaskList.vue'
import { useActivityLogger } from '../../../composables/Activity/useActivityLogger'

const { taskCreated } = useActivityLogger()
const props = defineProps<{ open: boolean}>()
const emit  = defineEmits<{ close: []; create: [task: Omit<Task, 'id' | 'created_at' | 'comments'>] }>()

const { users, isLoading: usersLoading } = useUsers()
const { tags, isLoading: tagsLoading, fetchTags, createTag } = useTags()

const newTagName  = ref('')
const newTagColor = ref('#22d3ee')

const submitNewTag = async () => {
  if (!newTagName.value.trim()) return
  const created = await createTag(newTagName.value.trim(), newTagColor.value)
  if (created) {
    form.tags.push(created)
    newTagName.value = ''
    newTagColor.value = '#22d3ee'
  }
}

interface TaskForm {
  title: string
  description: string
  status: TaskStatus
  priority: TaskPriority
  type: TaskType
  assignee: User | undefined
  tags: Tag[]
  due_date: string
  subtasks: SubTask[]
}

const reorderSubtasks = (reorderedSubtasks: SubTask[]) => {
  form.subtasks = reorderedSubtasks
}

const defaultForm = (): TaskForm => ({
  title: '', description: '', status: 'open', priority: 'medium',
  type: 'standard', assignee: undefined, tags: [], due_date: '', subtasks: [],
})
const form = reactive<TaskForm>(defaultForm())

// Lock body scroll when modal is open
watch(() => props.open, (v) => {
  document.body.style.overflow = v ? 'hidden' : ''
})
onUnmounted(() => {
  document.body.style.overflow = ''
})

watch(() => props.open, v => { if (v) Object.assign(form, defaultForm()) })

onMounted(() => fetchTags())

const types = [
  { value: 'standard'     as const, label: 'Standard',     active: 'border-slate-500/40 bg-slate-500/10 text-slate-300' },
  { value: 'needs_review' as const, label: 'Vérification', active: 'border-violet-500/40 bg-violet-500/10 text-violet-300' },
]
const priorities = [
  { value: 'low'      as const, label: 'Basse',    icon: ArrowDown, active: 'border-slate-500/40 bg-slate-500/10 text-slate-300' },
  { value: 'medium'   as const, label: 'Moyenne',  icon: Minus,     active: 'border-blue-500/40 bg-blue-500/10 text-blue-300' },
  { value: 'high'     as const, label: 'Haute',    icon: ArrowUp,   active: 'border-amber-500/40 bg-amber-500/10 text-amber-300' },
  { value: 'critical' as const, label: 'Critique', icon: Zap,       active: 'border-red-500/40 bg-red-500/10 text-red-300' },
]

const toggleTag = (tag: Tag) => {
  const idx = form.tags.findIndex(t => t.id === tag.id)
  if (idx === -1) form.tags.push(tag); else form.tags.splice(idx, 1)
}

let nextSubId = -1
const toggleSubtask = (id: number) => {
  const s = form.subtasks.find(x => x.id === id)
  if (s) s.completed = !s.completed
}
const deleteSubtask = (id: number) => {
  const idx = form.subtasks.findIndex(x => x.id === id)
  if (idx !== -1) form.subtasks.splice(idx, 1)
}
const addSubtask = (title: string) => {
  form.subtasks.push({ id: nextSubId--, title, completed: false, order: form.subtasks.length })
}

const submit = () => {
  if (!form.title.trim()) return
  emit('create', { ...form, due_date: form.due_date || undefined })
  taskCreated(form.title)
  emit('close')
}
</script>

<style scoped>
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s ease; }
.modal-enter-from,   .modal-leave-to     { opacity: 0; }
.modal-enter-active .relative, .modal-leave-active .relative { transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1); }
.modal-enter-from   .relative, .modal-leave-to   .relative   { transform: scale(0.95) translateY(8px); }
</style>