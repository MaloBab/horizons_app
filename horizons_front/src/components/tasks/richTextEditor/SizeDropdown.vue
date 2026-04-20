<template>
  <div class="relative" ref="btnRef">
    <ToolbarButton title="Taille du texte" @act="toggle">
      <Type class="w-3.5 h-3.5" />
      <ChevronDown class="w-2.5 h-2.5 opacity-50 ml-0.5" />
    </ToolbarButton>
    <Teleport to="body">
      <div
        v-if="show"
        class="fixed z-9999 bg-slate-800 border border-white/10 rounded-xl shadow-2xl p-1 flex flex-col min-w-32"
        :style="pos"
        @mousedown.stop
      >
        <button
          v-for="s in sizes" :key="s.em"
          class="px-3 py-1.5 rounded-lg text-left hover:bg-white/5 text-slate-300 whitespace-nowrap transition-colors"
          :style="{ fontSize: s.px }"
          @mousedown.prevent="select(s.em)"
        >
          {{ s.label }}
        </button>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Type, ChevronDown } from 'lucide-vue-next'
import ToolbarButton from '../richTextEditor/ToolbarButton.vue'

const emit = defineEmits<{ applySize: [em: string] }>()

const show   = ref(false)
const pos    = ref({ top: '0px', left: '0px' })
const btnRef = ref<HTMLElement | null>(null)

const sizes = [
  { label: 'Très petit', em: '0.7em',  px: '11px' },
  { label: 'Petit',      em: '0.85em', px: '13px' },
  { label: 'Normal',     em: '1em',    px: '15px' },
  { label: 'Grand',      em: '1.25em', px: '18px' },
  { label: 'Très grand', em: '1.5em',  px: '22px' },
]

const toggle = () => {
  show.value = !show.value
  if (show.value && btnRef.value) {
    const r = btnRef.value.getBoundingClientRect()
    pos.value = { top: `${r.bottom + 4}px`, left: `${r.left}px` }
  }
}

const select = (em: string) => {
  emit('applySize', em)
  show.value = false
}

const close = () => { show.value = false }
defineExpose({ close })
</script>