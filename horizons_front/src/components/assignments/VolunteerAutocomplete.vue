<template>
  <div class="relative min-w-44" ref="containerRef">

    <User class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none z-10" />

    <input
      id="search-assigned-volunteer"
      ref="inputRef"
      v-model="searchText"
      type="text"
      placeholder="Affectations bénévole…"
      autocomplete="off"
      class="w-full bg-slate-700/50 border border-white/10 rounded-lg pl-9 pr-8 py-2 text-sm text-white placeholder-slate-500 outline-none focus:border-purple-500/50 transition-colors"
      :class="{ 'border-purple-500/50 bg-purple-500/10': hasSelection }"
      @focus="onFocus"
      @blur="onBlur"
      @input="onUserInput"
      @keydown="onKeydown"
    />

    <button
      v-if="hasSelection"
      type="button"
      aria-label="Effacer la sélection"
      class="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-white transition-colors z-10"
      @click="onClear"
    >
      <X class="w-3.5 h-3.5" />
    </button>

    <Teleport to="body">
      <ul
        v-if="isOpen"
        role="listbox"
        aria-label="Suggestions de bénévoles"
        class="fixed z-50 bg-slate-800 border border-white/10 rounded-xl shadow-2xl overflow-hidden max-h-52 overflow-y-auto"
        :style="dropdownStyle"
        ref="dropdownRef"
        @mousedown="isMouseDownInDropdown = true"
        @mouseup="isMouseDownInDropdown = false"
      >
        <li
          v-for="(volunteer, index) in suggestions"
          :key="volunteer.id"
          role="option"
          :aria-selected="index === activeIndex"
          class="flex items-center gap-2.5 px-3 py-2 cursor-pointer transition-colors text-left select-none"
          :class="index === activeIndex ? 'bg-white/10' : 'hover:bg-white/5'"
          @click="onSelect(volunteer)"
          @mouseenter="activeIndex = index"
        >
          <div
            class="w-6 h-6 rounded-md shrink-0 flex items-center justify-center text-[9px] font-bold text-white"
            :class="volunteer.volunteer_type === 'Specialise' ? 'bg-amber-500/40' : 'bg-slate-600/60'"
          >
            {{ getInitials(`${volunteer.first_name} ${volunteer.last_name}`) }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm text-slate-200 truncate leading-tight">
              {{ volunteer.first_name }} {{ volunteer.last_name }}
            </p>
            <p class="text-[10px] text-slate-500 leading-tight">
              {{ volunteer.volunteer_type === 'Specialise' ? 'Spécialisé' : 'Normal' }}
            </p>
          </div>
        </li>

        <li v-if="suggestions.length === 0" class="px-3 py-4 text-sm text-slate-500 text-center">
          Aucun résultat
        </li>
      </ul>
    </Teleport>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onUnmounted } from 'vue'
import { User, X } from 'lucide-vue-next'
import { getInitials } from '../../utils/stringUtils'
import type { Volunteer } from '../../types/benevole.types'


const props = defineProps<{
  modelValue: string
  volunteers: Volunteer[]
}>()

const emit = defineEmits<{
  'update:modelValue': [id: string]
  'cleared': []
}>()


const containerRef  = ref<HTMLElement | null>(null)
const inputRef      = ref<HTMLInputElement | null>(null)
const dropdownRef   = ref<HTMLElement | null>(null)

const searchText            = ref('')
const isOpen                = ref(false)
const activeIndex           = ref(-1)
const isMouseDownInDropdown = ref(false)

const isProgrammaticChange = ref(false)

const positionTick = ref(0)


const hasSelection = computed(() => Boolean(props.modelValue))

const suggestions = computed<Volunteer[]>(() => {
  const query = searchText.value.trim().toLowerCase()
  const filtered = query
    ? props.volunteers.filter(v =>
        `${v.first_name} ${v.last_name}`.toLowerCase().includes(query)
      )
    : props.volunteers
  return filtered.slice(0, 20)
})

const dropdownStyle = computed(() => {
  positionTick.value
  if (!containerRef.value) return {}
  const { bottom, left, width } = containerRef.value.getBoundingClientRect()
  return {
    top:   `${bottom + 4}px`,
    left:  `${left}px`,
    width: `${width}px`,
  }
})


function labelFromId(id: string): string {
  if (!id) return ''
  const volunteer = props.volunteers.find(v => v.id === id)
  return volunteer ? `${volunteer.first_name} ${volunteer.last_name}` : ''
}

function setProgrammatically(value: string): void {
  isProgrammaticChange.value = true
  searchText.value = value
  nextTick(() => { isProgrammaticChange.value = false })
}

watch(
  () => props.modelValue,
  id => { setProgrammatically(labelFromId(id)) },
  { immediate: true },
)


function refreshPosition(): void {
  nextTick(() => { positionTick.value++ })
}

defineExpose({ refreshPosition })


function onExternalScroll(event: Event): void {
  if (dropdownRef.value && dropdownRef.value.contains(event.target as Node)) return
  closeDropdown()
  inputRef.value?.blur()
}

function attachScrollListener(): void {
  window.addEventListener('scroll', onExternalScroll, { capture: true, passive: true })
}

function detachScrollListener(): void {
  window.removeEventListener('scroll', onExternalScroll, { capture: true })
}

onUnmounted(detachScrollListener)


function openDropdown(): void {
  refreshPosition()
  activeIndex.value = -1
  isOpen.value = true
  attachScrollListener()
}

function closeDropdown(): void {
  isOpen.value = false
  activeIndex.value = -1
  detachScrollListener()
}


function onFocus(): void {
  openDropdown()
}

function onBlur(): void {
  if (isMouseDownInDropdown.value) return

  closeDropdown()
  setProgrammatically(labelFromId(props.modelValue))
}

function onUserInput(): void {
  if (isProgrammaticChange.value) return
  if (props.modelValue) emit('update:modelValue', '')
  if (!isOpen.value) openDropdown()
}


function onKeydown(event: KeyboardEvent): void {
  if (!isOpen.value) {
    if (event.key === 'ArrowDown' || event.key === 'Enter') openDropdown()
    return
  }

  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault()
      activeIndex.value = Math.min(activeIndex.value + 1, suggestions.value.length - 1)
      break
    case 'ArrowUp':
      event.preventDefault()
      activeIndex.value = Math.max(activeIndex.value - 1, 0)
      break
    case 'Enter':
      event.preventDefault()
      if (activeIndex.value >= 0 && suggestions.value[activeIndex.value]) {
        onSelect(suggestions.value[activeIndex.value]!)
      }
      break
    case 'Escape':
      closeDropdown()
      inputRef.value?.blur()
      break
    case 'Tab':
      closeDropdown()
      break
  }
}


function onSelect(volunteer: Volunteer): void {
  setProgrammatically(`${volunteer.first_name} ${volunteer.last_name}`)
  emit('update:modelValue', volunteer.id)
  closeDropdown()
}

function onClear(): void {
  setProgrammatically('')
  emit('update:modelValue', '')
  emit('cleared')
  nextTick(() => inputRef.value?.focus())
}
</script>