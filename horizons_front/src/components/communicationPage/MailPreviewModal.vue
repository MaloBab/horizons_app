<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-all duration-200 ease-out"
      leave-active-class="transition-all duration-150 ease-in"
      enter-from-class="opacity-0"
      leave-to-class="opacity-0"
    >
      <div
        v-if="show"
        class="fixed inset-0 z-50 flex items-center justify-center p-6 bg-black/70 backdrop-blur-sm"
        @click.self="$emit('close')"
      >
        <Transition
          enter-active-class="transition-all duration-200 ease-out"
          leave-active-class="transition-all duration-150 ease-in"
          enter-from-class="opacity-0 scale-95 translate-y-2"
          leave-to-class="opacity-0 scale-95 translate-y-2"
        >
          <div
            v-if="show"
            class="bg-slate-900 border border-white/10 rounded-2xl shadow-2xl flex flex-col"
            style="width: min(820px, 100%); max-height: 85vh"
          >
            <!-- Header -->
            <div class="shrink-0 flex items-center justify-between px-6 py-4 border-b border-white/8">
              <div class="flex flex-col">
                <h2 class="text-base font-semibold text-white">Aperçu du mail</h2>
                <p v-if="volunteer" class="text-xs text-slate-400 mt-0.5">
                  Rendu pour <strong class="text-slate-300">{{ volunteer.first_name }} {{ volunteer.last_name }}</strong>
                </p>
              </div>

              <div class="flex items-center gap-2">
                <!-- Sélecteur de bénévole -->
                <select
                  v-if="volunteers.length"
                  :value="selectedId"
                  class="text-xs bg-slate-800 border border-white/10 rounded-lg px-3 py-1.5 text-slate-200 outline-none focus:border-cyan-500/40"
                  @change="$emit('select', ($event.target as HTMLSelectElement).value)"
                >
                  <option v-for="v in volunteers" :key="v.id" :value="v.id">
                    {{ v.first_name }} {{ v.last_name }}
                  </option>
                </select>

                <button
                  class="w-8 h-8 flex items-center justify-center rounded-lg text-slate-400 hover:text-white hover:bg-slate-700 transition-colors"
                  @click="$emit('close')"
                >
                  <X class="w-4 h-4" />
                </button>
              </div>
            </div>

            <!-- Objet -->
            <div class="shrink-0 px-6 py-3 border-b border-white/5 flex items-center gap-3">
              <span class="text-xs text-slate-500 font-semibold uppercase tracking-wider">Objet</span>
              <span class="text-sm text-slate-200">{{ renderedSubject }}</span>
            </div>

            <!-- Corps -->
            <div class="flex-1 overflow-y-auto">
              <!-- Onglets -->
              <div class="flex border-b border-white/5 px-6">
                <button
                  v-for="tab in tabs"
                  :key="tab.id"
                  class="px-4 py-2.5 text-xs font-medium border-b-2 transition-colors"
                  :class="activeTab === tab.id
                    ? 'border-cyan-500 text-cyan-400'
                    : 'border-transparent text-slate-500 hover:text-slate-300'"
                  @click="activeTab = tab.id"
                >
                  {{ tab.label }}
                </button>
              </div>

              <!-- Corps du mail rendu -->
              <div v-if="activeTab === 'mail'" class="p-6">
                <div
                  class="prose prose-invert prose-sm max-w-none bg-slate-800/40 rounded-xl p-5 border border-white/5 text-slate-200"
                  v-html="renderedBody || '<p class=\'text-slate-600\'>Aucun contenu rédigé.</p>'"
                />
              </div>

              <!-- Planning personnel rendu (iframe) -->
              <div v-else-if="activeTab === 'schedule'" class="p-6">
                <div class="rounded-xl overflow-hidden border border-white/8 bg-[#0f1623]">
                  <iframe
                    ref="scheduleIframe"
                    class="w-full border-0"
                    style="min-height: 500px"
                    title="Planning personnel"
                  />
                </div>
              </div>
            </div>

            <!-- Footer -->
            <div class="shrink-0 px-6 py-4 border-t border-white/8 flex items-center justify-end gap-3">
              <button
                class="px-4 py-2 text-sm bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
                @click="$emit('close')"
              >
                Fermer
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { X } from 'lucide-vue-next'
import type { Volunteer } from '../../types/benevole.types'
import type { JobWithRelations } from '../../types/planning.types'
import { interpolateTemplate } from '../../composables/useMailTemplate'
import type { FestivalConfig } from '../../composables/useMailTemplate'
import { generatePersonalScheduleHtml } from '../../templates/personalSchedule.template'

const props = defineProps<{
  show:             boolean
  volunteer:        Volunteer | null
  volunteers:       Volunteer[]
  selectedId:       string
  subject:          string
  bodyHtml:         string
  volunteerJobs:    JobWithRelations[]
  allVolunteers:    Volunteer[]
  assignmentsByJob: Map<number, { volunteer_id: string }[]>
  festivalConfig?:  FestivalConfig
}>()

defineEmits<{
  close:  []
  select: [id: string]
}>()

const activeTab      = ref<'mail' | 'schedule'>('mail')
const scheduleIframe = ref<HTMLIFrameElement | null>(null)

const tabs = [
  { id: 'mail'     as const, label: 'Corps du mail' },
  { id: 'schedule' as const, label: 'Planning personnel (PJ)' },
]

// ── Rendu du corps du mail ────────────────────────────────────────────────────
const renderedBody = computed(() => {
  if (!props.volunteer) return ''
  return interpolateTemplate(
    props.bodyHtml,
    props.volunteer,
    props.volunteerJobs,
    props.festivalConfig,
  )
})

// ── Rendu de l'objet ─────────────────────────────────────────────────────────
// Utilise interpolateTemplate pour supporter toutes les variables (dont {{festival_*}})
const renderedSubject = computed(() => {
  if (!props.volunteer) return props.subject
  return interpolateTemplate(
    props.subject,
    props.volunteer,
    props.volunteerJobs,
    props.festivalConfig,
  )
})

const scheduleHtml = computed(() => {
  if (!props.volunteer) return ''
  return generatePersonalScheduleHtml(
    props.volunteer,
    props.volunteerJobs,
    props.allVolunteers,
    props.assignmentsByJob,
  )
})

function injectSchedule() {
  const iframe = scheduleIframe.value
  if (!iframe) return
  const doc = iframe.contentDocument ?? iframe.contentWindow?.document
  if (!doc) return
  doc.open()
  doc.write(scheduleHtml.value)
  doc.close()

  iframe.onload = () => {
    const body = iframe.contentDocument?.body
    if (body) {
      iframe.style.height = `${body.scrollHeight + 32}px`
    }
  }
}

watch(
  [activeTab, scheduleHtml],
  ([tab]) => {
    if (tab === 'schedule') {
      nextTick(injectSchedule)
    }
  },
)

watch(
  () => props.show,
  (val) => {
    if (val && activeTab.value === 'schedule') {
      nextTick(injectSchedule)
    }
    if (val) activeTab.value = 'mail'
  },
)
</script>