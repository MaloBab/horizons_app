<template>
  <!--
    PAS de overflow-hidden ici — c'est ce qui bloquait le sticky.
    Le border-radius est géré via CSS sur les enfants directs (voir <style>).
  -->
  <div class="rich-editor bg-slate-800/50 border border-white/10 rounded-xl">
    <RichToolbar
      ref="toolbarRef"
      :st="st"
      :active-color="activeColor"
      @toggle-inline="toggleInline"
      @toggle-list="toggleList"
      @set-block="setBlock"
      @apply-size="applyFontSize"
      @apply-color="applyColor"
      @save-selection="saveSelection"
      @color-picker-close="onColorPickerClose"
      @insert-table="insertTable"
      @clear-format="clearFormat"
      @undo="undo"
      @redo="redo"
    />
    <RichContent
      ref="contentRef"
      :placeholder="placeholder"
      @input="onInput"
      @keyup="refreshState"
      @mouseup="refreshState"
      @keydown="onKeydown"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import RichToolbar from '../richTextEditor/RichToolbar.vue'
import RichContent from '../richTextEditor/RichContent.vue'
import { useRichEditor } from '../../../composables/useRichEditor'

const props = defineProps<{ modelValue: string; placeholder?: string }>()
const emit  = defineEmits<{ 'update:modelValue': [v: string] }>()

const toolbarRef = ref<InstanceType<typeof RichToolbar> | null>(null)
const contentRef = ref<InstanceType<typeof RichContent> | null>(null)
const editorEl   = ref<HTMLElement | null>(null)

const {
  st, activeColor,
  init, onInput, onKeydown, refreshState,
  undo, redo,
  toggleInline, toggleList, setBlock,
  applyColor, applyFontSize, saveSelection, onColorPickerClose,
  insertTable, clearFormat,
} = useRichEditor(editorEl)

onMounted(() => {
  editorEl.value = contentRef.value?.editorRef ?? null
  init(props.modelValue, (html) => emit('update:modelValue', html))
  document.addEventListener('mousedown', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('mousedown', handleClickOutside)
})

const handleClickOutside = (e: MouseEvent) => {
  const toolbar = toolbarRef.value?.toolbarRef
  if (toolbar?.contains(e.target as Node)) return
  toolbarRef.value?.closeDropdowns()
}

watch(() => props.modelValue, (val) => {
  if (editorEl.value && editorEl.value.innerHTML !== val)
    editorEl.value.innerHTML = val || ''
})

// ── Insertion à la position du curseur ───────────────────────────────────────
function insertAtCursor(text: string) {
  const el = contentRef.value?.editorRef
  if (!el) return

  el.focus()

  const sel = window.getSelection()
  if (!sel || sel.rangeCount === 0) {
    // Pas de sélection active : placer le curseur à la fin
    const range = document.createRange()
    range.selectNodeContents(el)
    range.collapse(false)
    sel?.removeAllRanges()
    sel?.addRange(range)
  }

  document.execCommand('insertText', false, text)
}

defineExpose({ insertAtCursor })
</script>

<style scoped>
.rich-editor :deep(> :first-child) {
  border-radius: 0.75rem 0.75rem 0 0;
}
.rich-editor :deep(> :last-child) {
  border-radius: 0 0 0.75rem 0.75rem;
}
</style>