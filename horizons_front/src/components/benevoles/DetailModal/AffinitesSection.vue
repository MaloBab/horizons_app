<template>
  <section class="bg-slate-700/30 rounded-xl p-3 border border-slate-600/40 flex flex-col min-h-0">
    <div class="flex items-center justify-between mb-3 shrink-0">
      <h3 class="text-sm font-semibold text-white flex items-center gap-2">
        <Heart class="w-4 h-4 text-pink-400" />
        Affinités
        <span class="text-slate-400 text-xs font-normal">({{ volunteer.mates.length }})</span>
      </h3>
      <button
        @click="$emit('toggle-edit')"
        class="p-1.5 rounded-lg transition-colors"
        :class="isEditing ? 'bg-pink-500/20 text-pink-300' : 'hover:bg-slate-600 text-slate-400'"
      >
        <Pencil class="w-3.5 h-3.5" />
      </button>
    </div>

    <!-- Liste des mates existants -->
    <div
      class="space-y-1.5 overflow-y-auto custom-scrollbar shrink-0"
      :class="isEditing ? 'max-h-48' : 'max-h-64'"
    >
      <div
        v-for="mate in volunteer.mates" :key="mate.id"
        class="flex items-center gap-2 bg-slate-700/50 rounded-lg p-2 border transition-colors"
        :class="isEditing ? 'border-slate-600/50 hover:border-red-500/30' : 'border-slate-600/50'"
      >
        <div class="w-7 h-7 rounded-full bg-linear-to-br from-pink-500 to-purple-600 flex items-center justify-center text-white font-bold text-xs shrink-0">
          {{ mate.first_name[0] }}{{ mate.last_name[0] }}
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-white text-xs font-medium truncate">{{ mate.first_name }} {{ mate.last_name }}</p>
          <p class="text-slate-400 text-xs truncate">{{ mate.email }}</p>
        </div>
        <button
          v-if="isEditing"
          @click="$emit('remove-mate', mate.id)"
          :disabled="loadingMateId === mate.id"
          class="p-1 rounded-md hover:bg-red-500/20 text-slate-500 hover:text-red-400 transition-colors shrink-0"
        >
          <Loader2 v-if="loadingMateId === mate.id" class="w-3.5 h-3.5 animate-spin" />
          <Trash2 v-else class="w-3.5 h-3.5" />
        </button>
      </div>
      <p v-if="!volunteer.mates.length" class="text-slate-400 text-xs py-1">Aucune affinité</p>
    </div>

    <!-- Zone ajout (mode édition) -->
    <div v-if="isEditing" class="border-t border-slate-600/50 pt-3 mt-3 shrink-0">
      <p class="text-xs text-slate-400 mb-2 flex items-center gap-1.5">
        <UserPlus class="w-3.5 h-3.5" /> Ajouter une affinité
      </p>

      <div class="relative">
        <div class="relative">
          <Search class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400 pointer-events-none" />
          <input id="search-for-affinity"
            :value="searchQuery"
            @input="$emit('update:search-query', ($event.target as HTMLInputElement).value)"
            type="text"
            autocomplete="off"
            placeholder="Rechercher par nom ou email..."
            class="w-full bg-slate-700 border border-slate-500 rounded-lg pl-8 pr-3 py-2 text-sm text-white focus:outline-none focus:border-pink-400 transition-colors"
            @focus="$emit('search-focus')"
            @blur="$emit('search-blur')"
          />
        </div>

        <!-- Dropdown vers le haut -->
        <div
          v-if="showDropdown && candidates.length > 0"
          class="absolute left-0 right-0 bottom-full mb-1 bg-slate-700 border border-slate-500 rounded-lg overflow-hidden max-h-44 overflow-y-auto custom-scrollbar shadow-xl z-10"
        >
          <button
            v-for="candidate in candidates" :key="candidate.id"
            @mousedown.prevent
            @click="$emit('add-mate', candidate)"
            :disabled="loadingMateId === candidate.id"
            class="w-full flex items-center gap-2 px-3 py-2 hover:bg-slate-600 transition-colors text-left"
          >
            <div class="w-6 h-6 rounded-full bg-linear-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-xs shrink-0">
              {{ candidate.first_name[0] }}{{ candidate.last_name[0] }}
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-white text-xs font-medium truncate">{{ candidate.first_name }} {{ candidate.last_name }}</p>
              <p class="text-slate-400 text-xs truncate">{{ candidate.email }}</p>
            </div>
            <Loader2 v-if="loadingMateId === candidate.id" class="w-3.5 h-3.5 animate-spin text-slate-400 shrink-0" />
            <Plus v-else class="w-3.5 h-3.5 text-pink-400 shrink-0" />
          </button>
        </div>

        <p
          v-else-if="showDropdown && searchQuery.length >= 1 && candidates.length === 0"
          class="absolute left-0 right-0 bottom-full mb-1 text-xs text-slate-400 text-center py-2 bg-slate-700 border border-slate-500 rounded-lg z-10"
        >
          Aucun bénévole trouvé
        </p>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { Heart, Pencil, Trash2, Loader2, UserPlus, Search, Plus } from 'lucide-vue-next'
import type { Volunteer } from '../../../types/benevole.types'

defineProps<{
  volunteer:     Volunteer
  isEditing:     boolean
  loadingMateId: string | null
  searchQuery:   string
  showDropdown:  boolean
  candidates:    Volunteer[]
}>()

defineEmits<{
  'toggle-edit':         []
  'remove-mate':         [mateId: string]
  'add-mate':            [candidate: Volunteer]
  'update:search-query': [value: string]
  'search-focus':        []
  'search-blur':         []
}>()
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar       { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #475569; border-radius: 2px; }
</style>