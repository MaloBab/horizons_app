<template>
  <div class="relative" ref="btnRef">
    <ToolbarButton title="Insérer un tableau" @act="toggle">
      <Table class="w-3.5 h-3.5" />
    </ToolbarButton>
    <Teleport to="body">
      <div
        v-if="show"
        class="fixed z-9999 bg-slate-800 border border-white/10 rounded-xl shadow-2xl p-3 flex flex-col gap-2.5 min-w-44"
        :style="pos"
        @mousedown.stop
      >
        <p class="text-[11px] text-slate-400 font-medium">Dimensions du tableau</p>
        <div class="flex items-center gap-2">
          <label class="text-xs text-slate-500 w-16 shrink-0">Colonnes</label>
          <input id="tab-dim1" v-model.number="config.cols" type="number" min="1" max="10"
            class="w-14 bg-slate-700 border border-white/10 rounded-lg px-2 py-1 text-xs text-slate-200 outline-none focus:border-cyan-500/40 text-center" />
        </div>
        <div class="flex items-center gap-2">
          <label class="text-xs text-slate-500 w-16 shrink-0">Lignes</label>
          <input id="tab-dim2" v-model.number="config.rows" type="number" min="1" max="20"
            class="w-14 bg-slate-700 border border-white/10 rounded-lg px-2 py-1 text-xs text-slate-200 outline-none focus:border-cyan-500/40 text-center" />
        </div>
        <div class="flex items-center gap-2 pt-1">
          <label class="text-xs text-slate-500 w-16 shrink-0">En-tête</label>
          <button
            @mousedown.prevent="config.header = !config.header"
            class="w-7 h-4 rounded-full transition-colors relative"
            :class="config.header ? 'bg-cyan-500' : 'bg-slate-600'"
          >
            <div class="absolute top-0.5 w-3 h-3 rounded-full bg-white shadow transition-all"
              :class="config.header ? 'left-3.5' : 'left-0.5'" />
          </button>
        </div>
        <button
          class="mt-1 w-full px-3 py-1.5 rounded-lg text-xs font-semibold bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 hover:bg-cyan-500/25 transition-all"
          @mousedown.prevent="insert"
        >
          Insérer
        </button>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Table } from 'lucide-vue-next'
import ToolbarButton from '../richTextEditor/ToolbarButton.vue'

const emit = defineEmits<{ insertTable: [rows: number, cols: number, header: boolean] }>()

const show   = ref(false)
const pos    = ref({ top: '0px', left: '0px' })
const btnRef = ref<HTMLElement | null>(null)
const config = reactive({ rows: 3, cols: 3, header: true })

const toggle = () => {
  show.value = !show.value
  if (show.value && btnRef.value) {
    const r = btnRef.value.getBoundingClientRect()
    pos.value = { top: `${r.bottom + 4}px`, left: `${r.left}px` }
  }
}

const insert = () => {
  emit('insertTable', config.rows, config.cols, config.header)
  show.value = false
}

const close = () => { show.value = false }
defineExpose({ close })
</script>