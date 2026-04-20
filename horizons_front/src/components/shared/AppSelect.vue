<template>
  <div class="relative" ref="containerRef">
    <button
      type="button"
      @click="toggle"
      class="flex items-center justify-between gap-2 w-full bg-slate-800/60 border rounded-lg px-3 py-2 text-sm outline-none transition-all cursor-pointer"
      :class="isOpen
        ? 'border-cyan-500/50 bg-slate-800 text-white'
        : isModified
          ? 'border-cyan-500/30 bg-slate-800/80 text-cyan-300 hover:border-cyan-500/50 hover:bg-slate-800'
          : 'border-white/10 text-slate-300 hover:border-white/20 hover:bg-slate-800'"
    >
      <span class="truncate">{{ selectedLabel }}</span>
      <svg
        class="w-3.5 h-3.5 shrink-0 transition-transform duration-200"
        :class="[isOpen ? 'rotate-180' : '', isModified ? 'text-cyan-400' : 'text-slate-500']"
        viewBox="0 0 12 12" fill="none"
      >
        <path d="M2.5 4L6 7.5 9.5 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </button>

    <Teleport to="body">
      <Transition name="dropdown">
        <div
          v-if="isOpen"
          ref="dropdownRef"
          @mouseenter="lockScroll"
          @mouseleave="unlockScroll"
          :style="dropdownStyle"
          class="fixed z-9999 bg-slate-800 border border-white/10 rounded-lg shadow-xl shadow-black/40 overflow-y-auto max-h-64"
        >
          <div
            v-for="option in options"
            :key="option.value"
            @click="select(option)"
            class="flex items-center justify-between px-3 py-2 text-sm cursor-pointer transition-colors"
            :class="option.value === modelValue
              ? 'bg-cyan-500/15 text-cyan-300'
              : 'text-slate-300 hover:bg-white/5 hover:text-white'"
          >
            <span>{{ option.label }}</span>
            <svg
              v-if="option.value === modelValue"
              class="w-3 h-3 text-cyan-400 shrink-0 ml-4"
              viewBox="0 0 12 12" fill="none"
            >
              <path d="M2 6l3 3 5-5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted, nextTick } from 'vue'

interface Option { label: string; value: string | number }

const props = defineProps<{
  modelValue: string | number
  options: Option[]
}>()

const emit = defineEmits<{ 'update:modelValue': [value: string | number] }>()

const isOpen       = ref(false)
const isInsideDrop = ref(false)
const containerRef = ref<HTMLElement | null>(null)
const dropdownRef  = ref<HTMLElement | null>(null)

// ✅ Position calculée depuis le bouton trigger
const dropdownStyle = ref<Record<string, string>>({})

function updatePosition() {
  if (!containerRef.value) return
  const rect = containerRef.value.getBoundingClientRect()
  dropdownStyle.value = {
    top:      `${rect.bottom + 4}px`,
    left:     `${rect.left}px`,
    minWidth: `${rect.width}px`,
  }
}

const selectedLabel = computed(
  () => props.options.find(o => o.value === props.modelValue)?.label ?? '—'
)

const isModified = computed(() => {
  if (props.options.length === 0) return false
  return props.options.find(o => o.value === props.modelValue)?.value !== props.options[0]!.value
})

// ─── Scroll lock ──────────────────────────────────────────────────────────────

function preventScroll(e: WheelEvent | TouchEvent) {
  if (dropdownRef.value?.contains(e.target as Node)) return
  e.preventDefault()
  e.stopPropagation()
  close()
}

function lockScroll() {
  isInsideDrop.value = true
  window.addEventListener('wheel',     preventScroll, { passive: false, capture: true })
  window.addEventListener('touchmove', preventScroll, { passive: false, capture: true })
}

function unlockScroll() {
  isInsideDrop.value = false
  window.removeEventListener('wheel',     preventScroll, { capture: true })
  window.removeEventListener('touchmove', preventScroll, { capture: true })
}

// ─── Scroll extérieur ─────────────────────────────────────────────────────────

function onExternalScroll(e: Event) {
  if (!isOpen.value) return
  if (dropdownRef.value?.contains(e.target as Node)) return
  close()
}

// ─── Cycle de vie ─────────────────────────────────────────────────────────────

async function open() {
  isOpen.value = true
  await nextTick()   // attend que le DOM du bouton soit stable
  updatePosition()
  document.addEventListener('mousedown', onClickOutside)
  window.addEventListener('scroll', onExternalScroll, { capture: true, passive: true })
  window.addEventListener('resize', updatePosition)
}

function close() {
  isOpen.value = false
  unlockScroll()
  document.removeEventListener('mousedown', onClickOutside)
  window.removeEventListener('scroll', onExternalScroll, { capture: true })
  window.removeEventListener('resize', updatePosition)
}

function toggle() {
  isOpen.value ? close() : open()
}

function select(option: Option) {
  emit('update:modelValue', option.value)
  close()
}

function onClickOutside(e: MouseEvent) {
  if (!containerRef.value?.contains(e.target as Node)) close()
}

onUnmounted(() => close())

watch(isOpen, (val) => { if (!val) unlockScroll() })
</script>

<style scoped>
.dropdown-enter-active, .dropdown-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.dropdown-enter-from, .dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>