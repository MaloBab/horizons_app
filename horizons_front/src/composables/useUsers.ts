import { ref, computed } from 'vue'
import type { User } from '../types/task.types'
import { apiFetch } from '../api'

interface RawUser {
  id: string
  username: string
  email: string
  profile_picture_url: string | null
  role: 'admin' | 'user'
}

const USER_COLORS = [
  '#a855f7', '#3b82f6', '#10b981', '#f59e0b',
  '#ec4899', '#22d3ee', '#ef4444', '#84cc16',
]

function colorFromUuid(uuid: string): string {
  const seed = parseInt(uuid.replace(/-/g, '').slice(0, 8), 16)
  return USER_COLORS[seed % USER_COLORS.length]!
}

function initialsFromUsername(username: string): string {
  return username
    .split(/[\s._-]+/)
    .slice(0, 2)
    .map(p => p[0]?.toUpperCase() ?? '')
    .join('')
}

export function mapUser(raw: { id: string; username: string; email: string; profile_picture_url?: string | null; role?: string }): User {
  return {
    id:         raw.id,
    username:   raw.username,
    email:      raw.email,
    avatar_url: raw.profile_picture_url ?? undefined,
    initials:   initialsFromUsername(raw.username),
    color:      colorFromUuid(raw.id),
    role:       raw.role,
  }
}

const _users     = ref<User[]>([])
const _isLoading = ref(false)
const _error     = ref<string | null>(null)
let   _fetched   = false


export function useUsers() {
  const users     = computed<User[]>(() => _users.value)
  const isLoading = computed<boolean>(() => _isLoading.value)
  const error     = computed<string | null>(() => _error.value)

  /** Fetch all users — no-op if already loaded */
  async function fetchUsers(): Promise<void> {
    if (_fetched) return
    _isLoading.value = true
    _error.value     = null
    try {
      const res = await apiFetch(`/users/`)
      if (!res.ok) throw new Error(`Erreur ${res.status}`)
      const data: RawUser[] = await res.json()
      _users.value = data.map(mapUser)
      _fetched = true
    } catch (err_) {
      _error.value = err_ instanceof Error ? err_.message : 'Erreur inconnue'
    } finally {
      _isLoading.value = false
    }
  }

  /** Force a refresh (e.g. after a user is created / updated) */
  async function refreshUsers(): Promise<void> {
    _fetched = false
    await fetchUsers()
  }

  /** Fetch a single user by UUID and upsert into the list */
  async function fetchUserById(id: string): Promise<User | undefined> {
    const cached = _users.value.find(u => u.id === id)
    if (cached) return cached
    try {
      const res = await apiFetch(`/users/${id}`)
      if (!res.ok) return undefined
      const raw: RawUser = await res.json()
      const user = mapUser(raw)
      const idx = _users.value.findIndex(u => u.id === id)
      if (idx !== -1) _users.value[idx] = user
      else _users.value.push(user)
      return user
    } catch {
      return undefined
    }
  }

  /** Synchronous lookup from the loaded list */
  function getUserById(id: string): User | undefined {
    return _users.value.find(u => u.id === id)
  }

  return {
    users,       
    isLoading, 
    error,      
    fetchUsers,
    refreshUsers,
    fetchUserById,
    getUserById,
    mapUser,
  }
}