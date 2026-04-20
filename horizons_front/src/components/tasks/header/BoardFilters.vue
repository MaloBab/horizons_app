<template>
  <div class="relative z-10 flex items-center gap-2.5 px-6 py-3 border-b border-white/10 bg-slate-900/60 backdrop-blur-sm flex-wrap">
    <div class="relative">
      <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 pointer-events-none" />
      <input id="search-task"
        v-model="filters.search" type="text" placeholder="Rechercher..."
        class="bg-slate-800/50 border border-white/10 rounded-xl pl-9 pr-4 py-2 text-sm text-white placeholder-slate-500 outline-none focus:border-cyan-500/40 focus:bg-slate-800 transition-all w-56"
      />
      <button v-if="filters.search" @click="filters.search = ''"
        class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-white">
        <X class="w-3.5 h-3.5" />
      </button>
    </div>

    <div class="w-px h-5 bg-white/10" />

    <button
      @click="filters.myTasks = !filters.myTasks"
      class="flex items-center gap-1.5 px-2 py-1 rounded-xl text-sm border transition-all"
      :class="filters.myTasks ? 'border-violet-500/40 bg-violet-500/15 text-violet-300' : 'border-white/10 text-slate-400 hover:border-white/20 hover:text-white'"
    ><User class="w-3.5 h-3.5" /> Mes tâches</button>

    <div class="relative" ref="userPickerRef">
      <button
        @click="togglePicker('user', userPickerRef)"
        class="flex items-center gap-1.5 px-2 py-1 rounded-xl text-sm border transition-all"
        :class="filters.userId ? 'border-cyan-500/40 bg-cyan-500/15 text-cyan-300' : 'border-white/10 text-slate-400 hover:border-white/20 hover:text-white'"
      >
        <Users class="w-3.5 h-3.5" />
        {{ filters.userId === '__unassigned__' ? 'Non assigné' : filters.userId ? getUserById(filters.userId)?.username : 'Utilisateur' }}
      </button>

      <Teleport to="body">
        <div v-if="activePicker === 'user'" class="picker-dropdown fixed z-9999 bg-slate-800 border border-white/10 rounded-xl shadow-2xl p-1.5 min-w-44" :style="pickerPos" @mousedown.stop>
          <button @click="filters.userId = null; closeAllPickers()" class="w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2.5" :class="filters.userId === null ? 'bg-white/8 text-white' : 'text-slate-400 hover:bg-white/5 hover:text-white'">
            <div class="w-6 h-6 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center shrink-0"><Users class="w-3.5 h-3.5 text-slate-400" /></div> Tous
          </button>
          <button @click="filters.userId = '__unassigned__'; closeAllPickers()" class="w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2.5" :class="filters.userId === '__unassigned__' ? 'bg-white/8 text-white' : 'text-slate-400 hover:bg-white/5 hover:text-white'">
            <div class="w-6 h-6 rounded-lg border border-dashed flex items-center justify-center shrink-0" :class="filters.userId === '__unassigned__' ? 'bg-white/8' : 'border-white/15 bg-transparent'"><UserX class="w-3.5 h-3.5 text-slate-400" /></div> Non assigné
          </button>
          <div class="h-px bg-white/8 my-1" />
          <button v-for="u in users" :key="u.id" @click="filters.userId = u.id; closeAllPickers()" class="w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2.5" :class="filters.userId === u.id ? 'bg-white/8 text-white' : 'text-slate-300 hover:bg-white/5'">
            <div class="w-6 h-6 rounded-lg flex items-center justify-center text-xs font-semibold shrink-0 overflow-hidden" :style="{ background: u.color + '33', color: u.color }">
              <img v-if="u.avatar_url" :src="u.avatar_url" class="w-full h-full object-cover" />
              <span v-else>{{ u.initials }}</span>
            </div>
            {{ u.username }}
          </button>
        </div>
      </Teleport>
    </div>

    <div class="relative" ref="tagPickerRef">
      <button @click="togglePicker('tag', tagPickerRef)" class="flex items-center gap-1.5 px-2 py-1 rounded-xl text-sm border transition-all" :class="filters.tagIds.length > 0 ? 'border-pink-500/40 bg-pink-500/15 text-pink-300' : 'border-white/10 text-slate-400 hover:border-white/20 hover:text-white'">
        <TagIcon class="w-3.5 h-3.5" /> Tags {{ filters.tagIds.length > 0 ? `(${filters.tagIds.length})` : '' }}
      </button>

      <Teleport to="body">
        <div v-if="activePicker === 'tag'" class="picker-dropdown fixed z-9999 bg-slate-800 border border-white/10 rounded-xl shadow-2xl min-w-48 max-h-80 flex flex-col overflow-hidden" :style="pickerPos" @mousedown.stop>
          <div class="p-2 border-b border-white/10 shrink-0 bg-slate-800/95 backdrop-blur-xs">
            <div class="relative">
              <Search class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-500 pointer-events-none" />
              <input id="search-task2" v-model="tagSearchQuery" type="text" placeholder="Chercher un tag..." class="w-full bg-slate-900/50 border border-white/10 rounded-lg pl-8 pr-3 py-1.5 text-xs text-white placeholder-slate-400 outline-none focus:border-cyan-500/40 focus:bg-slate-900 transition-all" />
            </div>
          </div>
          <div class="p-1.5 overflow-y-auto overscroll-contain">
            <button v-for="tag in filteredTagsList" :key="tag.id" @click="toggleTagFilter(tag.id)" class="w-full text-left px-2.5 py-2 rounded-lg text-sm transition-colors flex items-center justify-between" :class="filters.tagIds.includes(tag.id) ? 'bg-white/10 text-white' : 'text-slate-300 hover:bg-white/5'">
              <div class="flex items-center gap-2.5">
                <div class="w-2.5 h-2.5 rounded-full border border-white/20 shadow-xs" :style="{ backgroundColor: tag.color }"></div> {{ tag.name }}
              </div>
              <svg v-if="filters.tagIds.includes(tag.id)" class="w-4 h-4 text-cyan-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
            </button>
            <div v-if="filteredTagsList.length === 0" class="px-2 py-6 text-center text-xs text-slate-500">Aucun tag trouvé</div>
          </div>
        </div>
      </Teleport>
    </div>

    <div class="flex gap-1.5 items-center ml-1" v-if="filters.tagIds.length > 0">
      <button v-for="tagId in filters.tagIds.slice(0, 2)" :key="'active-'+tagId" @click="toggleTagFilter(tagId)" class="flex items-center gap-1.5 px-2 py-1 rounded-lg text-xs font-medium border transition-all hover:opacity-80 group whitespace-nowrap" :style="{ background: getTagById(tagId)?.color + '22', borderColor: getTagById(tagId)?.color + '44', color: getTagById(tagId)?.color }">
        {{ getTagById(tagId)?.name }} <X class="w-3 h-3 opacity-60 group-hover:opacity-100 transition-opacity" />
      </button>
      <button v-if="filters.tagIds.length > 2" @click="togglePicker('tag', tagPickerRef)" class="px-2 py-1 rounded-lg text-xs font-medium border border-white/10 bg-white/5 text-slate-300 hover:bg-white/10 transition-all whitespace-nowrap">
        +{{ filters.tagIds.length - 2 }}
      </button>
    </div>

    <div v-if="isLoading" class="flex items-center gap-2 text-xs text-slate-500">
      <div class="w-3 h-3 rounded-full border-2 border-cyan-500/40 border-t-cyan-400 animate-spin" /> Chargement…
    </div>
    
    <div class="ml-auto flex items-center gap-4">
      <Transition name="fade">
        <button v-if="hasFilters" @click="$emit('reset')" class="flex items-center gap-2 px-3 py-2 rounded-xl text-sm text-red-400 border border-red-500/20 bg-red-500/10 hover:bg-red-500/20 transition-all whitespace-nowrap">
          <X class="w-3.5 h-3.5" /> Réinitialiser
        </button>
      </Transition>
      <span class="text-xs text-slate-500 whitespace-nowrap min-w-15 text-right">{{ totalFiltered }} tâche{{ totalFiltered !== 1 ? 's' : '' }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'
import { Search, X, User, Users, UserX, Tag as TagIcon } from 'lucide-vue-next'

const props = defineProps<{
  filters: { search: string, myTasks: boolean, userId: string | null, tagIds: number[] }
  users: any[]
  tags: any[]
  totalFiltered: number
  isLoading: boolean
}>()

const emit = defineEmits(['reset'])

const activePicker = ref<'user' | 'tag' | null>(null)
const userPickerRef = ref<HTMLElement | null>(null)
const tagPickerRef = ref<HTMLElement | null>(null)
const pickerPos = ref({ top: '0px', left: '0px' })
const tagSearchQuery = ref('')

const getUserById = (id: string) => props.users.find(u => u.id === id)
const getTagById = (id: number) => props.tags.find(t => t.id === id)

const filteredTagsList = computed(() => {
  if (!tagSearchQuery.value) return props.tags
  const query = tagSearchQuery.value.toLowerCase()
  return props.tags.filter(t => t.name.toLowerCase().includes(query))
})

const hasFilters = computed(() => props.filters.search || props.filters.myTasks || props.filters.userId || props.filters.tagIds.length > 0)

const toggleTagFilter = (id: number) => {
  const idx = props.filters.tagIds.indexOf(id)
  if (idx === -1) props.filters.tagIds.push(id); else props.filters.tagIds.splice(idx, 1)
}

const togglePicker = (type: 'user' | 'tag', elementRef: HTMLElement | null) => {
  if (activePicker.value === type) {
    activePicker.value = null
    return
  }
  if (elementRef) {
    const r = elementRef.getBoundingClientRect()
    pickerPos.value = { top: `${r.bottom + 6}px`, left: `${r.left}px` }
  }
  activePicker.value = type
  if (type === 'tag') tagSearchQuery.value = ''
}

const closeAllPickers = () => { activePicker.value = null }

const handleClickOutside = (e: MouseEvent) => {
  if (!activePicker.value) return
  const target = e.target as Element
  if (target.closest('.picker-dropdown')) return
  const isClickOnUserBtn = activePicker.value === 'user' && userPickerRef.value?.contains(target as Node)
  const isClickOnTagBtn  = activePicker.value === 'tag'  && tagPickerRef.value?.contains(target as Node)
  if (!isClickOnUserBtn && !isClickOnTagBtn) closeAllPickers()
}

const handleScroll = (e: Event) => {
  const target = e.target as Element | Document
  if (target === document) { closeAllPickers(); return }
  if (target instanceof Element && target.closest('.picker-dropdown')) return
  closeAllPickers()
}

document.addEventListener('mousedown', handleClickOutside)
window.addEventListener('scroll', handleScroll, true)

onUnmounted(() => {
  document.removeEventListener('mousedown', handleClickOutside)
  window.removeEventListener('scroll', handleScroll, true)
})
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from,  .fade-leave-to      { opacity: 0; }
</style>