<template>
  <Transition name="backdrop">
    <div v-if="task" class="fixed inset-0 z-50 flex items-stretch justify-end" @click.self="onClickOutside">
      <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="onClickOutside" />

      <Transition name="slideover">
        <div v-if="task"
          ref="panelRef"
          class="relative z-10 flex flex-col bg-slate-900 border-l border-white/10 shadow-2xl overflow-hidden"
          style="width: min(860px, 95vw)"
        >
          <TaskDetailHeader
            ref="headerRef"
            :task-id="task.id"
            :status="localTask.status"
            :task-type="localTask.type"
            :assignee="localTask.assignee"
            :can-close="canCloseFromReview"
            :is-saving="isSaving"
            :saved-at="savedAt"
            @cycle-status="cycleStatus"
            @close="emit('close')"
          />

          <TaskDetailMetaBar
            :users="users"
            :assignee="localTask.assignee"
            :priority="localTask.priority"
            :tags="localTask.tags ?? []"
            :available-tags="availableTags"
            :due-date="localTask.due_date"
            :task-type="localTask.type"
            :created-at="task.created_at"
            @assignee="onAssigneeChange"
            @priority="onPriorityChange"
            @add-tag="addTag"
            @remove-tag="removeTag"
            @new-tag="onNewTag"
            @type="onTypeChange"
            @due-date="onDueDateChange"
          />

          <div ref="scrollRef" class="flex-1 overflow-y-auto px-6 py-5 flex flex-col gap-5 custom-scrollbar">

            <div>
              <textarea
                v-if="editingTitle" ref="titleRef" v-model="localTitle" rows="2"
                class="w-full bg-transparent text-2xl font-semibold text-white outline-none resize-none leading-snug border-b-2 border-cyan-500/60 pb-1"
                style="font-family: 'Instrument Serif', serif"
                @blur="saveTitle" @keydown.enter.prevent="saveTitle" @keydown.escape="cancelTitle"
              />
              <h2 v-else
                class="text-2xl font-semibold text-white cursor-text hover:opacity-80 transition-opacity leading-snug"
                style="font-family: 'Instrument Serif', serif"
                @click="startEditTitle"
              >{{ task.title }}</h2>
              <p v-if="!editingTitle" class="text-xs text-slate-500 mt-1">Cliquer pour modifier</p>
            </div>

            <div class="flex items-center justify-between -mt-2 min-h-6">
              <div class="flex items-center gap-2">
                <template v-if="localTask.due_date && localTask.status !== 'closed'">
                  <CalendarDays class="w-3.5 h-3.5 shrink-0"
                    :class="isDueDatePast ? 'text-red-400' : 'text-slate-500'" />
                  <span class="text-xs" :class="isDueDatePast ? 'text-red-400 font-medium' : 'text-slate-400'">
                    {{ isDueDatePast ? 'En retard · ' : 'Échéance · ' }}{{ fmtDate(localTask.due_date) }}
                  </span>
                </template>
              </div>

              <AddToCalendarButton
                v-if="localTask.status !== 'closed'"
                :task-id="localTask.id"
                :is-exported="!!localTask.google_calendar_event_id"
                :task-title="task.title"
                :due-date="localTask.due_date"
              />
            </div>

            <DescriptionSection
              ref="descRef"
              :model-value="localTask.description"
              :task="task"
              @update:model-value="onDescSave"
              @editing-change="descEditing = $event"
            />

            <section class="bg-slate-800/50 border border-white/10 rounded-xl p-4">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Sous-tâches</h3>
                <span v-if="localSubtasks.length" class="text-xs text-slate-500">
                  {{ localSubtasks.filter(s => s.completed).length }}/{{ localSubtasks.length }}
                </span>
              </div>
              <SubtaskList
                :subtasks="localSubtasks"
                @toggle="toggleSubtask"
                @delete="deleteSubtask"
                @add="addSubtask"
                @reorder="handleReorder"
              />
            </section>

            <section class="bg-slate-800/50 border border-white/10 rounded-xl p-4">
              <div class="flex items-center gap-2 mb-4">
                <h3 class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Commentaires</h3>
                <span v-if="localComments.length"
                  class="px-1.5 py-0.5 rounded-full bg-white/5 text-slate-500 text-[10px] font-mono">
                  {{ localComments.length }}
                </span>
                <div v-if="loadingActivity" class="ml-auto flex items-center gap-1.5 text-xs text-slate-500">
                  <div class="w-3 h-3 rounded-full border-2 border-cyan-500/40 border-t-cyan-400 animate-spin" />
                </div>
              </div>
              <CommentsSection
                :comments="localComments"
                :current-user="currentUser ?? undefined"
                :task-title="task.title"
                @comment="onComment"
                @delete-comment="id => deleteComment(task!.id, id)"
              />
            </section>
          </div>
        </div>
      </Transition>

      <Toast
        :show="toast.show"
        :message="toast.message"
        :type="toast.type"
        @close="hideToast"
      />

    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, computed, watch, reactive, nextTick, onMounted, onUnmounted } from 'vue'
import { CalendarDays } from 'lucide-vue-next'
import type { Task, User, Tag, SubTask, TaskStatus, TaskPriority, TaskType } from '../../../types/task.types'
import { useUsers } from '../../../composables/useUsers'
import { useTags } from '../../../composables/useTags'
import { useTasks } from '../../../composables/useTasks'
import { useToast } from '../../../composables/useToast' 
import { useUserStore } from '../../../stores/useUserStore'
import Toast from '../../shared/Toast.vue'
import TaskDetailHeader  from './TaskDetailHeader.vue'
import TaskDetailMetaBar from './TaskDetailMetaBar.vue'
import DescriptionSection from './DescriptionSection.vue'
import SubtaskList       from '../SubtaskList.vue'
import CommentsSection   from './CommentSection.vue'
import AddToCalendarButton from './AddToCalendarButton.vue'
import { useActivityLogger } from '../../../composables/Activity/useActivityLogger'

const props = defineProps<{ task: Task | null }>()
const emit  = defineEmits<{ close: []; update: [task: Task]; comment: [taskId: string, content: string] }>()
const { commentAdded, taskStatusChanged } = useActivityLogger()

const { users }                       = useUsers()
const { tags, fetchTags, createTag }  = useTags()
const taskStore                       = useTasks()
const { toast, showToast, hideToast } = useToast()
const authStore                       = useUserStore()
const currentUser                     = computed(() => authStore.asTaskUser)

// ── Body scroll lock ──────────────────────────────────────────────────────────
// Empêche la scrollbar globale de l'app quand TaskDetail est ouvert
watch(() => props.task, (t) => {
  document.body.style.overflow = t ? 'hidden' : ''
}, { immediate: true })

onUnmounted(() => {
  document.body.style.overflow = ''
})

// ── State ─────────────────────────────────────────────────────────────────────
const localTask     = reactive<Task>({} as Task)
const editingTitle  = ref(false)
const localTitle    = ref('')
const localSubtasks = ref<SubTask[]>([])
const localComments = ref<Task['comments']>([])
const isSaving      = ref(false)
const savedAt       = ref(false)
const loadingActivity = ref(false)
const titleRef      = ref<HTMLTextAreaElement | null>(null)
const descRef       = ref<InstanceType<typeof DescriptionSection> | null>(null)
const descEditing   = ref(false)

const onClickOutside = () => {
  if (descEditing.value) return
  emit('close')
}
let savedTimeout: ReturnType<typeof setTimeout> | null = null

// ── Watch ─────────────────────────────────────────────────────────────────────
watch(() => props.task, async (t, prev) => {
  if (!t) return
  const isNewTask = t.id !== prev?.id

  if (isNewTask) {
    Object.keys(localTask).forEach(k => delete (localTask as any)[k])
    Object.assign(localTask, JSON.parse(JSON.stringify(t)))
    localTitle.value    = t.title
    localSubtasks.value = JSON.parse(JSON.stringify(t.subtasks ?? []))
    localComments.value = JSON.parse(JSON.stringify(t.comments ?? []))
    editingTitle.value  = false
    descRef.value?.resetEditing()

    loadingActivity.value = true
    try {
      const [fc] = await Promise.all([taskStore.fetchComments(t.id)])
      localComments.value = fc
    } finally {
      loadingActivity.value = false
    }
  } else {
    if (t.comments?.length) localComments.value = JSON.parse(JSON.stringify(t.comments))
  }
}, { immediate: true })

onMounted(() => fetchTags())

// ── Computed ──────────────────────────────────────────────────────────────────
const availableTags = computed<Tag[]>(() =>
  tags.value.filter((t: Tag) => !localTask.tags?.some((lt: Tag) => lt.id === t.id))
)
const isDueDatePast = computed(() => {
  if (!localTask.due_date) return false
  return new Date(localTask.due_date) < new Date(new Date().toDateString())
})
const canCloseFromReview = computed(() =>
  localTask.status !== 'review' ||
  !currentUser.value ||
  localTask.assignee?.id !== currentUser.value.id
)

// ── Helpers ───────────────────────────────────────────────────────────────────
function showSaved() {
  if (savedTimeout) clearTimeout(savedTimeout)
  savedAt.value = true
  savedTimeout = setTimeout(() => { savedAt.value = false }, 2000)
}
function pushUpdate(patch: Partial<Task>) {
  isSaving.value = true
  const updated = Object.assign({}, localTask, patch, { subtasks: localSubtasks.value })
  emit('update', updated as Task)
  isSaving.value = false
  showSaved()
}

const handleReorder = async (reorderedSubtasks: SubTask[]) => {
  const hasTemporaryIds = reorderedSubtasks.some(s => s.id < 0)
  
  localSubtasks.value = reorderedSubtasks
  
  if (hasTemporaryIds) return
  
  await taskStore.reorderSubtasks(localTask.id, reorderedSubtasks)
  showSaved()
}


// ── Status ────────────────────────────────────────────────────────────────────
const STATUS_ORDER: TaskStatus[] = ['open', 'review', 'closed']
const cycleStatus = () => {
  let next = STATUS_ORDER[(STATUS_ORDER.indexOf(localTask.status) + 1) % STATUS_ORDER.length]!
  if (next === 'closed' && !canCloseFromReview.value) return
  if (next === 'review' && localTask.type === 'standard') next = 'closed'
  taskStatusChanged(localTask.title, localTask.status, next)
  localTask.status = next
  pushUpdate({ status: next })
}

// ── Title ─────────────────────────────────────────────────────────────────────
const startEditTitle = async () => { editingTitle.value = true; await nextTick(); titleRef.value?.focus() }
const saveTitle = () => {
  if (localTitle.value.trim()) { localTask.title = localTitle.value.trim(); pushUpdate({ title: localTask.title }) }
  editingTitle.value = false
}
const cancelTitle = () => { localTitle.value = localTask.title; editingTitle.value = false }

// ── Description ───────────────────────────────────────────────────────────────
const onDescSave = (html: string) => {
  localTask.description = html
  pushUpdate({ description: html })
}

// ── Subtasks ──────────────────────────────────────────────────────────────────
let nextSubId = -1
nextSubId--
const toggleSubtask = (id: number) => { const s = localSubtasks.value.find(x => x.id === id); if (s) { s.completed = !s.completed; pushUpdate({}) } }
const deleteSubtask = (id: number) => { localSubtasks.value = localSubtasks.value.filter(x => x.id !== id); pushUpdate({}) }
const addSubtask = async (title: string) => {
  const tempId = nextSubId--
  localSubtasks.value.push({ id: tempId, title, completed: false, order: localSubtasks.value.length })
  const updated = await taskStore.updateTask(localTask.id, taskStore.toUpdatePayload({
    ...localTask,
    subtasks: localSubtasks.value,
  }))

  if (updated) {
    localSubtasks.value = updated.subtasks ?? []
    showSaved()
  }
}

// ── Tags ──────────────────────────────────────────────────────────────────────
const addTag    = (tag: Tag)    => { if (!localTask.tags) localTask.tags = []; localTask.tags.push(tag); pushUpdate({ tags: localTask.tags }) }
const removeTag = (id: number)  => { localTask.tags = localTask.tags?.filter(t => t.id !== id) ?? []; pushUpdate({ tags: localTask.tags }) }
const onNewTag  = async (name: string, color: string) => { const t = await createTag(name, color); if (t) addTag(t) }

// ── Meta handlers ─────────────────────────────────────────────────────────────
const onAssigneeChange = (u: User | null)          => { localTask.assignee  = u ?? undefined; pushUpdate({ assignee: localTask.assignee }) }
const onPriorityChange = (p: TaskPriority)         => { localTask.priority  = p;              pushUpdate({ priority: p }) }
const onTypeChange     = (t: TaskType)             => { localTask.type      = t;              pushUpdate({ type: t }) }
const onDueDateChange  = (val: string | undefined) => { localTask.due_date  = val;            pushUpdate({ due_date: val }) }

// ── Comments ──────────────────────────────────────────────────────────────────
const onComment = async (content: string) => {
  if (!props.task) return
  const saved = await taskStore.addComment(props.task.id, content)
  if (saved) {
    localComments.value.push(saved)
    commentAdded(localTask.title)
  }
}

const deleteComment = async (taskId: string, commentId: number) => {
  const success = await taskStore.deleteComment(taskId, commentId)
  if (success) {
    localComments.value = localComments.value.filter(c => c.id !== commentId)
    showToast('Commentaire supprimé', 'success')
  } else {
    showToast('Impossible de supprimer le commentaire', 'error')
  }
}

const fmtDate = (iso: string) => new Date(iso).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })
</script>

<style scoped>
.backdrop-enter-active, .backdrop-leave-active { transition: opacity 0.25s ease; }
.backdrop-enter-from,  .backdrop-leave-to      { opacity: 0; }
.slideover-enter-active, .slideover-leave-active { transition: transform 0.3s cubic-bezier(0.32, 0.72, 0, 1); }
.slideover-enter-from,   .slideover-leave-to     { transform: translateX(100%); }
</style>