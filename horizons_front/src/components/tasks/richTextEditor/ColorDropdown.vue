<template>
  <div class="relative" ref="btnRef">
    <!-- Toolbar button -->
    <button
      class="flex flex-col items-center justify-center w-7 h-7 mx-0.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-all cursor-pointer"
      title="Couleur du texte"
      @mousedown.prevent="toggle"
    >
      <span class="text-[11px] font-black leading-none mt-1" style="font-family:serif">A</span>
      <div class="w-4 h-0.75 rounded-full mt-0.5 transition-colors duration-150" :style="{ background: currentColor }" />
    </button>

    <Teleport to="body">
      <div
        v-if="show"
        class="fixed z-9999 bg-slate-800 border border-white/10 rounded-xl shadow-2xl p-3 flex flex-col gap-2.5 w-52"
        :style="pos"
        @mousedown.stop
      >
        <!-- Preset colors -->
        <div>
          <p class="text-[10px] text-slate-500 font-medium uppercase tracking-wider mb-1.5">Couleurs</p>
          <div class="grid grid-cols-10 gap-1">
            <button
              v-for="c in PRESETS"
              :key="c"
              class="w-4 h-4 rounded-full ring-1 ring-white/10 hover:scale-110 transition-transform"
              :style="{ background: c }"
              :title="c"
              @mousedown.prevent="apply(c)"
            />
          </div>
        </div>

        <!-- Recent colors -->
        <template v-if="recentColors.length">
          <div class="border-t border-white/8 pt-2">
            <p class="text-[10px] text-slate-500 font-medium uppercase tracking-wider mb-1.5">Récentes</p>
            <div class="flex flex-wrap gap-1">
              <button
                v-for="c in recentColors"
                :key="c"
                class="w-4 h-4 rounded-full ring-1 ring-white/10 hover:scale-110 transition-transform"
                :style="{ background: c }"
                :title="c"
                @mousedown.prevent="apply(c)"
              />
            </div>
          </div>
        </template>

        <!-- Custom color picker -->
        <div class="border-t border-white/8 pt-2 flex items-center gap-2">
          <label
            class="flex items-center gap-2 cursor-pointer flex-1 px-2 py-1.5 rounded-lg hover:bg-white/5 transition-colors"
          >
            <div class="w-5 h-5 rounded-full ring-1 ring-white/20 shrink-0" :style="{ background: currentColor }" />
            <span class="text-xs text-slate-400">Couleur personnalisée</span>
            <input id="color-input2"
              type="color"
              :value="currentColor"
              class="sr-only"
              @focus="pickerOpen = true"
              @blur="pickerOpen = false"
              @input="onPickerInput"
              @change="onPickerChange"
            />
          </label>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const PRESETS = ['#FFFFFF', '#000000', '#0000FF', '#000080',
                '#FF0000', '#008000', '#A5A5A5', '#FF8C00',
                '#800080', '#FFD700'
                ]

const MAX_RECENT = 10

const props = defineProps<{
  activeColor: string
}>()

const emit = defineEmits<{
  applyColor:       [color: string]
  saveSelection:    []
  colorPickerClose: []
}>()

const show        = ref(false)
const pos         = ref({ top: '0px', left: '0px' })
const btnRef      = ref<HTMLElement | null>(null)
const currentColor = ref(props.activeColor || '#ffffff')
const recentColors = ref<string[]>([])
const pickerOpen = ref(false)

// Watch prop changes (e.g. cursor move updates activeColor externally)
import { watch } from 'vue'
watch(() => props.activeColor, (v) => {
  if (v) currentColor.value = v
})

const toggle = () => {
  if (!show.value) {
    emit('saveSelection')
    if (btnRef.value) {
      const r = btnRef.value.getBoundingClientRect()
      // Prefer opening to the right; clamp if near edge
      const left = Math.min(r.left, window.innerWidth - 224)
      pos.value = { top: `${r.bottom + 4}px`, left: `${left}px` }
    }
  }
  show.value = !show.value
}

const apply = (color: string) => {
  emit('saveSelection')
  currentColor.value = color
  emit('applyColor', color)
  addRecent(color)
  show.value = false
  emit('colorPickerClose')
}

const onPickerInput = (e: Event) => {
  const color = (e.target as HTMLInputElement).value
  currentColor.value = color
  emit('applyColor', color)
}

const onPickerChange = (e: Event) => {
  const color = (e.target as HTMLInputElement).value
  currentColor.value = color
  addRecent(color)
  pickerOpen.value = false
  emit('colorPickerClose')
  show.value = false
}

const addRecent = (color: string) => {
  const filtered = recentColors.value.filter(c => c.toLowerCase() !== color.toLowerCase())
  recentColors.value = [color, ...filtered].slice(0, MAX_RECENT)
}

const onOutside = (e: MouseEvent) => {
  if (pickerOpen.value) return    
  if (!btnRef.value?.contains(e.target as Node)) {
    show.value = false
  }
}
onMounted(() => document.addEventListener('mousedown', onOutside))
onUnmounted(() => document.removeEventListener('mousedown', onOutside))
</script>