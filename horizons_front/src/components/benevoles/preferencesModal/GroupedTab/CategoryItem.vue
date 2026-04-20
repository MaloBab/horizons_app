<template>
  <div class="group flex items-center gap-2 px-3 h-8 bg-white/3 border border-white/5 rounded-lg hover:bg-white/5 hover:border-white/10 transition-colors">

    <input id="edit-cat1"
      v-if="isEditing"
      ref="editInput"
      v-model="editLabel"
      type="text"
      class="flex-1 min-w-0 bg-slate-700 border border-cyan-500/30 rounded px-1.5 py-px text-slate-100 text-xs outline-none"
      @keyup.enter="confirmUpdate"
      @keyup.escape="isEditing = false"
      @click.stop
    />
    <span v-else class="flex-1 min-w-0 text-xs text-slate-200 truncate">{{ category.label }}</span>

    <input id="edit-cat2"
      v-if="isEditing"
      v-model.number="editPoleId"
      type="number"
      placeholder="id"
      class="w-14 shrink-0 bg-slate-700 border border-cyan-500/20 rounded px-1.5 py-px text-cyan-400 font-mono text-xs outline-none"
      @keyup.enter="confirmUpdate"
      @keyup.escape="isEditing = false"
      @click.stop
    />
    <template v-else>
      <span
        v-if="category.pole_id != null"
        class="shrink-0 px-1.5 py-px rounded text-[10px] font-mono bg-cyan-500/5 text-cyan-500/70 border border-cyan-500/40"
      >{{ category.pole_id }}</span>
      <span v-else class="shrink-0 w-6 text-center text-[10px] font-mono text-slate-700">—</span>
    </template>

    <!-- Déplacer — ref sur le wrapper, listener natif en phase capture -->
    <div ref="moveWrapRef" class="relative">
      <button
        class="w-5 h-5 flex items-center justify-center rounded text-slate-600 hover:text-cyan-400 hover:bg-cyan-500/10 opacity-0 group-hover:opacity-100 transition-all"
        title="Déplacer vers un autre groupe"
        @click.stop="isMoveOpen = !isMoveOpen"
      >
        <ArrowRightLeft class="w-3 h-3" />
      </button>

      <Transition
        enter-active-class="transition-all duration-150 ease-out"
        leave-active-class="transition-all duration-100 ease-in"
        enter-from-class="opacity-0 -translate-y-1 scale-95"
        leave-to-class="opacity-0 -translate-y-1 scale-95"
      >
        <div
          v-if="isMoveOpen"
          class="absolute right-0 top-6 z-30 min-w-36 bg-slate-800 border border-white/10 rounded-xl shadow-2xl overflow-hidden py-1"
          @click.stop
        >
          <p class="px-3 py-1 text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Déplacer vers…</p>
          <button
            v-for="pref in otherPreferences"
            :key="pref.id"
            class="w-full text-left px-3 py-1.5 text-xs text-slate-300 hover:bg-white/5 hover:text-cyan-400 transition-colors"
            @click="handleMove(pref.id)"
          >{{ pref.label }}</button>
          <p v-if="otherPreferences.length === 0" class="px-3 py-1.5 text-xs text-slate-600">
            Aucun autre groupe
          </p>
        </div>
      </Transition>
    </div>

    <div class="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity" @click.stop>
      <button
        v-if="isEditing"
        class="w-5 h-5 flex items-center justify-center rounded text-emerald-400 hover:bg-emerald-500/15 transition-colors"
        @click="confirmUpdate"
      ><Check class="w-3 h-3" /></button>
      <button
        v-else
        class="w-5 h-5 flex items-center justify-center rounded text-slate-500 hover:text-slate-200 hover:bg-white/10 transition-colors"
        @click="startEdit"
      ><Pencil class="w-3 h-3" /></button>
      <button
        class="w-5 h-5 flex items-center justify-center rounded text-slate-500 hover:text-red-400 hover:bg-red-500/10 transition-colors"
        @click="$emit('delete', category)"
      ><Trash2 class="w-3 h-3" /></button>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { Check, Pencil, Trash2, ArrowRightLeft } from 'lucide-vue-next'
import type { Preference, Category } from '../../../../types/planning.types'

const props = defineProps<{ category: Category; otherPreferences: Preference[] }>()
const emit  = defineEmits<{
  update: [payload: { id: number; label: string; poleId: number | null }]
  delete: [cat: Category]
  move:   [payload: { cat: Category; toPreferenceId: number }]
}>()

const editInput   = ref<HTMLInputElement | null>(null)
const moveWrapRef = ref<HTMLElement | null>(null)
const isEditing   = ref(false)
const isMoveOpen  = ref(false)
const editLabel   = ref('')
const editPoleId  = ref<number | null>(null)

// Phase capture (3e arg = true) : intercepte AVANT tout @click.stop dans l'arbre
const onDocMousedown = (e: MouseEvent) => {
  if (isMoveOpen.value && moveWrapRef.value && !moveWrapRef.value.contains(e.target as Node)) {
    isMoveOpen.value = false
  }
}
onMounted(()       => document.addEventListener('mousedown', onDocMousedown, true))
onBeforeUnmount(() => document.removeEventListener('mousedown', onDocMousedown, true))

const startEdit = async () => {
  editLabel.value  = props.category.label
  editPoleId.value = props.category.pole_id ?? null
  isEditing.value  = true
  await nextTick()
  editInput.value?.focus()
  editInput.value?.select()
}

const confirmUpdate = () => {
  if (!editLabel.value.trim()) return
  emit('update', { id: props.category.id, label: editLabel.value.trim(), poleId: editPoleId.value })
  isEditing.value = false
}

const handleMove = (toPreferenceId: number) => {
  isMoveOpen.value = false
  emit('move', { cat: props.category, toPreferenceId })
}
</script>