<template>
  <div class="flex-1 flex flex-col gap-2 min-w-0">

    <div class="flex items-center justify-between">
      <span class="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
        <template v-if="preference">
          Pôles —
          <span class="text-cyan-400 normal-case font-normal tracking-normal">{{ preference.label }}</span>
        </template>
        <template v-else>Pôles</template>
      </span>
      <span v-if="preference" class="text-[10px] text-slate-600">
        {{ preference.categories.length }} pôle{{ preference.categories.length > 1 ? 's' : '' }}
      </span>
    </div>

    <!-- Ajout — ENTER suffit -->
    <div v-if="preference" class="flex gap-2">
      <input id="edit-pref1"
        v-model="newLabel"
        type="text"
        placeholder="Nom du pôle…"
        class="flex-1 min-w-0 h-8 px-3 rounded-lg bg-slate-900/50 border border-white/10 text-slate-200 text-xs placeholder:text-slate-600 outline-none focus:border-cyan-500/40 focus:bg-slate-900/80 transition-all"
        @keyup.enter="handleCreate"
      />
      <div class="group/tip relative">
        <input id="edit-pref2"
          v-model.number="newPoleId"
          type="number"
          placeholder="id"
          class="w-16 h-8 px-2 rounded-lg bg-slate-900/50 border border-white/10 text-cyan-400 font-mono text-xs placeholder:text-slate-600 outline-none focus:border-cyan-500/40 transition-all"
          @keyup.enter="handleCreate"
        />
        <span class="pointer-events-none absolute bottom-full left-1/2 -translate-x-1/2 mb-1.5 px-2 py-1 rounded-lg bg-slate-700 border border-white/10 text-[10px] text-slate-300 whitespace-nowrap opacity-0 group-hover/tip:opacity-100 transition-opacity z-10">
          ID famille de pôle (optionnel)
        </span>
      </div>
      <button
        class="shrink-0 w-8 h-8 flex items-center justify-center rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 hover:bg-cyan-500/20 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
        :disabled="!newLabel.trim()"
        title="Ajouter (Entrée)"
        @click="handleCreate"
      >
        <Plus class="w-3.5 h-3.5" />
      </button>
    </div>

    <!-- Placeholder -->
    <div v-if="!preference" class="flex-1 flex flex-col items-center justify-center gap-2 text-slate-700">
      <LayoutGrid class="w-7 h-7 opacity-40" />
      <p class="text-xs">Sélectionnez un groupe</p>
    </div>

    <!-- Liste -->
    <div v-else class="flex flex-col gap-0.5 flex-1 overflow-y-auto">
      <p v-if="sortedCategories.length === 0" class="text-center py-8 text-slate-600 text-xs">
        Aucun pôle dans ce groupe
      </p>
      <CategoryItem
        v-for="cat in sortedCategories"
        :key="cat.id"
        :category="cat"
        :other-preferences="otherPreferences"
        @update="$emit('update', $event.id, $event.label, $event.poleId)"
        @delete="$emit('delete', $event)"
        @move="$emit('move', $event.cat, $event.toPreferenceId)"
      />
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Plus, LayoutGrid } from 'lucide-vue-next'
import type { Preference, Category } from '../../../../types/planning.types'
import CategoryItem from './CategoryItem.vue'

const props = defineProps<{ preference: Preference | null; otherPreferences: Preference[] }>()
const emit  = defineEmits<{
  create: [label: string, poleId: number | null]
  update: [id: number, label: string, poleId: number | null]
  delete: [cat: Category]
  move:   [cat: Category, toPreferenceId: number]
}>()

const newLabel  = ref('')
const newPoleId = ref<number | null>(null)

//sort by pole_id
const sortedCategories = computed(() =>
  props.preference
    ? [...props.preference.categories].sort((a, b) => (a.pole_id ?? 0) - (b.pole_id ?? 0) || a.label.localeCompare(b.label))
    : []
)

const handleCreate = () => {
  if (!newLabel.value.trim()) return
  emit('create', newLabel.value.trim(), newPoleId.value)
  newLabel.value  = ''
  newPoleId.value = null
}
</script>