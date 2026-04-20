<template>
  <div
    ref="editorRef"
    contenteditable="true"
    class="rich-content min-h-28 p-3 text-sm outline-none leading-relaxed"
    :data-placeholder="placeholder"
    @input="emit('input')"
    @keyup="emit('keyup')"
    @mouseup="emit('mouseup')"
    @keydown="handleKeydown"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{ placeholder?: string }>()
const emit = defineEmits<{
  input:   []
  keyup:   []
  mouseup: []
  keydown: [e: KeyboardEvent]
}>()

const editorRef = ref<HTMLElement | null>(null)
defineExpose({ editorRef })

const REPLACEMENTS: { trigger: string; replacement: string }[] = [
  { trigger: '->',   replacement: '→' },
  { trigger: '<-',   replacement: '←' },
  { trigger: '=>',   replacement: '⇒' },
  { trigger: '<=',   replacement: '⇐' },
  { trigger: '<->',  replacement: '↔' },
  { trigger: '<=>',  replacement: '⟺' },
  { trigger: '-->',  replacement: '⟶' },
  { trigger: '<--',  replacement: '⟵' },
  { trigger: '>>',   replacement: '»' },
  { trigger: '<<',   replacement: '«' },

  { trigger: '!=',   replacement: '≠' },
  { trigger: '~=',   replacement: '≈' },
  { trigger: '<=',   replacement: '≤' },
  { trigger: '>=',   replacement: '≥' },
  { trigger: '**',   replacement: '×' },
  { trigger: '//',   replacement: '÷' },
  { trigger: 'inf',  replacement: '∞' },

  { trigger: '...',  replacement: '…' },
  { trigger: '--',   replacement: '—' },
  { trigger: '(c)',  replacement: '©' },
  { trigger: '(r)',  replacement: '®' },
  { trigger: '(tm)', replacement: '™' },
  { trigger: '1/2',  replacement: '½' },
  { trigger: '1/3',  replacement: '⅓' },
  { trigger: '2/3',  replacement: '⅔' },
  { trigger: '1/4',  replacement: '¼' },
  { trigger: '3/4',  replacement: '¾' },
]

const SORTED_REPLACEMENTS = [...REPLACEMENTS].sort(
  (a, b) => b.trigger.length - a.trigger.length
)


function tryReplace(): boolean {
  const sel = window.getSelection()
  if (!sel || sel.rangeCount === 0) return false

  const range = sel.getRangeAt(0)
  if (!range.collapsed) return false

  const node = range.startContainer
  if (node.nodeType !== Node.TEXT_NODE) return false

  const text   = node.textContent ?? ''
  const offset = range.startOffset

  for (const { trigger, replacement } of SORTED_REPLACEMENTS) {
    if (offset < trigger.length) continue
    const slice = text.slice(offset - trigger.length, offset)
    if (slice !== trigger) continue

    const newText =
      text.slice(0, offset - trigger.length) +
      replacement +
      text.slice(offset)

    node.textContent = newText

    const newOffset = offset - trigger.length + replacement.length
    const newRange  = document.createRange()
    newRange.setStart(node, newOffset)
    newRange.collapse(true)
    sel.removeAllRanges()
    sel.addRange(newRange)

    return true
  }
  return false
}


function handleKeydown(e: KeyboardEvent) {
  if (e.key === ' ' || e.key === 'Enter' || e.key === 'Tab') {
      if (tryReplace()) {}
    }
  emit('keydown', e)
}
</script>

<style scoped>
.rich-content { color: rgba(203, 213, 225, 0.9); }

[contenteditable]:empty:before {
  content: attr(data-placeholder);
  color: rgba(148, 163, 184, 0.4);
  pointer-events: none;
}

.rich-content :deep(h1) { font-size:1.5em; font-weight:700; color:white; margin:.5em 0 .2em; line-height:1.2; }
.rich-content :deep(h2) { font-size:1.25em; font-weight:600; color:rgba(255,255,255,.9); margin:.4em 0 .15em; }
.rich-content :deep(h3) { font-size:1.05em; font-weight:600; color:rgba(255,255,255,.8); margin:.35em 0 .1em; }
.rich-content :deep(p)  { margin:.2em 0; }
.rich-content :deep(ul) { list-style:disc;    padding-left:1.4em; margin:.25em 0; }
.rich-content :deep(ol) { list-style:decimal; padding-left:1.4em; margin:.25em 0; }
.rich-content :deep(li) { margin:.15em 0; }
.rich-content :deep(a)  { color:#22d3ee; text-decoration:underline; }
.rich-content :deep(hr) { border:none; border-top:1px solid rgba(255,255,255,.1); margin:8px 0; }
.rich-content :deep(table) { border-collapse:collapse; width:100%; margin:6px 0; }
.rich-content :deep(td),
.rich-content :deep(th)    { border:1px solid rgba(255,255,255,.15); padding:5px 10px; }
.rich-content :deep(th)    { background:rgba(255,255,255,.06); font-weight:600; }
</style>