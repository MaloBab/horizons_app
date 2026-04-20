import { ref } from 'vue'
import { useUsers } from './useUsers'
import type { Task, TaskStatus, TaskPriority, TaskType, Tag, SubTask, Comment, User } from '../types/task.types'
import { apiFetch } from '../api'

const _tasks = ref<Task[]>([])
const _isLoading = ref(false)
const _error = ref<string | null>(null)

interface RawUserEmbedded {
  id: string
  username: string
  profile_picture_url: string | null
}

interface RawSubtask {
  id: number
  title: string
  is_completed: boolean
  position: number
}

interface RawTag {
  id: number
  name: string
  color_hex: string | null
}

interface RawComment {
  id: number
  task_id: string
  author_id: string
  author: RawUserEmbedded
  content: string
  created_at: string
  updated_at: string | null
}

interface RawTask {
  id: string
  title: string
  description: string | null
  type: TaskType
  status: TaskStatus
  priority: TaskPriority
  creator_id: string
  assignee_id: string | null
  assignee: RawUserEmbedded | null
  due_date: string | null
  opened_at: string
  verification_opened_at: string | null
  closed_at: string | null
  tags: RawTag[]
  subtasks?: RawSubtask[]
  comments?: RawComment[]
  google_calendar_event_id?: string
}

export interface TaskCreatePayload {
  title: string
  description?: string
  type?: TaskType
  priority?: TaskPriority
  due_date?: string
  assignee_id?: string
  tag_ids?: number[]
  subtasks?: { title: string; is_completed: boolean; order: number }[]
}

export interface TaskUpdatePayload {
  title?: string
  description?: string
  type?: TaskType
  status?: TaskStatus
  priority?: TaskPriority
  assignee_id?: string | null
  due_date?: string | null
  tag_ids?: number[]
  subtasks?: { id?: number; title: string; is_completed: boolean; order: number }[]
}

export interface TaskFilters {
  skip?: number
  limit?: number
  status?: TaskStatus
  assignee_id?: string
}

export function useTasks() {
  const { fetchUsers, mapUser } = useUsers()

  const tasks = _tasks
  const isLoading = _isLoading
  const error = _error

  async function handleResponse<T>(res: Response): Promise<T> {
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      throw new Error(data.detail ?? `Erreur ${res.status}`)
    }
    if (res.status === 204) return undefined as T
    return res.json()
  }

  function mapEmbeddedUser(raw: RawUserEmbedded | null | undefined): User | undefined {
    if (!raw) return undefined
    return mapUser({
      id: raw.id,
      username: raw.username,
      email: '',
      profile_picture_url: raw.profile_picture_url,
    })
  }

  function mapTag(raw: RawTag): Tag {
    return { id: raw.id, name: raw.name, color: raw.color_hex ?? '#64748b' }
  }

  function mapComment(raw: RawComment): Comment {
    return {
      id: raw.id,
      author: mapEmbeddedUser(raw.author)!,
      content: raw.content,
      created_at: raw.created_at,
    }
  }

  function mapSubtask(raw: RawSubtask): SubTask {
    return { id: raw.id, title: raw.title, completed: raw.is_completed, order: raw.position }
  }

  function mapTask(raw: RawTask): Task {
    const due_date = raw.due_date ? raw.due_date.slice(0, 10) : undefined
    return {
      id: raw.id,
      title: raw.title,
      description: raw.description ?? '',
      status: raw.status,
      priority: raw.priority,
      type: raw.type ?? 'standard',
      assignee: mapEmbeddedUser(raw.assignee),
      tags: (raw.tags ?? []).map(mapTag),
      subtasks: (raw.subtasks ?? []).map(mapSubtask).sort((a, b) => a.order - b.order),
      due_date,
      created_at: raw.opened_at,
      comments: (raw.comments ?? []).map(mapComment),
      google_calendar_event_id: raw.google_calendar_event_id
    }
  }

  async function fetchTasks(filters: TaskFilters = {}): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      await fetchUsers()

      const params = new URLSearchParams()
      if (filters.skip !== undefined) params.set('skip', String(filters.skip))
      if (filters.limit !== undefined) params.set('limit', String(filters.limit))
      if (filters.status) params.set('status', filters.status)
      if (filters.assignee_id) params.set('assignee_id', filters.assignee_id)

      const qs = params.toString()
      const res = await apiFetch(`/tasks/${qs ? `?${qs}` : ''}`)
      const raw = await handleResponse<RawTask[]>(res)
      tasks.value = raw.map(mapTask)
    } catch (err_) {
      error.value = err_ instanceof Error ? err_.message : 'Erreur inconnue'
    } finally {
      isLoading.value = false
    }
  }

  async function createTask(payload: TaskCreatePayload): Promise<Task | null> {
    error.value = null
    try {
      const cleanPayload = { ...payload }
      if (!cleanPayload.due_date) delete cleanPayload.due_date
      const res = await apiFetch(`/tasks/`, {
        method: 'POST', body: JSON.stringify(cleanPayload),
      })
      const raw = await handleResponse<RawTask>(res)
      const task = mapTask(raw)
      tasks.value.unshift(task)
      return task
    } catch (err_) {
      error.value = err_ instanceof Error ? err_.message : 'Erreur inconnue'
      return null
    }
  }

  async function updateTask(taskId: string, payload: TaskUpdatePayload): Promise<Task | null> {
    error.value = null
    try {
      const res = await apiFetch(`/tasks/${taskId}`, {
        method: 'PUT', body: JSON.stringify(payload),
      })
      const raw = await handleResponse<RawTask>(res)
      const task = mapTask(raw)
      const idx = tasks.value.findIndex(t => t.id === taskId)
      if (idx !== -1) {
        task.comments = tasks.value[idx]!.comments
        tasks.value[idx] = task
      }
      return task
    } catch (err_) {
      error.value = err_ instanceof Error ? err_.message : 'Erreur inconnue'
      return null
    }
  }

  async function changeStatus(taskId: string, status: TaskStatus): Promise<Task | null> {
    error.value = null
    const idx = tasks.value.findIndex(t => t.id === taskId)
    const previous = idx !== -1 ? { ...tasks.value[idx]! } : null
    if (idx !== -1) tasks.value[idx]!.status = status

    try {
      const res = await apiFetch(`/tasks/${taskId}/status?new_status=${status}`, {
        method: 'PATCH',
      })
      const raw = await handleResponse<RawTask>(res)
      const task = mapTask(raw)
      if (idx !== -1) {
        task.comments = tasks.value[idx]!.comments
        tasks.value[idx] = task
      }
      return task
    } catch (err_) {
      if (idx !== -1 && previous) tasks.value[idx] = previous as Task
      error.value = err_ instanceof Error ? err_.message : 'Erreur inconnue'
      return null
    }
  }

  async function assignTask(taskId: string, assigneeId?: string | null): Promise<Task | null> {
    error.value = null
    try {
      const params = new URLSearchParams()
      if (assigneeId != null) params.set('assignee_id', assigneeId)

      const res = await apiFetch(`/tasks/${taskId}/assign?${params}`, {
        method: 'PATCH',
      })
      const raw = await handleResponse<RawTask>(res)
      const task = mapTask(raw)
      const idx = tasks.value.findIndex(t => t.id === taskId)
      if (idx !== -1) {
        task.comments = tasks.value[idx]!.comments
        tasks.value[idx] = task
      }
      return task
    } catch (err_) {
      error.value = err_ instanceof Error ? err_.message : 'Erreur inconnue'
      return null
    }
  }

  async function deleteTask(taskId: string): Promise<boolean> {
    error.value = null
    try {
      const res = await apiFetch(`/tasks/${taskId}`, {
        method: 'DELETE',
      })
      await handleResponse<void>(res)
      tasks.value = tasks.value.filter(t => t.id !== taskId)
      return true
    } catch (err_) {
      error.value = err_ instanceof Error ? err_.message : 'Erreur inconnue'
      return false
    }
  }

  async function addComment(taskId: string, content: string): Promise<Comment | null> {
    error.value = null
    try {
      const res = await apiFetch(`/tasks/${taskId}/comments`, {
        method: 'POST', body: JSON.stringify({ content }),
      })
      const raw = await handleResponse<RawComment>(res)
      const comment = mapComment(raw)
      const task = tasks.value.find(t => t.id === taskId)
      if (task) task.comments.push(comment)
      return comment
    } catch (err_) {
      error.value = err_ instanceof Error ? err_.message : 'Erreur inconnue'
      return null
    }
  }

    async function deleteComment(taskId: string, commentId: number): Promise<boolean> {
    error.value = null
    try {
      const res = await apiFetch(`/tasks/${taskId}/comments/${commentId}`, {
        method: 'DELETE',
      })
      await handleResponse<void>(res)
      const task = tasks.value.find(t => t.id === taskId)
      if (task) task.comments = task.comments.filter(c => c.id !== commentId)
      return true
    }
      catch (err_) {
        error.value = err_ instanceof Error ? err_.message : 'Erreur inconnue'
        return false
      }
  }

  async function fetchComments(taskId: string): Promise<Comment[]> {
    error.value = null
    try {
      const res = await apiFetch(`/tasks/${taskId}/comments`)
      const data = await handleResponse<RawComment[]>(res)
      return data.map(mapComment)
    } catch (err_) {
      error.value = err_ instanceof Error ? err_.message : 'Erreur inconnue'
      return []
    }
  }

  async function reorderSubtasks(taskId: string, subtasks: SubTask[]): Promise<void> {
    error.value = null
    try {
      const items = subtasks
        .map((sub, index) => ({ id: sub.id, order: index }))
        .filter(item => item.id > 0)      
            if (items.length === 0) return

      const res = await apiFetch(`/tasks/${taskId}/subtasks/reorder`, {
        method: 'PATCH',
        body: JSON.stringify(items),
      })
      await handleResponse<void>(res)

      const task = tasks.value.find(t => t.id === taskId)
      if (task) task.subtasks = subtasks
    } catch (err_) {
      error.value = err_ instanceof Error ? err_.message : 'Erreur inconnue'
    }
  }

  function toCreatePayload(form: {
    title: string
    description?: string
    type?: TaskType
    priority?: TaskPriority
    assignee?: { id: string }
    tags?: Tag[]
    due_date?: string
    subtasks?: SubTask[]
  }): TaskCreatePayload {
    return {
      title: form.title,
      description: form.description,
      type: form.type,
      priority: form.priority,
      assignee_id: form.assignee?.id,
      tag_ids: form.tags?.map(t => t.id),
      due_date: (form.due_date && form.due_date.trim()) ? form.due_date : undefined,
      subtasks: (form.subtasks ?? []).map((s, i) => ({
        title: s.title,
        is_completed: s.completed,
        order: i,
      })),
    }
  }

  function toUpdatePayload(patch: Partial<Task>): TaskUpdatePayload {
    const p: TaskUpdatePayload = {}
    if (patch.title !== undefined) p.title = patch.title
    if (patch.description !== undefined) p.description = patch.description
    if (patch.status !== undefined) p.status = patch.status
    if (patch.priority !== undefined) p.priority = patch.priority
    if (patch.type !== undefined) p.type = patch.type
    if ('due_date' in patch) p.due_date = patch.due_date ?? null
    if (patch.tags !== undefined) p.tag_ids = patch.tags.map(t => t.id)
    if ('assignee' in patch) p.assignee_id = (patch.assignee as any)?.id ?? null
    if (patch.subtasks !== undefined) p.subtasks = patch.subtasks.map((s, i) => ({
      id: typeof s.id === 'number' && s.id < 0 ? undefined : s.id as number | undefined,
      title: s.title,
      is_completed: s.completed,
      order: i,
    }))
    return p
  }

  async function exportToCalendar(taskId: string): Promise<string | null> {
    _error.value = null
    try {
      const res = await apiFetch(`/tasks/${taskId}/export-calendar`, {
        method: 'POST',
      })

      const data = await handleResponse<{ is_exported: boolean; link: string | null }>(res)

      const task = _tasks.value.find(t => t.id === taskId)
      if (task) {
        task.google_calendar_event_id = data.is_exported ? 'sync' : null as any
      }

      return data.link || ''
    } catch (err_) {
      _error.value = err_ instanceof Error ? err_.message : 'Erreur'
      throw err_
    }
  }

  return {
    tasks, isLoading, error,
    fetchTasks, createTask, updateTask, changeStatus,
    assignTask, deleteTask, addComment, deleteComment, fetchComments,
    reorderSubtasks,
    toCreatePayload, toUpdatePayload, exportToCalendar,
  }
}