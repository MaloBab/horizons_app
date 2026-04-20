<template>
  <Transition name="modal">
    <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/70 backdrop-blur-sm" @click="emit('close')" />
      <div class="relative z-10 w-full max-w-sm bg-slate-900 border border-white/10 rounded-2xl shadow-2xl p-6">

        <div class="flex items-center justify-between mb-5">
          <h2 class="text-base font-semibold text-white" style="font-family: 'Instrument Serif', serif">Nouveau tag</h2>
          <button @click="emit('close')" class="p-1.5 rounded-lg text-slate-500 hover:text-white hover:bg-white/10 transition-all">
            <X class="w-4 h-4" />
          </button>
        </div>

        <div class="flex flex-col gap-4">
          <div>
            <label class="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1.5">Nom du tag</label>
            <input id="add-tag-modal"
              v-model="name" type="text" placeholder="Ex: Urgent, Design, Dev…" maxlength="25"
              class="w-full bg-slate-800/60 border border-white/10 rounded-xl px-3 py-2.5 text-sm text-slate-300 placeholder-slate-600 outline-none focus:border-cyan-500/40 transition-colors"
              @keydown.enter="submit"
              autofocus
            />
          </div>

          <div>
            <label class="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1.5">Couleur</label>
            <div class="flex items-center gap-3">
              <input id="color-input3" type="color" v-model="color"
                class="w-10 h-10 rounded-xl cursor-pointer bg-transparent border border-white/10 p-1"
              />
              <div class="flex gap-1.5 flex-wrap">
                <button
                  v-for="c in PRESET_COLORS" :key="c"
                  @click="color = c"
                  class="w-6 h-6 rounded-lg border-2 transition-all"
                  :style="{ background: c, borderColor: color === c ? 'white' : 'transparent' }"
                />
              </div>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <span class="text-xs text-slate-500">Aperçu :</span>
            <span
              class="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium border"
              :style="{ background: color + '22', borderColor: color + '44', color }"
            >{{ name || 'Mon tag' }}</span>
          </div>
        </div>

        <div class="flex items-center justify-end gap-3 mt-5">
          <button @click="emit('close')" class="px-4 py-2 rounded-xl text-sm text-slate-400 hover:text-white transition-colors">
            Annuler
          </button>
          <button
            @click="submit"
            :disabled="!name.trim() || loading"
            class="px-5 py-2 rounded-xl text-sm font-medium bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 hover:bg-cyan-500/25 transition-all disabled:opacity-30 disabled:cursor-not-allowed"
          >
            <span v-if="loading" class="flex items-center gap-1.5">
              <div class="w-3 h-3 rounded-full border-2 border-cyan-500/40 border-t-cyan-400 animate-spin" />
              Création…
            </span>
            <span v-else>Créer le tag</span>
          </button>
        </div>

      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { X } from 'lucide-vue-next'
import { useTags } from '../../../composables/useTags'

const PRESET_COLORS = ['#22d3ee', '#a855f7', '#3b82f6', '#10b981', '#f59e0b', '#ec4899', '#ef4444', '#84cc16']

defineProps<{ open: boolean }>()
const emit = defineEmits<{ close: [] }>()

const { createTag } = useTags()

const name    = ref('')
const color   = ref('#22d3ee')
const loading = ref(false)

const submit = async () => {
  if (!name.value.trim() || loading.value) return
  loading.value = true
  await createTag(name.value.trim(), color.value)
  loading.value = false
  name.value    = ''
  color.value   = '#22d3ee'
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