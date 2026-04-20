export type TaskStatus   = 'open' | 'review' | 'closed'
export type TaskPriority = 'low' | 'medium' | 'high' | 'critical'
export type TaskType     = 'standard' | 'needs_review'

export interface User {
  id: string
  username: string
  email: string
  avatar_url?: string
  initials: string
  color: string
  role?: string
}

export interface Tag {
  id: number
  name: string
  color: string
}

export interface SubTask {
  id: number
  title: string
  completed: boolean
  order: number
}

export interface Comment {
  id: number
  author: User
  content: string
  created_at: string
}

export type ActivityEntry =
  | { kind: 'comment'; data: Comment }

export interface Task {
  id: string
  title: string
  description: string
  status: TaskStatus
  priority: TaskPriority
  type: TaskType
  assignee?: User
  tags: Tag[]
  subtasks: SubTask[]
  due_date?: string
  created_at: string
  comments: Comment[]
  google_calendar_event_id?: string
}