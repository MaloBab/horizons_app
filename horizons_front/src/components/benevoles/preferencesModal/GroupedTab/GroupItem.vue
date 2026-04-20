<template>
  <div
    class="group flex items-center gap-2 px-3 h-8 rounded-lg border cursor-pointer select-none transition-colors"
    :class="isSelected
      ? 'bg-cyan-500/10 border-cyan-500/20 text-white'
      : 'bg-white/3 border-white/5 hover:bg-white/5 hover:border-white/10 text-slate-300'"
    @click="$emit('select', preference)"
  >
    <div
      class="w-1.5 h-1.5 rounded-full shrink-0 transition-colors"
      :class="isSelected ? 'bg-cyan-400' : 'bg-slate-600'"
    />

    <input id="rename"
      v-if="isRenaming"
      ref="renameInput"
      v-model="renamingLabel"
      class="flex-1 min-w-0 bg-slate-700 border border-cyan-500/30 rounded px-1.5 py-px text-slate-100 text-xs outline-none"
      @keyup.enter="confirmRename"
      @keyup.escape="isRenaming = false"
      @click.stop
    />
    <span v-else class="flex-1 min-w-0 text-xs font-medium truncate">{{ preference.label }}</span>

    <span class="shrink-0 text-[10px] text-slate-600 tabular-nums">{{ preference.categories.length }}</span>

    <div class="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity" @click.stop>
      <button
        v-if="isRenaming"
        class="w-5 h-5 flex items-center justify-center rounded text-emerald-400 hover:bg-emerald-500/15 transition-colors"
        @click="confirmRename"
      ><Check class="w-3 h-3" /></button>
      <template v-else>
        <button
          class="w-5 h-5 flex items-center justify-center rounded text-slate-500 hover:text-slate-200 hover:bg-white/10 transition-colors"
          @click="startRename"
        ><Pencil class="w-3 h-3" /></button>
        <button
          class="w-5 h-5 flex items-center justify-center rounded text-slate-500 hover:text-red-400 hover:bg-red-500/10 transition-colors"
          @click="$emit('delete', preference)"
        ><Trash2 class="w-3 h-3" /></button>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { Check, Pencil, Trash2 } from 'lucide-vue-next'
import type { Preference } from '../../../../types/planning.types'

const props = defineProps<{ preference: Preference; isSelected: boolean }>()
const emit  = defineEmits<{
  select: [pref: Preference]
  rename: [payload: { id: number; label: string }]
  delete: [pref: Preference]
}>()

const isRenaming    = ref(false)
const renamingLabel = ref('')
const renameInput   = ref<HTMLInputElement | null>(null)

const startRename = async () => {
  renamingLabel.value = props.preference.label
  isRenaming.value    = true
  await nextTick()
  renameInput.value?.focus()
  renameInput.value?.select()
}

const confirmRename = () => {
  if (!renamingLabel.value.trim()) return
  emit('rename', { id: props.preference.id, label: renamingLabel.value.trim() })
  isRenaming.value = false
}
</script>