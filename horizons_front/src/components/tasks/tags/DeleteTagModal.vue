<template>
  <Transition name="modal">
    <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/70 backdrop-blur-sm" @click="emit('close')" />
      <div class="relative z-10 w-full max-w-sm bg-slate-900 border border-white/10 rounded-2xl shadow-2xl p-6">

        <div class="flex items-center justify-between mb-2">
          <h2 class="text-base font-semibold text-white" style="font-family: 'Instrument Serif', serif">Supprimer des tags</h2>
          <button @click="emit('close')" class="p-1.5 rounded-lg text-slate-500 hover:text-white hover:bg-white/10 transition-all">
            <X class="w-4 h-4" />
          </button>
        </div>
        <p class="text-xs text-slate-500 mb-4">Sélectionnez les tags à supprimer. Cette action est irréversible.</p>

        <div v-if="tagsLoading" class="flex items-center gap-2 text-xs text-slate-500 py-3">
          <div class="w-3 h-3 rounded-full border-2 border-cyan-500/40 border-t-cyan-400 animate-spin" />
          Chargement…
        </div>
        <p v-else-if="tags.length === 0" class="text-xs text-slate-500 italic py-3">Aucun tag disponible.</p>
        <div v-else class="flex flex-col gap-1 max-h-60 overflow-y-auto custom-scrollbar">
          <label
            v-for="tag in tags" :key="tag.id"
            class="flex items-center gap-3 px-3 py-2.5 rounded-xl cursor-pointer transition-all"
            :class="selected.has(tag.id)
              ? 'bg-red-500/10 border border-red-500/20'
              : 'border border-transparent hover:bg-white/5'"
          >
            <input id="delete-tag"
              type="checkbox" :checked="selected.has(tag.id)"
              @change="toggle(tag.id)"
              class="w-4 h-4 rounded accent-red-400 cursor-pointer shrink-0"
            />
            <span
              class="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium border"
              :style="{ background: tag.color + '22', borderColor: tag.color + '44', color: tag.color }"
            >{{ tag.name }}</span>
          </label>
        </div>

        <div class="flex items-center justify-end gap-3 mt-5">
          <button @click="emit('close')" class="px-4 py-2 rounded-xl text-sm text-slate-400 hover:text-white transition-colors">
            Annuler
          </button>
          <button
            @click="submit"
            :disabled="selected.size === 0 || loading"
            class="px-5 py-2 rounded-xl text-sm font-medium bg-red-500/15 text-red-300 border border-red-500/30 hover:bg-red-500/25 transition-all disabled:opacity-30 disabled:cursor-not-allowed"
          >
            <span v-if="loading" class="flex items-center gap-1.5">
              <div class="w-3 h-3 rounded-full border-2 border-red-500/40 border-t-red-400 animate-spin" />
              Suppression…
            </span>
            <span v-else>Supprimer ({{ selected.size }})</span>
          </button>
        </div>

      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { X } from 'lucide-vue-next'
import { useTags } from '../../../composables/useTags'

const props = defineProps<{ open: boolean }>()
const emit  = defineEmits<{ close: []; deleted: [ids: number[]] }>()

const { tags, isLoading: tagsLoading, deleteTag } = useTags()

const selected = ref<Set<number>>(new Set())
const loading  = ref(false)

// Reset selection every time the modal opens
watch(() => props.open, (v) => { if (v) selected.value = new Set() })

const toggle = (id: number) => {
  const s = new Set(selected.value)
  s.has(id) ? s.delete(id) : s.add(id)
  selected.value = s
}

const submit = async () => {
  if (selected.value.size === 0 || loading.value) return
  loading.value = true
  const ids = [...selected.value]
  await Promise.all(ids.map(id => deleteTag(id)))
  loading.value  = false
  emit('deleted', ids)
  emit('close')
}
</script>

<style scoped>
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s ease; }
.modal-enter-from,   .modal-leave-to     { opacity: 0; }
.modal-enter-active .relative,
.modal-leave-active .relative { transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1); }
.modal-enter-from   .relative,
.modal-leave-to     .relative { transform: scale(0.95) translateY(8px); }
</style>