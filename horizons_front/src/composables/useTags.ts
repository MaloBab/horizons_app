import { ref, computed } from 'vue'
import type { Tag } from '../types/task.types'
import { apiFetch } from '../api'

interface RawTag {
  id: number
  name: string
  color_hex: string | null
}

function mapTag(raw: RawTag): Tag {
  return {
    id:    raw.id,
    name:  raw.name,
    color: raw.color_hex ?? '#64748b',
  }
}

const _tags      = ref<Tag[]>([])
const _isLoading = ref(false)
const _error     = ref<string | null>(null)
let   _fetched   = false

export function useTags() {
  const tags      = computed<Tag[]>(() => _tags.value)
  const isLoading = computed<boolean>(() => _isLoading.value)
  const error     = computed<string | null>(() => _error.value)

  async function fetchTags(): Promise<void> {
    if (_fetched) return
    _isLoading.value = true
    _error.value     = null
    try {
      const res = await apiFetch(`/tags/`)
      if (!res.ok) throw new Error(`Erreur ${res.status}`)
      const data: RawTag[] = await res.json()
      _tags.value = data.map(mapTag)
      _fetched = true
    } catch (err_) {
      _error.value = err_ instanceof Error ? err_.message : 'Erreur inconnue'
    } finally {
      _isLoading.value = false
    }
  }

  async function refreshTags(): Promise<void> {
    _fetched = false
    await fetchTags()
  }


  async function createTag(name: string, colorHex: string): Promise<Tag | null> {
    _error.value = null
    try {
      const res = await apiFetch(`/tags/`, {
        method:  'POST',
        body:    JSON.stringify({ name, color_hex: colorHex }),
      })
      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail ?? `Erreur ${res.status}`)
      }
      const raw: RawTag = await res.json()
      const tag = mapTag(raw)
      _tags.value.push(tag)
      return tag
    } catch (err_) {
      _error.value = err_ instanceof Error ? err_.message : 'Erreur inconnue'
      return null
    }
  }

  async function deleteTag(tagId: number): Promise<boolean> {
    _error.value = null
    try {
      const res = await apiFetch(`/tags/${tagId}`, {
        method:  'DELETE',
      })
      if (!res.ok && res.status !== 204) throw new Error(`Erreur ${res.status}`)
      _tags.value = _tags.value.filter(t => t.id !== tagId)
      return true
    } catch (err_) {
      _error.value = err_ instanceof Error ? err_.message : 'Erreur inconnue'
      return false
    }
  }

  return {
    tags,
    isLoading,
    error,
    fetchTags,
    refreshTags,
    createTag,
    deleteTag,
  }
}