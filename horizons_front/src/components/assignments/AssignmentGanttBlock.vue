<template>
  <div
    ref="blockRef"
    class="assignment-block relative rounded-lg select-none transition-all duration-150 cursor-pointer"
    :class="blockStateClass"
    :style="blockStyle"
    @dragenter.prevent="onDragEnter"
    @dragover.prevent="onDragOver"
    @dragleave="onDragLeave"
    @drop.prevent="onDrop"
    @click.stop="openModal"
    @mouseenter="onMouseEnter"
    @mouseleave="onMouseLeave"
  >
    <!-- Bordure gauche remplissage -->
    <div
      class="absolute left-0 top-1 bottom-1 w-0.5 rounded-full transition-colors duration-300 pointer-events-none"
      :class="fillBorderColor"
    />

    <!-- Contenu -->
    <div
      class="flex flex-col justify-center px-1.5 h-full gap-1 overflow-hidden"
      :class="isDraggingExternal ? 'pointer-events-none' : ''"
    >
      <span
        class="text-[9px] font-bold font-mono leading-none pointer-events-none whitespace-nowrap"
        :class="fillTextColor"
      >
        {{ assignedCount }}/{{ job.required_volunteers }}
      </span>
      <div class="h-0.5 w-full bg-slate-600/50 rounded-full overflow-hidden pointer-events-none">
        <div
          class="h-full rounded-full transition-all duration-500"
          :class="fillBarColor"
          :style="{ width: `${fillPercent}%` }"
        />
      </div>
    </div>

    <!-- Surbrillance bénévole sélectionné (mode emploi du temps) -->
    <div
      v-if="highlightVolunteerId && isHighlightedVolunteerAssigned"
      class="absolute inset-0 rounded-lg ring-2 ring-purple-400/60 bg-purple-500/10 pointer-events-none"
    />

    <!-- Overlay drop invalide -->
    <div
      v-if="isDragOver && !isCompatible"
      class="absolute inset-0 rounded-lg bg-red-500/15 border border-red-500/40 flex items-center justify-center pointer-events-none"
    >
      <X class="w-3 h-3 text-red-400" />
    </div>

    <!-- Élément invisible pour tuer le ghost natif sur les drags de chips -->
    <div ref="ghostKillerRef" class="fixed -left-2499 -top-2499 w-1 h-1 opacity-0 pointer-events-none" aria-hidden="true" />
  </div>

  <!-- Tooltip au survol -->
  <AssignmentJobTooltip
    :show="tooltipVisible && !isDragging"
    :job="job"
    :color-index="colorIndex"
    :anchor-rect="blockRect"
  />

  <!-- Modal au clic -->
  <AssignmentJobModal
    v-model="modalOpen"
    :job="job"
    :color-index="colorIndex"
    @unassign="(vid, jid) => emit('unassign', vid, jid)"
  />
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { X } from 'lucide-vue-next'
import { storeToRefs } from 'pinia'
import { useAssignmentStore } from '../../stores/useAssignmentStore'
import { useDragState } from '../../composables/useDragState'
import type { JobWithRelations } from '../../types/planning.types'
import AssignmentJobModal   from './AssignmentJobModal.vue'
import AssignmentJobTooltip from './AssignmentJobTooltip.vue'

const props = defineProps<{
  job:                  JobWithRelations
  columnWidth:          number
  rowHeight:            number
  colorIndex:           number
  /** ID du bénévole à surbrillancer (mode emploi du temps) */
  highlightVolunteerId?: string
}>()

const emit = defineEmits<{
  assign:            [volunteerId: string, jobId: number]
  unassign:          [volunteerId: string, jobId: number]
  'open-volunteer':  [volunteerId: string]
  'drag-chip-start': [volunteerId: string, fromJobId: number]
  'drag-chip-end':   []
}>()

const store = useAssignmentStore()
const { assignmentsByJob } = storeToRefs(store)
const { dragState, isDragging, endDrag } = useDragState()

const chipDragging       = ref(false)
const isDraggingExternal = computed(() => isDragging.value && !chipDragging.value)

// ── Surbrillance mode emploi du temps ─────────────────────────────────────────
const isHighlightedVolunteerAssigned = computed(() => {
  if (!props.highlightVolunteerId) return false
  return (assignmentsByJob.value.get(props.job.id) ?? []).some(
    a => a.volunteer_id === props.highlightVolunteerId
  )
})

// ── Modal ──────────────────────────────────────────────────────────────────────
const modalOpen = ref(false)
function openModal() {
  if (isDragging.value) return
  tooltipVisible.value = false
  modalOpen.value = true
}

// ── Tooltip ────────────────────────────────────────────────────────────────────
const tooltipVisible = ref(false)
const blockRect      = ref<DOMRect | null>(null)
let tooltipTimer: ReturnType<typeof setTimeout> | null = null

function onMouseEnter() {
  if (isDragging.value) return
  tooltipTimer = setTimeout(() => {
    if (blockRef.value && !isDragging.value) {
      blockRect.value      = blockRef.value.getBoundingClientRect()
      tooltipVisible.value = true
    }
  }, 350)
}
function onMouseLeave() {
  if (tooltipTimer) { clearTimeout(tooltipTimer); tooltipTimer = null }
  tooltipVisible.value = false
  blockRect.value      = null
}

// ── Données ────────────────────────────────────────────────────────────────────
const assignedList  = computed(() => assignmentsByJob.value.get(props.job.id) ?? [])
const assignedCount = computed(() => assignedList.value.length)
const fillPercent   = computed(() =>
  props.job.required_volunteers > 0 ? (assignedCount.value / props.job.required_volunteers) * 100 : 0
)
const isFull  = computed(() => assignedCount.value >= props.job.required_volunteers)
const isEmpty = computed(() => assignedCount.value === 0)

// ── Dimensions ─────────────────────────────────────────────────────────────────
const durationHours = computed(() => props.job.slot.end_time - props.job.slot.start_time)
const blockStyle = computed(() => ({
  width:  `${Math.max(1, durationHours.value * props.columnWidth - 4)}px`,
  height: `${props.rowHeight - 8}px`,
}))

// ── Couleurs ───────────────────────────────────────────────────────────────────
const fillBorderColor = computed(() => isEmpty.value ? 'bg-red-400/70'  : isFull.value ? 'bg-green-400/70' : 'bg-amber-400/70')
const fillTextColor   = computed(() => isEmpty.value ? 'text-red-400'   : isFull.value ? 'text-green-400'  : 'text-amber-400')
const fillBarColor    = computed(() => isEmpty.value ? 'bg-red-400'     : isFull.value ? 'bg-green-400'    : 'bg-amber-400')

// ── Compatibilité globale ──────────────────────────────────────────────────────
const incompatibilityReason = computed<string | null>(() => {
  if (!isDraggingExternal.value) return null
  const vid = dragState.value?.volunteerId
  if (!vid) return null
  return store.getIncompatibilityReason(vid, props.job)
})
const isGloballyCompatible   = computed(() => isDraggingExternal.value && incompatibilityReason.value === null)
const isGloballyIncompatible = computed(() => isDraggingExternal.value && incompatibilityReason.value !== null)

// ── DnD ────────────────────────────────────────────────────────────────────────
const isDragOver   = ref(false)
const isCompatible = ref(false)

function onDragEnter(e: DragEvent) {
  e.preventDefault()
  if (chipDragging.value) return
  tooltipVisible.value = false
  const vid = dragState.value?.volunteerId
  isCompatible.value = vid ? store.isCompatible(vid, props.job) : false
  isDragOver.value   = true
}
function onDragOver(e: DragEvent) {
  e.preventDefault()
  if (chipDragging.value) return
  e.dataTransfer!.dropEffect = isCompatible.value ? 'move' : 'none'
}
function onDragLeave(e: DragEvent) {
  const related = e.relatedTarget as Node | null
  if (related && blockRef.value?.contains(related)) return
  isDragOver.value   = false
  isCompatible.value = false
}
function onDrop(e: DragEvent) {
  e.preventDefault()
  isDragOver.value   = false
  isCompatible.value = false
  const volunteerId = dragState.value?.volunteerId
  const fromJobId   = dragState.value?.fromJobId ?? null
  endDrag()
  if (!volunteerId) return
  emit('assign', volunteerId, props.job.id)
  if (fromJobId !== null && fromJobId !== props.job.id) {
    emit('drag-chip-start', volunteerId, fromJobId)
  }
}

// ── State classes ──────────────────────────────────────────────────────────────
const blockStateClass = computed(() => {
  if (isDragOver.value && isCompatible.value)
    return 'bg-cyan-500/25 border border-cyan-400/60 ring-2 ring-cyan-400/30 scale-[1.02] z-20'
  if (isDragOver.value && !isCompatible.value)
    return 'bg-red-500/15 border border-red-400/40 cursor-not-allowed'
  if (isGloballyCompatible.value)
    return 'bg-cyan-500/10 border border-cyan-400/30 cursor-copy'
  if (isGloballyIncompatible.value)
    return 'bg-slate-700/30 border border-white/5 opacity-50 cursor-not-allowed'
  return 'bg-slate-700/50 border border-white/8 hover:bg-slate-700/70 hover:border-white/15'
})

const blockRef = ref<HTMLElement | null>(null)
</script>