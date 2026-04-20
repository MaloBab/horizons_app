<template>
  <div class="flex items-center justify-between px-6 py-4 border-b border-white/10 shrink-0">
    <div class="flex items-center gap-3">

      <button
        class="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium border transition-all"
        :class="[statusStyle.cls, canClose ? 'hover:opacity-80' : 'cursor-not-allowed opacity-60']"
        :title="!canClose ? 'Seul un autre utilisateur peut fermer cette tâche' : ''"
        @click="emit('cycleStatus')"
      >
        <component :is="statusStyle.icon" class="w-3.5 h-3.5" />
        {{ statusStyle.label }}
        <Lock v-if="!canClose" class="w-3 h-3 opacity-60" />
      </button>

      <!-- Prochain statut -->
      <div class="flex items-center gap-1.5 text-xs text-slate-600">
        <ArrowRight class="w-3 h-3" />
        <component :is="nextStyle.icon" class="w-3 h-3"/>
        <span>{{ nextStyle.label }}</span>
      </div>

    </div>

    <div class="flex items-center gap-2">
      <Transition name="fade">
        <span v-if="isSaving" class="text-xs text-slate-500 flex items-center gap-1.5">
          <div class="w-3 h-3 rounded-full border-2 border-cyan-500/40 border-t-cyan-400 animate-spin" />
          Sauvegarde...
        </span>
        <span v-else-if="savedAt" class="text-xs text-emerald-400">✓ Sauvegardé</span>
      </Transition>
      <button @click="emit('close')" class="p-2 rounded-lg text-slate-500 hover:text-white hover:bg-white/10 transition-all">
        <X class="w-4 h-4" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { X, Circle, Eye, CheckCircle2, Lock, ArrowRight } from 'lucide-vue-next'
import type { User, TaskStatus, TaskType } from '../../../types/task.types'

const props = defineProps<{
  taskId:   string
  status:   TaskStatus
  taskType: TaskType
  assignee?: User
  canClose: boolean
  isSaving: boolean
  savedAt:  boolean
}>()

const emit = defineEmits<{ close: []; cycleStatus: [] }>()

const STATUS_MAP: Record<TaskStatus, { label: string; icon: any; cls: string; textCls: string }> = {
  open:   { label: 'Ouvert',     icon: Circle,       cls: 'border-cyan-500/40 bg-cyan-500/10 text-cyan-300',       textCls: 'text-cyan-400/60'    },
  review: { label: 'À Vérifier', icon: Eye,          cls: 'border-violet-500/40 bg-violet-500/10 text-violet-300', textCls: 'text-violet-400/60'  },
  closed: { label: 'Fermé',      icon: CheckCircle2, cls: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300', textCls: 'text-emerald-400/60' },
}

const CYCLE_STANDARD:    TaskStatus[] = ['open', 'closed']
const CYCLE_NEEDS_REVIEW: TaskStatus[] = ['open', 'review', 'closed']

const statusStyle = computed(() => STATUS_MAP[props.status] ?? STATUS_MAP.open)

const nextStatus = computed<TaskStatus>(() => {
  const cycle = props.taskType === 'needs_review' ? CYCLE_NEEDS_REVIEW : CYCLE_STANDARD
  const idx   = cycle.indexOf(props.status)
  return cycle[(idx + 1) % cycle.length]!
})

const nextStyle = computed(() => STATUS_MAP[nextStatus.value])
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from,   .fade-leave-to     { opacity: 0; }
</style>