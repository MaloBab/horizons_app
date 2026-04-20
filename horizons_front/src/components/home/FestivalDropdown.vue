<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 scale-95 -translate-y-1"
      enter-to-class="opacity-100 scale-100 translate-y-0"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100 scale-100 translate-y-0"
      leave-to-class="opacity-0 scale-95 -translate-y-1"
    >
      <div
        v-if="modelValue"
        :style="dropdownStyle"
        class="fixed z-9999 w-80"
        v-click-outside="close"
        @click.stop
      >
        <div class="bg-slate-900/95 backdrop-blur-2xl border border-white/10 rounded-2xl shadow-2xl shadow-black/60 overflow-hidden outline-none" tabindex="-1" ref="containerRef" @keydown.enter.prevent="handleSave">

          <!-- Header -->
          <div class="px-5 pt-5 pb-4 border-b border-white/8">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center">
                <Settings class="w-4 h-4 text-cyan-400" />
              </div>
              <div>
                <p class="text-sm font-semibold text-white">Paramètres du festival</p>
                <p class="text-[11px] text-slate-500 mt-0.5">Modifier les informations générales</p>
              </div>
            </div>
          </div>

          <!-- Formulaire -->
          <div class="p-5 space-y-4">

            <div class="space-y-1.5">
              <label class="text-[11px] font-medium text-slate-400 uppercase tracking-wider">Nom</label>
              <input id="festival-name"
                v-model="form.name"
                type="text"
                placeholder="Nom du festival"
                class="w-full bg-slate-800/60 border border-white/8 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-cyan-500/50 focus:bg-slate-800 transition-all"
              />
            </div>

            <div class="space-y-1.5">
              <label class="text-[11px] font-medium text-slate-400 uppercase tracking-wider">Édition</label>
              <input id="festival-edition"
                v-model.number="form.edition"
                type="number"
                min="1"
                placeholder="N° d'édition"
                class="w-full bg-slate-800/60 border border-white/8 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-cyan-500/50 focus:bg-slate-800 transition-all"
              />
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div class="space-y-1.5">
                <label class="text-[11px] font-medium text-slate-400 uppercase tracking-wider">Début</label>
                <input id="festival-start-date"
                  v-model="form.start_date"
                  type="date"
                  class="w-full bg-slate-800/60 border border-white/8 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-500/50 focus:bg-slate-800 transition-all"
                />
              </div>
              <div class="space-y-1.5">
                <label class="text-[11px] font-medium text-slate-400 uppercase tracking-wider">Fin</label>
                <input id="festival-end-date"
                  v-model="form.end_date"
                  type="date"
                  class="w-full bg-slate-800/60 border border-white/8 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-500/50 focus:bg-slate-800 transition-all"
                />
              </div>
            </div>

            <div class="space-y-1.5">
              <label class="text-[11px] font-medium text-slate-400 uppercase tracking-wider">Lieu</label>
              <input id="festival-location"
                v-model="form.location_name"
                type="text"
                placeholder="Nom du lieu"
                class="w-full bg-slate-800/60 border border-white/8 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-cyan-500/50 focus:bg-slate-800 transition-all"
              />
            </div>

            <div class="space-y-1.5">
              <label class="text-[11px] font-medium text-slate-400 uppercase tracking-wider">Ville</label>
              <input id="festival-city"
                v-model="form.location_city"
                type="text"
                placeholder="Ville"
                class="w-full bg-slate-800/60 border border-white/8 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-cyan-500/50 focus:bg-slate-800 transition-all"
              />
            </div>

            <p v-if="error" class="text-xs text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">
              {{ error }}
            </p>

          </div>

          <!-- Footer -->
          <div class="px-5 pb-5 flex items-center gap-3">
            <button
              class="flex-1 px-4 py-2 rounded-lg text-sm font-medium text-slate-400 hover:text-white hover:bg-white/5 transition-all cursor-pointer bg-transparent border border-transparent"
              @click="close"
            >
              Annuler
            </button>
            <button
              class="flex-1 px-4 py-2 rounded-lg text-sm font-semibold bg-cyan-500/15 border border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/25 hover:border-cyan-500/50 transition-all cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              :disabled="loading"
              @click="handleSave"
            >
              <span v-if="loading" class="w-3.5 h-3.5 border-2 border-cyan-400/30 border-t-cyan-400 rounded-full animate-spin" />
              <span>{{ loading ? 'Sauvegarde…' : 'Enregistrer' }}</span>
            </button>
          </div>

        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script lang="ts">
export default { inheritAttrs: false }
</script>

<script setup lang="ts">
import { reactive, watch, ref, nextTick } from 'vue'
import { storeToRefs } from 'pinia'
import { Settings } from 'lucide-vue-next'
import { useFestivalStore } from '../../stores/useFestivalStore'
import { vClickOutside } from '../../directives/clickOutside'
import type { CSSProperties } from 'vue'

// ── Props / emits ────────────────────────────────────────────
const props = defineProps<{
  modelValue: boolean          // v-model : ouvert / fermé
  dropdownStyle: CSSProperties  // position calculée par le parent
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

// ── Festival logic ───────────────────────────────────────────
const festivalStore = useFestivalStore()
const { festival, isLoading: loading, error } = storeToRefs(festivalStore)
const { fetchFestival, createFestival, updateFestival } = festivalStore

const form = reactive({
  name: '',
  edition: 1,
  start_date: '',
  end_date: '',
  location_name: '',
  location_city: '',
})

function populateForm() {
  if (!festival.value) return
  form.name          = festival.value.name
  form.edition       = festival.value.edition
  form.start_date    = festival.value.start_date
  form.end_date      = festival.value.end_date
  form.location_name = festival.value.location_name
  form.location_city = festival.value.location_city
}

// Charge + pré-remplit quand le dropdown s'ouvre
const containerRef = ref<HTMLElement | null>(null)

watch(() => props.modelValue, async (open) => {
  if (!open) return
  if (!festival.value) await fetchFestival()
  populateForm()
  await nextTick()
  containerRef.value?.focus()
})

watch(festival, populateForm)

// ── Actions ──────────────────────────────────────────────────
function close() {
  emit('update:modelValue', false)
}

async function handleSave() {
  if (loading.value) return
  const data = { ...form }
  const ok = festival.value
    ? await updateFestival(data)
    : await createFestival(data)

  if (ok) {
    close()
  }
}
</script>