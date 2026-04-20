<template>
  <div class="min-h-screen bg-slate-900 text-white">

    <div class="fixed inset-0 pointer-events-none overflow-hidden">
      <div class="absolute top-0 right-0 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl" />
      <div class="absolute bottom-0 left-0 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl" />
    </div>

    <BoardHeader 
      :error="taskStore.error.value"
      :selected-closed-count="selectedClosedIds.size"
      @add-tag="showAddTag = true"
      @delete-tag="showDeleteTag = true"
      @delete-tasks="showDeleteTasks = true"
      @create-task="showCreate = true"
    />

    <BoardFilters 
      :filters="filters"
      :users="users"
      :tags="tags"
      :total-filtered="totalFiltered"
      :is-loading="taskStore.isLoading.value || usersLoading"
      @reset="resetFilters"
    />

    <main class="relative z-10 px-6 py-6 overflow-x-auto">
      <div class="flex gap-5" style="min-width: calc(3 * 320px + 2 * 1.25rem)">
        <KanbanColumn
          v-for="col in columns" :key="col.status"
          :title="col.title" 
          :status="col.status" 
          :color="col.color"
          :tasks="filteredByColumn(col.status)"
          :selected-ids="col.status === 'closed' ? selectedClosedIds : undefined"
          class="flex-1 min-w-72"
          @add="showCreate = true"
          @open="openTask"
          @toggle-select="toggleSelectClosed"
        />
      </div>
    </main>

    <TaskDetail
      :task="selectedTask"
      @close="selectedTask = null"
      @update="onTaskUpdate"
      @comment="(id: string, content: string) => taskStore.addComment(id, content)"
    />
    <CreateTaskModal :open="showCreate" @close="showCreate = false" @create="onCreate" />
    <AddTagModal    :open="showAddTag"    @close="showAddTag = false" />
    <DeleteTagModal :open="showDeleteTag" @close="showDeleteTag = false" @deleted="onTagsDeleted" />
    <DeleteTasksModal
      :open="showDeleteTasks"
      :count="selectedClosedIds.size"
      :loading="deletingTasks"
      @confirm="deleteSelectedTasks"
      @cancel="showDeleteTasks = false"
    />

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'

// Types & Composables
import type { Task, TaskStatus } from '../../types/task.types'
import { useTasks }     from '../../composables/useTasks'
import { useUsers }     from '../../composables/useUsers'
import { useTags }      from '../../composables/useTags'
import { useUserStore } from '../../stores/useUserStore'

// Composants
import BoardHeader      from './header/BoardHeader.vue'
import BoardFilters     from './header/BoardFilters.vue'
import KanbanColumn     from './KanbanColumn.vue'
import TaskDetail       from './taskDetail/TaskDetail.vue'
import CreateTaskModal  from './modals/CreateTaskModal.vue'
import AddTagModal      from './tags/AddTagModal.vue'
import DeleteTagModal   from './tags/DeleteTagModal.vue'
import DeleteTasksModal from './modals/DeleteTaskModal.vue'

const taskStore = useTasks()
const authStore = useUserStore()
const { users, isLoading: usersLoading, fetchUsers } = useUsers()
const { tags, fetchTags } = useTags()

// ── État local (Modales et Sélection) ─────────────────────────────────────────
const selectedTask      = ref<Task | null>(null)
const showCreate        = ref(false)
const showAddTag        = ref(false)
const showDeleteTag     = ref(false)
const showDeleteTasks   = ref(false)
const deletingTasks     = ref(false)
const selectedClosedIds = ref<Set<string>>(new Set())

const columns = [
  { status: 'open'   as TaskStatus, title: 'Ouvert',     color: '#22d3ee' },
  { status: 'review' as TaskStatus, title: 'À Vérifier', color: '#a855f7' },
  { status: 'closed' as TaskStatus, title: 'Fermé',      color: '#10b981' },
]

// ── Logique de Filtres ────────────────────────────────────────────────────────
const filters = reactive({
  search:  '',
  myTasks: false,
  userId:  null as string | null,
  tagIds:  [] as number[],
})

const filteredTasks = computed(() => {
  const allTasks = taskStore.tasks?.value || taskStore.tasks || []
  return allTasks.filter((t: Task) => {
    if (filters.search && !t.title.toLowerCase().includes(filters.search.toLowerCase())) return false
    if (filters.myTasks && t.assignee?.id !== authStore.user?.id) return false
    if (filters.userId === '__unassigned__' && t.assignee) return false
    if (filters.userId && filters.userId !== '__unassigned__' && t.assignee?.id !== filters.userId) return false
    if (filters.tagIds.length && !filters.tagIds.some(id => t.tags.some(tg => tg.id === id))) return false
    return true
  })
})

const filteredByColumn = (status: TaskStatus) => filteredTasks.value.filter(t => t.status === status)
const totalFiltered    = computed(() => filteredTasks.value.length)

const resetFilters = () => {
  filters.search = ''
  filters.myTasks = false
  filters.userId = null
  filters.tagIds = []
}

const onTagsDeleted = (ids: number[]) => {
  filters.tagIds = filters.tagIds.filter(id => !ids.includes(id))
}

// ── Logique Métier (Tâches) ───────────────────────────────────────────────────
const openTask = (task: Task) => {
  const allTasks = taskStore.tasks?.value || taskStore.tasks || []
  selectedTask.value = allTasks.find(t => t.id === task.id) ?? task
}

const onTaskUpdate = async (updated: Task) => {
  await taskStore.updateTask(updated.id, taskStore.toUpdatePayload(updated))
  const allTasks = taskStore.tasks?.value || taskStore.tasks || []
  selectedTask.value = allTasks.find(t => t.id === updated.id) ?? null
}

const onCreate = async (data: Omit<Task, 'id' | 'created_at' | 'comments'>) => {
  await taskStore.createTask(taskStore.toCreatePayload(data as any))
}

const toggleSelectClosed = (id: string) => {
  const s = new Set(selectedClosedIds.value)
  s.has(id) ? s.delete(id) : s.add(id)
  selectedClosedIds.value = s
}

const deleteSelectedTasks = async () => {
  deletingTasks.value = true
  await Promise.all([...selectedClosedIds.value].map(id => taskStore.deleteTask(id)))
  selectedClosedIds.value = new Set()
  deletingTasks.value     = false
  showDeleteTasks.value   = false
}

// ── Initialisation ────────────────────────────────────────────────────────────
onMounted(() => {
  fetchUsers()
  fetchTags()
  taskStore.fetchTasks()
})
</script>