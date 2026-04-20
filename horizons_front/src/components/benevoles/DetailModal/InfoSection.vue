<template>
  <section class="bg-slate-700/30 rounded-xl p-3 border border-slate-600/40">
    <div class="flex items-center justify-between mb-3">
      <h3 class="text-sm font-semibold text-white flex items-center gap-2">
        <User class="w-4 h-4 text-blue-400" />
        Informations personnelles
      </h3>
      <button
        @click="$emit('toggle-edit')"
        class="p-1.5 rounded-lg transition-colors"
        :class="isEditing ? 'bg-blue-500/20 text-blue-300' : 'hover:bg-slate-600 text-slate-400'"
      >
        <Pencil class="w-3.5 h-3.5" />
      </button>
    </div>

    <!-- Lecture -->
    <div v-if="!isEditing" class="space-y-2">
      <InfoField label="Email"     :value="volunteer.email"        icon="mail"    />
      <InfoField label="Téléphone" :value="volunteer.phone_number" icon="phone"   />
      <InfoField label="Adresse"   :value="volunteer.address"      icon="map-pin" />
    </div>

    <!-- Édition -->
    <div v-else class="space-y-2">
      <div>
        <label class="text-xs text-slate-400 mb-1 block">Email</label>
        <input id="edit-email"
          :value="modelEmail"
          @input="$emit('update:model-email', ($event.target as HTMLInputElement).value)"
          type="email"
          class="w-full bg-slate-700 border border-slate-500 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-400 transition-colors"
        />
      </div>
      <div>
        <label class="text-xs text-slate-400 mb-1 block">Téléphone</label>
        <input id="edit-tel"
          :value="modelPhone"
          @input="$emit('update:model-phone', ($event.target as HTMLInputElement).value)"
          type="text"
          class="w-full bg-slate-700 border border-slate-500 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-400 transition-colors"
        />
      </div>
      <div class="flex gap-2 pt-1">
        <button
          @click="$emit('save')"
          :disabled="isSaving"
          class="flex-1 flex items-center justify-center gap-1 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-medium py-1.5 rounded-lg transition-colors"
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
import { User, Pencil, Check, Loader2 } from 'lucide-vue-next'
import type { Volunteer } from '../../../types/benevole.types'
import InfoField from '../InfoField.vue'

defineProps<{
  volunteer:   Volunteer
  isEditing:   boolean
  isSaving:    boolean
  modelEmail:  string
  modelPhone:  string
}>()

defineEmits<{
  'toggle-edit':        []
  'save':               []
  'cancel':             []
  'update:model-email': [value: string]
  'update:model-phone': [value: string]
}>()
</script>