<template>
  <div class="flex flex-wrap items-center gap-3 px-5 py-3.5 bg-slate-900/70 border border-white/8 rounded-xl backdrop-blur-sm">

    <!-- Téléchargements -->
    <div class="flex items-center gap-2 flex-wrap">
      <span class="text-xs font-semibold uppercase tracking-widest text-slate-500 mr-1">
        Télécharger
      </span>

      <!-- Planning général -->
      <button
        class="flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium bg-slate-800
               hover:bg-slate-700 border border-white/8 hover:border-white/15
               text-slate-300 hover:text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        :disabled="isDownloadingGeneral"
        @click="downloadGeneral"
      >
        <FileDown class="w-3.5 h-3.5" />
        Planning général
        <Loader2 v-if="isDownloadingGeneral" class="w-3 h-3 animate-spin" />
      </button>

      <!-- Planning perso (pour un bénévole sélectionné) -->
      <div class="relative">
        <button
          class="flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium bg-slate-800
                 hover:bg-slate-700 border border-white/8 hover:border-white/15
                 text-slate-300 hover:text-white transition-all"
          @click="showVolunteerPicker = !showVolunteerPicker"
        >
          <UserCheck class="w-3.5 h-3.5" />
          Planning bénévole
          <ChevronDown class="w-3 h-3 transition-transform" :class="showVolunteerPicker && 'rotate-180'" />
        </button>

        <Transition
          enter-active-class="transition-all duration-150 ease-out"
          leave-active-class="transition-all duration-100 ease-in"
          enter-from-class="opacity-0 translate-y-1"
          leave-to-class="opacity-0 translate-y-1"
        >
          <div
            v-if="showVolunteerPicker"
            v-click-outside="() => showVolunteerPicker = false"
            class="absolute bottom-full mb-2 left-0 w-64 bg-slate-800 border border-white/10
                   rounded-xl shadow-2xl overflow-hidden z-20"
          >
            <div class="p-2 border-b border-white/5">
              <input
                v-model="volunteerSearch"
                type="text"
                placeholder="Rechercher…"
                class="w-full px-3 py-1.5 text-xs bg-slate-900/60 border border-white/8
                       rounded-lg text-slate-200 placeholder-slate-600 outline-none"
              />
            </div>
            <div class="max-h-48 overflow-y-auto p-1">
              <button
                v-for="v in filteredVolunteers"
                :key="v.id"
                class="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-xs text-slate-300
                       hover:text-white hover:bg-slate-700/60 transition-colors text-left"
                :disabled="downloadingVolunteerId === v.id"
                @click="downloadPersonal(v)"
              >
                <span class="w-5 h-5 rounded-full bg-slate-700 flex items-center justify-center text-[9px] font-bold shrink-0">
                  {{ v.first_name[0] }}{{ v.last_name[0] }}
                </span>
                <span class="flex-1 truncate">{{ v.first_name }} {{ v.last_name }}</span>
                <Loader2 v-if="downloadingVolunteerId === v.id" class="w-3 h-3 animate-spin shrink-0 text-cyan-400" />
              </button>
              <p v-if="filteredVolunteers.length === 0" class="text-center text-xs text-slate-600 py-3">
                Aucun résultat
              </p>
            </div>
          </div>
        </Transition>
      </div>
    </div>

    <div class="h-5 w-px bg-white/10 hidden sm:block" />

    <!-- Prévisualisation -->
    <button
      class="flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium bg-slate-800
             hover:bg-slate-700 border border-white/8 hover:border-cyan-500/30
             text-slate-300 hover:text-cyan-300 transition-all"
      @click="$emit('preview')"
    >
      <Eye class="w-3.5 h-3.5" />
      Aperçu
    </button>

    <div class="h-5 w-px bg-white/10 hidden sm:block" />

    <!-- ── Toggle pièce jointe ── -->
    <button
      class="flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium border transition-all"
      :class="includeScheduleModel
        ? 'bg-violet-500/12 border-violet-500/25 text-violet-300'
        : 'bg-slate-800 border-white/8 text-slate-400 hover:text-slate-300 hover:border-white/15'"
      :title="includeScheduleModel
        ? 'Le planning personnel sera joint au mail'
        : 'Aucune pièce jointe'"
      @click="includeScheduleModel = !includeScheduleModel"
    >
      <Paperclip class="w-3.5 h-3.5" />
      <span>Planning en PJ</span>
      <!-- Indicateur on/off -->
      <span
        class="w-4 h-4 rounded-full flex items-center justify-center transition-colors"
        :class="includeScheduleModel ? 'bg-violet-500 text-white' : 'bg-slate-700 text-slate-500'"
      >
        <Check v-if="includeScheduleModel" class="w-2.5 h-2.5" />
        <X v-else class="w-2.5 h-2.5" />
      </span>
    </button>

    <!-- Spacer -->
    <div class="flex-1" />

    <!-- Bouton envoi principal -->
    <button
      class="flex items-center gap-2.5 px-5 py-2.5 rounded-xl text-sm font-semibold
             transition-all duration-200 shadow-lg"
      :class="canSend
        ? 'bg-linear-to-r from-cyan-600 to-cyan-500 hover:from-cyan-500 hover:to-cyan-400 text-white shadow-cyan-900/40 hover:shadow-cyan-800/40 hover:-translate-y-px'
        : 'bg-slate-700/50 text-slate-500 cursor-not-allowed'"
      :disabled="!canSend || isSending"
      @click="$emit('send')"
    >
      <Send class="w-4 h-4" />
      <span v-if="!isSending">Envoyer à tous ({{ recipientCount }})</span>
      <span v-else class="flex items-center gap-2">
        <Loader2 class="w-4 h-4 animate-spin" />
        Envoi en cours…
      </span>
    </button>

  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  FileDown, UserCheck, ChevronDown, Eye, Send, Loader2,
  Paperclip, Check, X,
} from 'lucide-vue-next'
import type { Volunteer }        from '../../types/benevole.types'
import type { JobWithRelations } from '../../types/planning.types'
import { generatePersonalScheduleHtml } from '../../templates/personalSchedule.template'
import { generateGeneralScheduleHtml }  from '../../templates/generalSchedule.template'
import { downloadPdf } from '../../composables/useMailTemplate'

const props = defineProps<{
  volunteers:             Volunteer[]
  jobs:                   JobWithRelations[]
  allVolunteers:          Volunteer[]
  assignmentsByJob:       Map<number, { volunteer_id: string }[]>
  assignmentsByVolunteer: Map<string, { job_id: number }[]>
  canSend:                boolean
  isSending:              boolean
  recipientCount:         number
  includeSchedule:        boolean
}>()

const emit = defineEmits<{
  preview:                  []
  send:                     []
  'update:includeSchedule': [v: boolean]
}>()

// ── Toggle pièce jointe ────────────────────────────────────────────────────────
const includeScheduleModel = computed({
  get: () => props.includeSchedule,
  set: (v) => emit('update:includeSchedule', v),
})

// ── Téléchargement planning général ───────────────────────────────────────────
const isDownloadingGeneral = ref(false)

async function downloadGeneral() {
  isDownloadingGeneral.value = true
  try {
    const html = generateGeneralScheduleHtml(props.jobs, props.allVolunteers, props.assignmentsByJob)
    await downloadPdf(html, 'planning_general.pdf')
  } finally {
    isDownloadingGeneral.value = false
  }
}

// ── Téléchargement planning bénévole ──────────────────────────────────────────
const showVolunteerPicker    = ref(false)
const volunteerSearch        = ref('')
const downloadingVolunteerId = ref<string | null>(null)

const filteredVolunteers = computed(() => {
  const q = volunteerSearch.value.toLowerCase()
  return props.volunteers.filter(v =>
    !q || `${v.first_name} ${v.last_name}`.toLowerCase().includes(q)
  )
})

async function downloadPersonal(v: Volunteer) {
  downloadingVolunteerId.value = v.id
  try {
    const volunteerJobs = (props.assignmentsByVolunteer.get(v.id) ?? [])
      .map(a => props.jobs.find(j => j.id === a.job_id))
      .filter(Boolean) as JobWithRelations[]
    const html = generatePersonalScheduleHtml(v, volunteerJobs, props.allVolunteers, props.assignmentsByJob)
    await downloadPdf(html, `planning_${v.first_name}_${v.last_name}.pdf`)
    showVolunteerPicker.value = false
  } finally {
    downloadingVolunteerId.value = null
  }
}

// ── Directive v-click-outside ─────────────────────────────────────────────────
const clickOutsideHandlers = new WeakMap<HTMLElement, (e: MouseEvent) => void>()
const vClickOutside = {
  mounted(el: HTMLElement, binding: { value: () => void }) {
    const handler = (e: MouseEvent) => { if (!el.contains(e.target as Node)) binding.value() }
    clickOutsideHandlers.set(el, handler)
    document.addEventListener('mousedown', handler)
  },
  unmounted(el: HTMLElement) {
    const handler = clickOutsideHandlers.get(el)
    if (handler) { document.removeEventListener('mousedown', handler); clickOutsideHandlers.delete(el) }
  },
}
</script>