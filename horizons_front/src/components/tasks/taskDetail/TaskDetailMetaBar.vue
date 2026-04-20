<template>
  <div class="shrink-0 bg-slate-900/60 flex flex-col">
    
    <div class="border-b border-white/6 px-5 flex items-center gap-4 overflow-x-auto custom-scrollbar" style="min-height: 52px;">
      
      <div class="flex items-center gap-2 shrink-0">
        <UserRound class="w-3.5 h-3.5 text-slate-500 shrink-0" />
        <span class="text-[11px] text-slate-500 font-medium shrink-0">Assigné</span>
        <UserPicker :users="users" :value="assignee" @select="emit('assignee', $event)" />
      </div>

      <Sep />

      <template v-for="p in priorities" :key="p.value">
        <button
          v-if="priority === p.value"
          @click="emit('priority', priorities[(priorities.findIndex(x=>x.value===p.value)+1)%priorities.length]!.value)"
          class="flex items-center gap-1.5 px-2 py-1.5 rounded-md text-xs border transition-all hover:opacity-80 shrink-0"
          :class="p.active"
        ><component :is="p.icon" class="w-3 h-3" />{{ p.label }}</button>
      </template>

      <Sep />

      <div class="flex items-center gap-2 shrink-0">
        <CalendarDays class="w-3.5 h-3.5 text-slate-500 shrink-0" />
        <input id="date-input2" type="date" :value="dueDate ?? ''" @blur="onDueDateBlur"
          class="bg-transparent text-sm outline-none cursor-pointer shrink-0 w-26"
          style="color-scheme: dark;"
          :class="dueDate ? 'text-slate-300 hover:text-white' : 'text-slate-500 hover:text-slate-400'" />
      </div>

      <Sep />

      <div class="flex gap-1.5 shrink-0">
        <button v-for="t in types" :key="t.value"
          @click="emit('type', t.value)"
          class="px-3 py-1.5 rounded-md text-xs border transition-all font-medium"
          :class="taskType === t.value ? t.active : 'border-transparent text-slate-600 hover:text-slate-400'"
        >{{ t.label }}</button>
      </div>

      <div class="shrink-0 ml-auto pl-4">
        <span class="text-[11px] text-slate-500 whitespace-nowrap">Créé le {{ fmtDate(createdAt) }}</span>
      </div>
    </div>

    <div class="border-b border-white/6 px-5 py-3 flex flex-wrap items-center gap-2 min-h-12">
      
      <TagChip
        v-for="tag in tags" :key="tag.id"
        :tag="tag"
        class="cursor-pointer hover:opacity-50 transition-opacity shrink-0"
        @click.native="emit('removeTag', tag.id)"
      />
      
      <div class="relative shrink-0" ref="tagBtnWrapRef">
        <button ref="tagBtnRef" @click="toggleTagPicker"
          class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs border border-dashed border-white/15 text-slate-500 hover:text-white hover:border-white/30 transition-all"
        ><Plus class="w-3 h-3" />Tag</button>

        <Teleport to="body">
          <div v-if="showTagPicker"
            class="fixed z-9999 bg-slate-800 border border-white/10 rounded-xl p-2 flex flex-col gap-0.5 shadow-2xl min-w-44"
            :style="tagPickerPos" @click.stop @mousedown.stop>
            <button v-for="tag in availableTags" :key="tag.id"
              @click="emit('addTag', tag); showTagPicker = false"
              class="flex items-center gap-2 px-2 py-1.5 rounded-lg text-sm hover:bg-white/5 text-left transition-colors">
              <div class="w-2.5 h-2.5 rounded-full shrink-0" :style="{ background: tag.color }" />
              <span class="text-slate-300">{{ tag.name }}</span>
            </button>
            <div v-if="availableTags.length" class="border-t border-white/10 mt-1 pt-1" />
            <div class="flex items-center gap-2 px-2 py-1.5">
              <input id="add-tag-name" v-model="newTagName" type="text" placeholder="Nouveau tag…"
                class="flex-1 bg-transparent text-sm text-slate-300 outline-none placeholder-slate-600 min-w-0"
                @keydown.enter.prevent="submitNewTag" />
              <input id="color-input4" type="color" v-model="newTagColor" class="w-5 h-5 rounded cursor-pointer bg-transparent border-0 p-0 shrink-0" />
              <button v-if="newTagName.trim()" @click="submitNewTag"
                class="text-xs text-cyan-400 hover:text-cyan-300 font-medium transition-colors">↵</button>
            </div>
          </div>
        </Teleport>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onUnmounted } from 'vue'
import { UserRound, CalendarDays, Plus, ArrowDown, Minus, ArrowUp, Zap } from 'lucide-vue-next'
import type { User, Tag, TaskPriority, TaskType } from '../../../types/task.types'
import UserPicker from './UserPicker.vue'
import TagChip from '../tags/TagChip.vue'
import { defineComponent, h } from 'vue'

const Sep = defineComponent({ render: () => h('div', { class: 'w-px h-4 bg-white/10 mx-0.5 shrink-0' }) })

const props = defineProps<{
  users: User[]
  assignee?: User
  priority: TaskPriority
  tags: Tag[]
  availableTags: Tag[]
  dueDate?: string
  taskType: TaskType
  createdAt: string
}>()

const emit = defineEmits<{
  assignee:  [user: User | null]
  priority:  [p: TaskPriority]
  addTag:    [tag: Tag]
  removeTag: [id: number]
  newTag:    [name: string, color: string]
  type:      [t: TaskType]
  dueDate:   [val: string | undefined]
}>()

const tagBtnRef      = ref<HTMLElement | null>(null)
const tagBtnWrapRef  = ref<HTMLElement | null>(null)
const tagPickerPos   = ref({ top: '0px', left: '0px' })
const showTagPicker  = ref(false)
const newTagName     = ref('')
const newTagColor    = ref('#22d3ee')

const toggleTagPicker = () => {
  if (!showTagPicker.value && tagBtnRef.value) {
    const r = tagBtnRef.value.getBoundingClientRect()
    tagPickerPos.value = { top: `${r.bottom + 6}px`, left: `${r.left}px` }
  }
  showTagPicker.value = !showTagPicker.value
}

const handleClickOutside = (e: MouseEvent) => {
  if (!showTagPicker.value) return
  if (tagBtnWrapRef.value?.contains(e.target as Node)) return
  showTagPicker.value = false
}

document.addEventListener('mousedown', handleClickOutside)
onUnmounted(() => document.removeEventListener('mousedown', handleClickOutside))

const submitNewTag = () => {
  if (!newTagName.value.trim()) return
  emit('newTag', newTagName.value.trim(), newTagColor.value)
  newTagName.value    = ''
  newTagColor.value   = '#22d3ee'
  showTagPicker.value = false
}

const onDueDateBlur = (e: FocusEvent) => {
  const val  = (e.target as HTMLInputElement).value
  if (!val) { emit('dueDate', undefined); return }
  const year = val.split('-')[0] ?? ''
  if (year.length < 4) return
  emit('dueDate', val)
}

const fmtDate = (iso: string) =>
  new Date(iso).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })

const priorities = [
  { value: 'low'      as const, label: 'Basse',    icon: ArrowDown, active: 'border-slate-500/40 bg-slate-500/10 text-slate-300' },
  { value: 'medium'   as const, label: 'Moyenne',  icon: Minus,     active: 'border-blue-500/40 bg-blue-500/10 text-blue-300' },
  { value: 'high'     as const, label: 'Haute',    icon: ArrowUp,   active: 'border-amber-500/40 bg-amber-500/10 text-amber-300' },
  { value: 'critical' as const, label: 'Critique', icon: Zap,       active: 'border-red-500/40 bg-red-500/10 text-red-300' },
]
const types = [
  { value: 'standard'     as const, label: 'Standard', active: 'border-slate-500/40 bg-slate-500/10 text-slate-300' },
  { value: 'needs_review' as const, label: 'Vérification',   active: 'border-violet-500/40 bg-violet-500/10 text-violet-300' },
]
</script>