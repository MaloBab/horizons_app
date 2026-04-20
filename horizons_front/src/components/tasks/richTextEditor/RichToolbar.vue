<template>
  <div
    ref="toolbarRef"
    class="flex items-center gap-0.5 px-2 py-1.5 border-b border-white/10 flex-wrap sticky top-0 z-10 backdrop-blur-md bg-slate-900/95"
  >
    <ToolbarButton title="Gras (Ctrl+B)"      :active="st.bold"      @act="emit('toggleInline', 'strong')">
      <Bold class="w-3.5 h-3.5" />
    </ToolbarButton>
    <ToolbarButton title="Italique (Ctrl+I)"   :active="st.italic"    @act="emit('toggleInline', 'em')">
      <Italic class="w-3.5 h-3.5" />
    </ToolbarButton>
    <ToolbarButton title="Souligné (Ctrl+U)"   :active="st.underline" @act="emit('toggleInline', 'u')">
      <Underline class="w-3.5 h-3.5" />
    </ToolbarButton>
    <ToolbarButton title="Barré"               :active="st.strike"    @act="emit('toggleInline', 's')">
      <Strikethrough class="w-3.5 h-3.5" />
    </ToolbarButton>

    <ToolbarSeparator />

    <SizeDropdown ref="sizeDropdownRef" @apply-size="emit('applySize', $event)" />

    <!-- Color picker dropdown -->
    <ColorDropdown
      :active-color="activeColor"
      @apply-color="emit('applyColor', $event)"
      @save-selection="emit('saveSelection')"
      @color-picker-close="emit('colorPickerClose')"
    />

    <ToolbarSeparator />

    <ToolbarButton title="Titre 1"      @act="emit('setBlock', 'h1')"><span class="text-[10px] font-black">H1</span></ToolbarButton>
    <ToolbarButton title="Titre 2"      @act="emit('setBlock', 'h2')"><span class="text-[10px] font-bold">H2</span></ToolbarButton>
    <ToolbarButton title="Titre 3"      @act="emit('setBlock', 'h3')"><span class="text-[10px] font-semibold">H3</span></ToolbarButton>
    <ToolbarButton title="Texte normal" @act="emit('setBlock', 'p')"><span class="text-[11px]">¶</span></ToolbarButton>

    <ToolbarSeparator />

    <ToolbarButton title="Liste à puces"    :active="st.ul" @act="emit('toggleList', 'ul')">
      <List class="w-3.5 h-3.5" />
    </ToolbarButton>
    <ToolbarButton title="Liste numérotée" :active="st.ol" @act="emit('toggleList', 'ol')">
      <ListOrdered class="w-3.5 h-3.5" />
    </ToolbarButton>

    <ToolbarSeparator />

    <TableDropdown ref="tableDropdownRef" @insert-table="(r, c, h) => emit('insertTable', r, c, h)" />

    <ToolbarSeparator />

    <ToolbarButton title="Annuler (Ctrl+Z)" @act="emit('undo')">
      <Undo2 class="w-3.5 h-3.5" />
    </ToolbarButton>
    <ToolbarButton title="Rétablir (Ctrl+Y)" @act="emit('redo')">
      <Redo2 class="w-3.5 h-3.5" />
    </ToolbarButton>

    <div class="ml-auto">
      <ToolbarButton title="Effacer la mise en forme" @act="emit('clearFormat')">
        <RemoveFormatIcon class="w-3.5 h-3.5" />
        <span class="text-[10px] ml-1 text-slate-500">Effacer</span>
      </ToolbarButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, defineComponent, h } from 'vue'
import { Bold, Italic, Underline, Strikethrough, List, ListOrdered, Undo2, Redo2 } from 'lucide-vue-next'
import ToolbarButton    from '../richTextEditor/ToolbarButton.vue'
import ToolbarSeparator from '../richTextEditor/ToolbarSeparator.vue'
import SizeDropdown     from '../richTextEditor/SizeDropdown.vue'
import ColorDropdown    from '../richTextEditor/ColorDropdown.vue'
import TableDropdown    from '../richTextEditor/TableDropdown.vue'

const RemoveFormatIcon = defineComponent({
  render: () => h('svg', {
    viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor',
    'stroke-width': '2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round',
  }, [
    h('path', { d: 'M4 7V4h16v3' }), h('path', { d: 'M5 20h6' }),
    h('path', { d: 'M13 4 9 20' }), h('line', { x1: '22', y1: '2', x2: '2', y2: '22' }),
  ]),
})

defineProps<{
  st: { bold: boolean; italic: boolean; underline: boolean; strike: boolean; ul: boolean; ol: boolean }
  activeColor: string
}>()

const emit = defineEmits<{
  toggleInline:     [tag: string]
  toggleList:       [type: 'ul' | 'ol']
  setBlock:         [tag: string]
  applySize:        [em: string]
  applyColor:       [color: string]
  saveSelection:    []
  colorPickerClose: []
  insertTable:      [rows: number, cols: number, header: boolean]
  clearFormat:      []
  undo:             []
  redo:             []
}>()

const sizeDropdownRef  = ref<InstanceType<typeof SizeDropdown> | null>(null)
const tableDropdownRef = ref<InstanceType<typeof TableDropdown> | null>(null)
const toolbarRef       = ref<HTMLElement | null>(null)

const closeDropdowns = () => {
  sizeDropdownRef.value?.close()
  tableDropdownRef.value?.close()
}

defineExpose({ toolbarRef, closeDropdowns })
</script>