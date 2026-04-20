<template>
  <Teleport to="body">
    <div
      v-if="dragState && isDragging"
      class="fixed top-0 left-0 pointer-events-none z-9999 select-none will-change-transform"
      :style="{ transform: `translate(${pos.x-100}px, ${pos.y-25}px)` }"
    >
      <div
        class="flex items-center gap-2 px-3 py-2 rounded-xl border shadow-2xl"
        :class="volunteer?.volunteer_type === 'Specialise'
          ? 'bg-slate-900 border-amber-500/50'
          : 'bg-slate-900 border-cyan-500/50'"
        style="min-width: 160px; max-width: 220px;"
      >
        <!-- Avatar -->
        <div
          class="w-7 h-7 rounded-lg shrink-0 flex items-center justify-center text-[10px] font-bold text-white"
          :class="volunteer?.volunteer_type === 'Specialise'
            ? 'bg-amber-500/50 border border-amber-400/40'
            : 'bg-cyan-500/30 border border-cyan-400/30'"
        >
          {{ initials }}
        </div>
        <!-- Nom + type -->
        <div class="flex-1 min-w-0">
          <p class="text-xs font-semibold text-white truncate leading-tight">
            {{ volunteer ? `${volunteer.first_name} ${volunteer.last_name}` : '…' }}
          </p>
          <p class="text-[10px] leading-tight mt-0.5"
            :class="volunteer?.volunteer_type === 'Specialise' ? 'text-amber-400' : 'text-slate-400'">
            {{ volunteer?.volunteer_type === 'Specialise' ? 'Spécialisé' : 'Normal' }}
          </p>
        </div>
        <!-- Icône drag -->
        <GripVertical class="w-3.5 h-3.5 text-slate-500 shrink-0" />
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { GripVertical } from 'lucide-vue-next'
import { useDragState } from '../../composables/useDragState'
import { useBenevoles } from '../../composables/useBenevoles'
import { getInitials } from '../../utils/stringUtils'

const { dragState, isDragging } = useDragState()
const { volunteers } = useBenevoles()

const pos = ref({ x: -9999, y: -9999 })

const volunteer = computed(() => {
  if (!dragState.value?.volunteerId) return null
  return volunteers.value.find(v => v.id === dragState.value!.volunteerId) ?? null
})

const initials = computed(() => {
  if (!volunteer.value) return '?'
  return getInitials(`${volunteer.value.first_name} ${volunteer.value.last_name}`)
})

/**
 * L'API HTML5 DnD bloque mousemove pendant le drag.
 * dragover est le seul event portant clientX/clientY en continu.
 * On l'écoute sur window en phase CAPTURE (3e argument = true)
 * pour le recevoir avant tout preventDefault() des drop zones —
 * sans ça, l'event est stoppé par les enfants et ne remonte jamais.
 */
function onDragOver(e: DragEvent) {
  pos.value = { x: e.clientX, y: e.clientY }
}

function onDragEnd() {
  pos.value = { x: -9999, y: -9999 }
}

onMounted(() => {
  window.addEventListener('dragover', onDragOver, true)
  window.addEventListener('dragend',  onDragEnd,  true)
})
onUnmounted(() => {
  window.removeEventListener('dragover', onDragOver, true)
  window.removeEventListener('dragend',  onDragEnd,  true)
})
</script>