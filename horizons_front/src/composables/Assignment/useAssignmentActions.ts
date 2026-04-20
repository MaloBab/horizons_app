import { ref } from 'vue'
import { useAssignmentStore } from '../../stores/useAssignmentStore'
import { useToast } from '../../composables/useToast'
import type { JobWithRelations } from '../../types/planning.types'
import type { Ref } from 'vue'

/**
 * Encapsule les actions d'assignation (assign / unassign / reassign)
 * ainsi que la gestion du drag-and-drop de chips.
 */
export function useAssignmentActions(jobs: Ref<JobWithRelations[]>) {
  const store = useAssignmentStore()
  const { toast, showToast, hideToast } = useToast()

  const dragChipFromJob = ref<number | null>(null)

  function onChipDragStart(_id: string, fromJobId: number) {
    dragChipFromJob.value = fromJobId
  }

  function onChipDragEnd() {
    dragChipFromJob.value = null
  }

  function handleAssign(volunteerId: string, jobId: number) {
    const job = jobs.value.find(j => j.id === jobId)
    if (!job) { showToast('Poste introuvable', 'error'); return }

    const isReassign = dragChipFromJob.value !== null && dragChipFromJob.value !== jobId
    if (isReassign) {
      const reason = store.getIncompatibilityReason(volunteerId, job)
      if (reason) { showToast(reason, 'error'); dragChipFromJob.value = null; return }
      store.reassign(volunteerId, dragChipFromJob.value!, jobId)
      dragChipFromJob.value = null
      return
    }

    const reason = store.getIncompatibilityReason(volunteerId, job)
    if (reason) { showToast(reason, 'error'); return }
    store.assign(volunteerId, jobId)
  }

  function handleUnassign(volunteerId: string, jobId: number) {
    store.unassign(volunteerId, jobId)
  }

  return {
    toast,
    hideToast,
    dragChipFromJob,
    onChipDragStart,
    onChipDragEnd,
    handleAssign,
    handleUnassign,
  }
}