<template>
  <div class="flex flex-col gap-1.5">

    <p class="text-[10px] font-bold uppercase tracking-widest text-slate-600 px-1 mb-1">
      Variables
    </p>

    <div class="mt-2 flex items-start gap-2 px-3 py-2.5 rounded-xl bg-slate-900/60 border border-white/5">
      <span class="mt-px text-slate-600 text-[13px] leading-none">💡</span>
      <p class="text-[10px] text-slate-600 leading-relaxed">
        Cliquez sur une variable pour l'insérer à la position du curseur.
      </p>
    </div>

    <!-- Groupes par catégorie -->
    <template v-for="group in groups" :key="group.id">
      <!-- En-tête de groupe -->
      <div class="flex items-center gap-2 px-1 mt-2 mb-0.5 first:mt-0">
        <component :is="group.icon" class="w-3 h-3" :class="group.color" />
        <span class="text-[9px] font-bold uppercase tracking-widest" :class="group.color">
          {{ group.label }}
        </span>
      </div>

      <button
        v-for="variable in group.variables"
        :key="variable.key"
        class="group relative flex flex-col gap-1 px-3 py-2.5 rounded-xl border border-transparent
               bg-slate-800/50 hover:bg-slate-800 transition-all duration-150 text-left w-full overflow-hidden"
        :class="group.hoverBorder"
        :title="variable.description"
        @click="$emit('insert', variable.key)"
      >
        <!-- Accent glow -->
        <span
          class="pointer-events-none absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-150"
          :style="group.glow"
        />

        <!-- Tag + label -->
        <span class="flex items-center gap-2">
          <span
            class="shrink-0 font-mono text-[10px] px-1.5 py-0.5 rounded-md border leading-none transition-colors"
            :class="group.tagClass"
          >
            {{ variable.key }}
          </span>
          <span class="text-[11px] font-semibold text-slate-300 group-hover:text-white transition-colors leading-tight truncate">
            {{ variable.label }}
          </span>
        </span>

        <!-- Description -->
        <span class="flex items-baseline gap-1.5 pl-0.5">
          <span class="text-[10px] text-slate-500 leading-snug">
            {{ variable.description }}
          </span>
        </span>

        <!-- Exemple -->
        <span class="pl-0.5 flex items-center gap-1">
          <span class="text-[9px] uppercase tracking-wide text-slate-600 font-semibold">ex.</span>
          <span class="text-[10px] font-mono text-slate-500 italic truncate">{{ variable.example }}</span>
        </span>

        <!-- Insert hint -->
        <span
          class="absolute right-2.5 top-1/2 -translate-y-1/2 text-[9px] font-semibold uppercase
                 tracking-widest opacity-0 group-hover:opacity-100 transition-opacity duration-150"
          :class="group.hintColor"
        >
          Insérer ↵
        </span>
      </button>
    </template>


  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { User, Calendar, MapPin } from 'lucide-vue-next'
import { TEMPLATE_VARIABLES } from '../../composables/useMailTemplate'

defineEmits<{
  insert: [key: string]
}>()

const groups = computed(() => [
  {
    id:          'volunteer',
    label:       'Bénévole',
    icon:        User,
    color:       'text-cyan-500',
    hoverBorder: 'hover:border-cyan-500/25',
    hintColor:   'text-cyan-500',
    tagClass:    'bg-cyan-950/80 text-cyan-400 border-cyan-800/40 group-hover:bg-cyan-900/70 group-hover:border-cyan-600/40',
    glow:        'background: radial-gradient(ellipse at 0% 50%, rgba(6,182,212,0.07) 0%, transparent 70%)',
    variables:   TEMPLATE_VARIABLES.filter(v => v.category === 'volunteer'),
  },
  {
    id:          'planning',
    label:       'Planning',
    icon:        Calendar,
    color:       'text-emerald-500',
    hoverBorder: 'hover:border-emerald-500/25',
    hintColor:   'text-emerald-500',
    tagClass:    'bg-emerald-950/80 text-emerald-400 border-emerald-800/40 group-hover:bg-emerald-900/70 group-hover:border-emerald-600/40',
    glow:        'background: radial-gradient(ellipse at 0% 50%, rgba(16,185,129,0.07) 0%, transparent 70%)',
    variables:   TEMPLATE_VARIABLES.filter(v => v.category === 'planning'),
  },
  {
    id:          'festival',
    label:       'Festival',
    icon:        MapPin,
    color:       'text-violet-400',
    hoverBorder: 'hover:border-violet-500/25',
    hintColor:   'text-violet-400',
    tagClass:    'bg-violet-950/80 text-violet-400 border-violet-800/40 group-hover:bg-violet-900/70 group-hover:border-violet-600/40',
    glow:        'background: radial-gradient(ellipse at 0% 50%, rgba(139,92,246,0.07) 0%, transparent 70%)',
    variables:   TEMPLATE_VARIABLES.filter(v => v.category === 'festival'),
  },
])
</script>