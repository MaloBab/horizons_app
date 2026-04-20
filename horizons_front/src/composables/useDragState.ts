/**
 * useDragState.ts
 *
 * Résout une limitation fondamentale de l'API HTML5 Drag & Drop :
 * dataTransfer.getData() retourne une chaîne vide pendant dragover/dragenter
 * (sécurité navigateur — les données ne sont accessibles qu'au drop).
 *
 * Solution : état réactif module-scope (singleton) qui stocke les métadonnées
 * du drag en cours, accessible par tous les composants sans prop drilling.
 */
import { ref, readonly } from 'vue'

interface DragState {
  volunteerId: string
  source: 'sidebar' | 'gantt'
  fromJobId: number | null
}

const _active      = ref(false)
const _dragState   = ref<DragState | null>(null)

export function useDragState() {
  function startDrag(volunteerId: string, source: 'sidebar' | 'gantt', fromJobId: number | null = null) {
    _active.value    = true
    _dragState.value = { volunteerId, source, fromJobId }
  }

  function endDrag() {
    _active.value    = false
    _dragState.value = null
  }

  return {
    isDragging:  readonly(_active),
    dragState:   readonly(_dragState),
    startDrag,
    endDrag,
  }
}