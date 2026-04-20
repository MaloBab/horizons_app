<template>
  <section class="bg-slate-800/50 border border-white/10 rounded-xl p-4">
    <div class="flex items-center justify-between mb-3">
      <h3 class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Description</h3>
      <button v-if="user?.id === task?.assignee?.id"
        @click="editing ? save() : startEdit()"
        class="text-xs transition-colors"
        :class="editing ? 'text-cyan-400 hover:text-cyan-300' : 'text-slate-500 hover:text-cyan-400'"
      >{{ editing ? 'Sauvegarder' : 'Éditer' }}</button>
    </div>

    <TextEditorView v-if="editing" v-model="localHtml" />
    <div v-else ref="previewRef" class="rich-preview text-sm leading-relaxed" />
  </section>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, nextTick } from 'vue'
import TextEditorView from '../richTextEditor/TextEditorView.vue'
import {useUserStore} from '../../../stores/useUserStore'
import type { Task } from '../../../types/task.types';
import { storeToRefs } from 'pinia';

const props = defineProps<{ modelValue: string; task?: Task}>()
const emit  = defineEmits<{ 'update:modelValue': [html: string]; 'editing-change': [editing: boolean] }>()

const editing    = ref(false)
const localHtml  = ref(props.modelValue)
const previewRef = ref<HTMLElement | null>(null)

const userStore = useUserStore()

const {user} = storeToRefs(userStore)

let userEdited = false

const renderPreview = (html: string) => {
  if (!previewRef.value) return
  previewRef.value.innerHTML = html
    || '<p style="color:rgba(148,163,184,0.5);font-style:italic">Aucune description.</p>'
}

watch(() => props.modelValue, async (val) => {
  if (userEdited) return
  localHtml.value = val
  if (!editing.value) {
    await nextTick()
    renderPreview(val)
  }
})

watch(() => props.task?.id, () => {
  userEdited      = false
  editing.value   = false
  emit('editing-change', false)
  localHtml.value = props.modelValue
  nextTick(() => renderPreview(props.modelValue))
})

onMounted(() => {
  if (!userStore.user) userStore.fetchCurrentUser()
  renderPreview(props.modelValue)
})

const startEdit = () => {
  editing.value = true
  emit('editing-change', true)
}

const save = async () => {
  const html    = localHtml.value
  userEdited    = true
  editing.value = false
  emit('editing-change', false)
  emit('update:modelValue', html)
  await nextTick()
  renderPreview(html)
}

defineExpose({
  resetEditing: () => {
    userEdited    = false
    editing.value = false
    emit('editing-change', false)
    nextTick(() => renderPreview(props.modelValue))
  }
})
</script>

<style>
.rich-preview        { color: rgba(203, 213, 225, 0.9); }
.rich-preview p      { margin: 0 0 0.4rem; font-size: 0.875rem; line-height: 1.6; }
.rich-preview h1     { font-size: 1.4em;   font-weight: 700; color: white;                margin: .5em 0 .2em; line-height: 1.2; }
.rich-preview h2     { font-size: 1.2em;   font-weight: 600; color: rgba(255,255,255,.9); margin: .45em 0 .2em; }
.rich-preview h3     { font-size: 1.05em;  font-weight: 600; color: rgba(255,255,255,.8); margin: .4em 0 .15em; }
.rich-preview ul     { list-style: disc;    padding-left: 1.5rem; margin: 0.35rem 0; }
.rich-preview ol     { list-style: decimal; padding-left: 1.5rem; margin: 0.35rem 0; }
.rich-preview li     { font-size: 0.875rem; margin: 0.1rem 0; }
.rich-preview strong,
.rich-preview b      { font-weight: 600; }
.rich-preview em,
.rich-preview i      { font-style: italic; }
.rich-preview u      { text-decoration: underline; }
.rich-preview s,
.rich-preview strike { text-decoration: line-through; opacity: .7; }
.rich-preview table  { border-collapse: collapse; width: 100%; margin: 0.5rem 0; font-size: 0.875rem; }
.rich-preview td,
.rich-preview th     { border: 1px solid rgba(255,255,255,.15); padding: 7px 12px; text-align: left; }
.rich-preview th     { background: rgba(255,255,255,.06); font-weight: 600; color: white; }
.rich-preview blockquote {
  border-left: 3px solid rgba(34,211,238,.45);
  padding: 3px 12px; margin: 6px 0;
  color: rgba(148,163,184,.9);
  background: rgba(255,255,255,.03);
  border-radius: 0 6px 6px 0;
}
.rich-preview code { background: rgba(255,255,255,.08); border-radius: 4px; padding: 1px 5px; font-family: monospace; font-size: .85em; color: #a5f3fc; }
.rich-preview a    { color: #22d3ee; text-decoration: underline; }
.rich-preview hr   { border: none; border-top: 1px solid rgba(255,255,255,.1); margin: 8px 0; }
</style>