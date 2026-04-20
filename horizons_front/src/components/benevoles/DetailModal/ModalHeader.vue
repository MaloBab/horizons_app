<template>
  <div class="bg-linear-to-r from-blue-600 to-purple-600 px-6 py-4 flex items-center justify-between shrink-0">
    <div class="flex items-center gap-3">
      <div class="w-12 h-12 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center text-white font-bold text-lg">
        {{ volunteer.first_name[0] }}{{ volunteer.last_name[0] }}
      </div>
      <div>
        <h2 class="text-xl font-bold text-white">{{ volunteer.first_name }} {{ volunteer.last_name }}</h2>
        <span
          class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium mt-1"
          :class="volunteer.volunteer_type === 'Specialise'
            ? 'bg-amber-500/30 text-amber-300'
            : 'bg-slate-500/30 text-slate-300'"
        >
          {{ volunteer.volunteer_type === 'Specialise' ? 'Bénévole spécialisé' : 'Bénévole normal' }}
        </span>
      </div>
    </div>
    <button @click="$emit('close')" class="p-2 hover:bg-white/20 rounded-lg transition-colors">
      <X class="w-5 h-5 text-white" />
    </button>
  </div>
</template>

<script setup lang="ts">
import { X } from 'lucide-vue-next'
import type { Volunteer } from '../../../types/benevole.types'

defineProps<{ volunteer: Volunteer }>()
defineEmits<{ close: [] }>()
</script>