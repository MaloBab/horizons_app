<template>
  <div class="bg-slate-800/50 backdrop-blur-sm border border-white/10 rounded-xl p-4">
    <div class="flex flex-wrap gap-3 items-center">

      <!-- Search -->
      <div class="relative flex-1 min-w-48">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
        <input id="search-planning" v-model="search" type="text" placeholder="Rechercher un poste..."
          class="w-full bg-slate-700/50 border border-white/10 rounded-lg pl-9 pr-4 py-2 text-sm text-white placeholder-slate-500 outline-none focus:border-cyan-500/50 focus:bg-slate-700 transition-all duration-200"
        />
        <button v-if="search" @click="search = ''" class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-white transition-colors">
          <X class="w-3.5 h-3.5" />
        </button>
      </div>

      <div class="w-px h-6 bg-white/10 hidden sm:block" />

      <!-- Jour -->
      <div class="relative">
        <button ref="dayTriggerRef" @click.stop="toggleDropdown('day')"
          class="flex items-center gap-2 px-3 py-2 bg-slate-700/50 border rounded-lg text-sm transition-all duration-200 hover:bg-slate-700"
          :class="selectedDay !== null ? 'border-cyan-500/50 text-cyan-300' : 'border-white/10 text-slate-300'"
        >
          <CalendarDays class="w-4 h-4" />
          <span>{{ selectedDay !== null ? festivalDays.find(d => d.day === selectedDay)?.label.split(' ').slice(0,2).join(' ') : 'Jour' }}</span>
          <ChevronDown class="w-3.5 h-3.5 text-slate-400 transition-transform duration-200" :class="openDropdown === 'day' ? 'rotate-180' : ''" />
        </button>
      </div>

      <!-- Pôle -->
      <div class="relative">
        <button ref="poleTriggerRef" @click.stop="toggleDropdown('pole')"
          class="flex items-center gap-2 px-3 py-2 bg-slate-700/50 border rounded-lg text-sm transition-all duration-200 hover:bg-slate-700"
          :class="selectedPoles.length ? 'border-cyan-500/50 text-cyan-300' : 'border-white/10 text-slate-300'"
        >
          <Layers class="w-4 h-4" />
          <span>Pôle</span>
          <span v-if="selectedPoles.length" class="bg-cyan-500/30 text-cyan-300 text-[10px] font-bold px-1.5 py-0.5 rounded-full">{{ selectedPoles.length }}</span>
          <ChevronDown class="w-3.5 h-3.5 text-slate-400 transition-transform duration-200" :class="openDropdown === 'pole' ? 'rotate-180' : ''" />
        </button>
      </div>

      <!-- Type de recrutement -->
      <div class="flex items-center gap-1 bg-slate-700/50 border border-white/10 rounded-lg p-1">
        <button @click="selectedRecruitment = null"
          class="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all duration-200"
          :class="selectedRecruitment === null ? 'bg-slate-500/60 text-white' : 'text-slate-400 hover:text-slate-300'"
        >Tous</button>
        <button v-for="type in recruitmentTypes" :key="type.value"
          @click="selectedRecruitment = selectedRecruitment === type.value ? null : type.value"
          class="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all duration-200"
          :class="selectedRecruitment === type.value ? type.activeClass : 'text-slate-400 hover:text-slate-300'"
        ><span>{{ type.icon }}</span>{{ type.label }}</button>
      </div>

      <!-- Créneau horaire -->
      <div class="relative">
        <button ref="slotTriggerRef" @click.stop="toggleDropdown('slot')"
          class="flex items-center gap-2 px-3 py-2 bg-slate-700/50 border rounded-lg text-sm transition-all duration-200 hover:bg-slate-700"
          :class="slotFilter !== 'all' ? 'border-purple-500/50 text-purple-300' : 'border-white/10 text-slate-300'"
        >
          <Clock class="w-4 h-4" />
          <span>{{ slotFilterLabel }}</span>
          <ChevronDown class="w-3.5 h-3.5 text-slate-400 transition-transform duration-200" :class="openDropdown === 'slot' ? 'rotate-180' : ''" />
        </button>
      </div>

      <!-- Effectif minimum -->
      <div class="relative">
        <button ref="countTriggerRef" @click.stop="toggleDropdown('count')"
          class="flex items-center gap-2 px-3 py-2 bg-slate-700/50 border rounded-lg text-sm transition-all duration-200 hover:bg-slate-700"
          :class="minVolunteers > 1 ? 'border-emerald-500/50 text-emerald-300' : 'border-white/10 text-slate-300'"
        >
          <Users class="w-4 h-4" />
          <span>{{ minVolunteers > 1 ? `≥ ${minVolunteers} bénévoles` : 'Effectif' }}</span>
          <ChevronDown class="w-3.5 h-3.5 text-slate-400 transition-transform duration-200" :class="openDropdown === 'count' ? 'rotate-180' : ''" />
        </button>
      </div>

      <!-- Reset -->
      <Transition name="fade">
        <button v-if="hasActiveFilters" @click="resetFilters"
          class="flex items-center gap-2 px-3 py-2 bg-red-500/10 border border-red-500/20 text-red-400 rounded-lg text-sm hover:bg-red-500/20 transition-all duration-200"
        ><X class="w-3.5 h-3.5" /></button>
      </Transition>

      <!-- Results count -->
      <div class="ml-auto text-xs text-slate-500">
        <span class="text-slate-300 font-medium">{{ resultCount }}</span> poste{{ resultCount > 1 ? 's' : '' }}
      </div>
    </div>

    <!-- ── Teleported dropdowns ── -->
    <Teleport to="body">

      <!-- Jour dropdown -->
      <Transition name="dropdown">
        <div v-if="openDropdown === 'day'" class="fixed z-40 bg-slate-800 border border-white/10 rounded-xl shadow-2xl p-2 min-w-52" :style="dropdownPos" @click.stop>
          <button @click.stop="selectedDay = null; openDropdown = null"
            class="w-full flex items-center justify-between gap-3 px-3 py-2 rounded-lg text-sm transition-all duration-150 hover:bg-white/5 text-left"
            :class="selectedDay === null ? 'text-white' : 'text-slate-400'"
          >Tous les jours <Check v-if="selectedDay === null" class="w-3.5 h-3.5 text-cyan-400 shrink-0" /></button>
          <button v-for="day in festivalDays" :key="day.day"
            @click.stop="selectedDay = day.day; openDropdown = null"
            class="w-full flex items-center justify-between gap-3 px-3 py-2 rounded-lg text-sm transition-all duration-150 hover:bg-white/5 text-left"
            :class="selectedDay === day.day ? 'text-white' : 'text-slate-400'"
          >{{ day.label }} <Check v-if="selectedDay === day.day" class="w-3.5 h-3.5 text-cyan-400 shrink-0" /></button>
        </div>
      </Transition>

      <!-- Pôle dropdown -->
      <Transition name="dropdown">
        <div v-if="openDropdown === 'pole'" data-dropdown="pole" class="fixed z-40 bg-slate-800 border border-white/10 rounded-xl shadow-2xl p-2 min-w-48" :style="dropdownPos" @click.stop>
          
          <!-- Recherche -->
          <div class="relative mb-1">
            <Search class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400 pointer-events-none" />
            <input id="search-pole"
              v-model="poleSearch"
              type="text"
              placeholder="Rechercher un pôle..."
              class="w-full bg-slate-700/50 border border-white/10 rounded-lg pl-8 pr-3 py-1.5 text-xs text-white placeholder-slate-500 outline-none focus:border-cyan-500/50 transition-all duration-200"
              @click.stop
            />
            <button v-if="poleSearch" @click.stop="poleSearch = ''" class="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-white transition-colors">
              <X class="w-3 h-3" />
            </button>
          </div>

          <!-- Liste avec scrollbar au-delà de 8 éléments -->
          <div class="overflow-y-auto" style="max-height: 256px">
            <div v-if="filteredPoleOptions.length === 0" class="px-3 py-2 text-xs text-slate-500 text-center">
              Aucun pôle trouvé
            </div>
            <button
              v-for="category in filteredPoleOptions"
              :key="category.id"
              @click.stop="togglePole(category.id)"
              class="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all duration-150 hover:bg-white/5 text-left"
              :class="selectedPoles.includes(category.id) ? 'text-white' : 'text-slate-400'"
            >
              <div class="w-2.5 h-2.5 rounded-full shrink-0" :style="{ background: getCategoryColor(category.id) }" />
              <span class="flex-1 truncate">{{ category.label }}</span>
              <Check v-if="selectedPoles.includes(category.id)" class="w-3.5 h-3.5 text-cyan-400 shrink-0" />
            </button>
          </div>

        </div>
      </Transition>

      <!-- Créneau dropdown -->
      <Transition name="dropdown">
        <div v-if="openDropdown === 'slot'" class="fixed z-40 bg-slate-800 border border-white/10 rounded-xl shadow-2xl p-2 min-w-44" :style="dropdownPos" @click.stop>
          <button v-for="opt in slotOptions" :key="opt.value"
            @click.stop="slotFilter = opt.value; openDropdown = null"
            class="w-full flex items-center justify-between gap-3 px-3 py-2 rounded-lg text-sm transition-all duration-150 hover:bg-white/5 text-left"
            :class="slotFilter === opt.value ? 'text-white' : 'text-slate-400'"
          >{{ opt.label }} <Check v-if="slotFilter === opt.value" class="w-3.5 h-3.5 text-purple-400 shrink-0" /></button>
        </div>
      </Transition>

      <!-- Effectif dropdown -->
      <Transition name="dropdown">
        <div v-if="openDropdown === 'count'" class="fixed z-40 bg-slate-800 border border-white/10 rounded-xl shadow-2xl p-4 min-w-52" :style="dropdownPos" @click.stop>
          <p class="text-xs text-slate-400 mb-3 uppercase tracking-wider">Bénévoles minimum requis</p>
          <div class="flex items-center gap-3">
            <input id="search-eff" type="range" v-model.number="minVolunteers" min="1" max="10" step="1" class="flex-1 accent-emerald-500" />
            <span class="text-sm font-bold text-emerald-400 w-6 text-center">{{ minVolunteers }}</span>
          </div>
          <div class="flex justify-between text-[10px] text-slate-600 mt-1 px-0.5"><span>1</span><span>5</span><span>10</span></div>
        </div>
      </Transition>

    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { Search, X, Layers, ChevronDown, Clock, Users, Check, CalendarDays } from 'lucide-vue-next'
import type { CategoryGroup, RecruitmentType } from '../../types/planning.types'
import { useFestivalDays } from '../../composables/useFestivalDays'


const{ festivalDays } = useFestivalDays()

interface Props { categoryGroups: CategoryGroup[]; resultCount: number }
const props = defineProps<Props>()
const emit = defineEmits<{
  'update:filtered': [groups: CategoryGroup[]]
  'update:selectedDay': [day: number | null]
}>()

const dayTriggerRef   = ref<HTMLElement | null>(null)
const poleTriggerRef  = ref<HTMLElement | null>(null)
const slotTriggerRef  = ref<HTMLElement | null>(null)
const countTriggerRef = ref<HTMLElement | null>(null)

const search              = ref('')
const selectedDay = ref<number | null>(null)
const selectedPoles       = ref<number[]>([])
const selectedRecruitment = ref<RecruitmentType | null>(null)
const slotFilter          = ref<'all' | 'day' | 'night' | 'cross-midnight'>('all')
const minVolunteers       = ref(1)
const openDropdown        = ref<'day' | 'pole' | 'slot' | 'count' | null>(null)

const dropdownPos = ref({ top: '0px', left: '0px' })

const poleSearch = ref('')

const filteredPoleOptions = computed(() =>
  categories.value.filter(c =>
    c.label.toLowerCase().includes(poleSearch.value.toLowerCase())
  )
)

const updateDropdownPos = () => {
  if (!openDropdown.value) return
  const triggerMap = { day: dayTriggerRef, pole: poleTriggerRef, slot: slotTriggerRef, count: countTriggerRef }
  const trigger = triggerMap[openDropdown.value]?.value
  if (!trigger) return
  const rect = trigger.getBoundingClientRect()
  dropdownPos.value = { top: `${rect.bottom + 8}px`, left: `${rect.left}px` }
}

const toggleDropdown = (name: 'day' | 'pole' | 'slot' | 'count') => {
  if (openDropdown.value === name) {
    openDropdown.value = null
  } else {
    openDropdown.value = name
    if (name !== 'pole') poleSearch.value = ''
    nextTick(updateDropdownPos)
  }
}

const categories = computed(() => props.categoryGroups.map(g => g.category))
const CATEGORY_COLORS = ['#22d3ee','#3b82f6','#a855f7','#ec4899','#10b981','#f59e0b','#ef4444','#6366f1']
const getCategoryColor = (id: number) => CATEGORY_COLORS[id % CATEGORY_COLORS.length]!

const recruitmentTypes = [
  { value: 'Normal'     as RecruitmentType, label: 'Normal',     icon: '👤', activeClass: 'bg-slate-500/60 text-white' },
  { value: 'Specialise' as RecruitmentType, label: 'Spécialisé', icon: '⭐', activeClass: 'bg-amber-500/30 text-amber-300' },
]

const slotOptions: { value: 'all' | 'day' | 'night' | 'cross-midnight'; label: string }[] = [
  { value: 'all',            label: 'Tous les créneaux' },
  { value: 'day',            label: '☀️ Journée (8h–18h)' },
  { value: 'night',          label: '🌙 Soirée / Nuit (18h-23h)' },
  { value: 'cross-midnight', label: '🌃 Passe minuit' },
]

const slotFilterLabel = computed(() => slotOptions.find(o => o.value === slotFilter.value)?.label ?? 'Créneau')

const hasActiveFilters = computed(() =>
  search.value !== '' || selectedDay.value !== null || selectedPoles.value.length > 0 ||
  selectedRecruitment.value !== null || slotFilter.value !== 'all' || minVolunteers.value > 1
)


const filteredGroups = computed((): CategoryGroup[] =>
  props.categoryGroups
    .filter(g => selectedPoles.value.length === 0 || selectedPoles.value.includes(g.category.id))
    .map(g => ({
      ...g,
      jobs: g.jobs.filter(job => {
        if (search.value && !job.name.toLowerCase().includes(search.value.toLowerCase())) return false
        if (selectedDay.value !== null && job.slot.day_index !== selectedDay.value) return false
        if (selectedRecruitment.value !== null && job.recruitment_type !== selectedRecruitment.value) return false
        if (job.required_volunteers < minVolunteers.value) return false
        if (slotFilter.value !== 'all') {
          const { start_time, end_time } = job.slot
          const crossesMidnight = end_time < start_time || (start_time <= 5 && end_time <= 5)
          if (slotFilter.value === 'cross-midnight' && !crossesMidnight) return false
          if (slotFilter.value === 'day' && (crossesMidnight || start_time >= 18 || end_time <= 8)) return false
          if (slotFilter.value === 'night' && !(start_time >= 18 && end_time <= 23 && !crossesMidnight)) return false
        }
        return true
      }),
    }))
    .filter(g => g.jobs.length > 0)
)

watch(filteredGroups, val => emit('update:filtered', val), { immediate: true })
watch(selectedDay, val => emit('update:selectedDay', val), { immediate: true })

const togglePole = (id: number) => {
  const idx = selectedPoles.value.indexOf(id)
  if (idx === -1) selectedPoles.value.push(id)
  else selectedPoles.value.splice(idx, 1)
}

const resetFilters = () => {
  search.value = ''
  selectedDay.value = null
  selectedPoles.value = []
  selectedRecruitment.value = null
  slotFilter.value = 'all'
  minVolunteers.value = 1
}

const handleOutsideClick = (e: MouseEvent) => {
  if (!openDropdown.value) return
  const triggers = [dayTriggerRef.value, poleTriggerRef.value, slotTriggerRef.value, countTriggerRef.value]
  if (triggers.some(t => t?.contains(e.target as Node))) return
  openDropdown.value = null
}

const handleScroll = (e: Event) => {
  const poleDropdown = document.querySelector('[data-dropdown="pole"]')
  if (poleDropdown?.contains(e.target as Node)) return
  openDropdown.value = null
}

onMounted(() => {
  document.addEventListener('click', handleOutsideClick)
  window.addEventListener('scroll', handleScroll, true)
  window.addEventListener('resize', () => { openDropdown.value = null })
})

onUnmounted(() => {
  document.removeEventListener('click', handleOutsideClick)
  window.removeEventListener('scroll', handleScroll, true)
  window.removeEventListener('resize', () => { openDropdown.value = null })
})
</script>

<style scoped>
.dropdown-enter-active, .dropdown-leave-active { transition: opacity 0.15s ease, transform 0.15s ease; }
.dropdown-enter-from, .dropdown-leave-to { opacity: 0; transform: translateY(-4px); }
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>