<template>
  <section class="bg-slate-700/30 rounded-xl p-3 border border-slate-600/40">
    <div class="flex items-center justify-between mb-3">
      <h3 class="text-sm font-semibold text-white flex items-center gap-2">
        <Star class="w-4 h-4 text-purple-400" />
        Préférences
        <span class="text-slate-400 text-xs font-normal">({{ volunteer.preferences.length }})</span>
      </h3>
      <button
        @click="$emit('toggle-edit')"
        class="p-1.5 rounded-lg transition-colors"
        :class="isEditing ? 'bg-purple-500/20 text-purple-300' : 'hover:bg-slate-600 text-slate-400'"
      >
        <Pencil class="w-3.5 h-3.5" />
      </button>
    </div>

    <!-- Lecture -->
    <div v-if="!isEditing" class="flex flex-wrap gap-1.5">
      <span
        v-for="pref in sortedPreferences" :key="pref.preference.id"
        class="px-2.5 py-1 bg-purple-500/20 text-purple-300 rounded-full text-xs font-medium border border-purple-500/30 flex items-center gap-1.5"
      >
        <span class="text-purple-400 font-bold">{{ pref.rank }}.</span>
        {{ pref.preference.label }}
      </span>
      <p v-if="!volunteer.preferences.length" class="text-slate-400 text-xs">Aucune préférence</p>
    </div>

    <!-- Édition drag & drop -->
    <div v-else>
      <p class="text-xs text-slate-400 mb-2 flex items-center gap-1">
        <GripVertical class="w-3 h-3" /> Glisser pour réordonner
      </p>
      <div class="space-y-1.5">
        <div
          v-for="(pref, index) in editPrefs" :key="pref.preference.id"
          draggable="true"
          @dragstart="$emit('drag-start', index)"
          @dragover.prevent="$emit('drag-over', index)"
          @dragend="$emit('drag-end')"
          class="flex items-center gap-2 bg-slate-700 border rounded-lg px-2.5 py-2 cursor-grab active:cursor-grabbing transition-all select-none"
          :class="dragOverIndex === index ? 'border-purple-400 bg-slate-600' : 'border-slate-600 hover:border-slate-500'"
        >
          <GripVertical class="w-4 h-4 text-slate-500 shrink-0" />
          <span class="w-5 h-5 rounded-full bg-purple-500/30 text-purple-300 text-xs font-bold flex items-center justify-center shrink-0">
            {{ index + 1 }}
          </span>
          <span class="text-sm text-white">{{ pref.preference.label }}</span>
        </div>
      </div>
      <div class="flex gap-2 mt-3">
        <button
          @click="$emit('save')"
          :disabled="isSaving"
          class="flex-1 flex items-center justify-center gap-1 bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white text-xs font-medium py-1.5 rounded-lg transition-colors"
        >
          <Loader2 v-if="isSaving" class="w-3 h-3 animate-spin" /><Check v-else class="w-3 h-3" />
          Enregistrer
        </button>
        <button
          @click="$emit('cancel')"
          class="flex-1 bg-slate-600 hover:bg-slate-500 text-slate-300 text-xs font-medium py-1.5 rounded-lg transition-colors"
        >
          Annuler
        </button>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Star, Pencil, GripVertical, Check, Loader2 } from 'lucide-vue-next'
import type { Volunteer, VolunteerPreference } from '../../../types/benevole.types'

const props = defineProps<{
  volunteer:     Volunteer
  isEditing:     boolean
  isSaving:      boolean
  editPrefs:     VolunteerPreference[]
  dragOverIndex: number | null
}>()

defineEmits<{
  'toggle-edit': []
  'save':        []
  'cancel':      []
  'drag-start':  [index: number]
  'drag-over':   [index: number]
  'drag-end':    []
}>()

const sortedPreferences = computed<VolunteerPreference[]>(() =>
  [...props.volunteer.preferences].sort((a, b) => a.rank - b.rank)
)
</script>