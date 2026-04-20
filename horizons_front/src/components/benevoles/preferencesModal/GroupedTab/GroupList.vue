<template>
  <div class="w-5/12 flex flex-col gap-2 min-w-0">

    <div class="flex items-center justify-between">
      <span class="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Groupes</span>
      <span class="text-[10px] text-slate-600">{{ preferences.length }}</span>
    </div>

    <!-- Création — ENTER suffit -->
    <div class="flex gap-2">
      <input id="create-group"
        v-model="newLabel"
        type="text"
        placeholder="Nouveau groupe…"
        class="flex-1 min-w-0 h-8 px-3 rounded-lg bg-slate-900/50 border border-white/10 text-slate-200 text-xs placeholder:text-slate-600 outline-none focus:border-cyan-500/40 focus:bg-slate-900/80 transition-all"
        @keyup.enter="handleCreate"
      />
      <button
        class="shrink-0 w-8 h-8 flex items-center justify-center rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 hover:bg-cyan-500/20 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
        :disabled="!newLabel.trim() || isLoading"
        title="Créer (Entrée)"
        @click="handleCreate"
      >
        <Plus class="w-3.5 h-3.5" />
      </button>
    </div>

    <!-- Liste -->
    <div class="flex flex-col gap-0.5 flex-1 overflow-y-auto">

      <div v-if="isLoading" class="flex flex-col items-center justify-center gap-2 py-10 text-slate-600 text-[11px]">
        <Loader2 class="w-4 h-4 animate-spin" />
        Chargement…
      </div>

      <p v-else-if="preferences.length === 0" class="text-center py-10 text-slate-600 text-xs">
        Aucun groupe défini
      </p>

      <template v-else>
        <GroupItem
          v-for="pref in preferences"
          :key="pref.id"
          :preference="pref"
          :is-selected="selectedId === pref.id"
          @select="$emit('select', $event)"
          @rename="$emit('rename', $event)"
          @delete="$emit('delete', $event)"
        />
      </template>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Plus, Loader2 } from 'lucide-vue-next'
import type { Preference } from '../../../../types/planning.types'
import GroupItem from './GroupItem.vue'

defineProps<{ preferences: Preference[]; isLoading: boolean; selectedId: number | null }>()

const emit = defineEmits<{
  select: [pref: Preference]
  create: [label: string]
  rename: [payload: { id: number; label: string }]
  delete: [pref: Preference]
}>()

const newLabel = ref('')

const handleCreate = () => {
  if (!newLabel.value.trim()) return
  emit('create', newLabel.value.trim())
  newLabel.value = ''
}
</script>