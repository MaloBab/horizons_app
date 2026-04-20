<template>
  <div class="flex flex-col h-full bg-linear-to-br from-slate-900 via-slate-800 to-slate-900 text-white overflow-hidden">

    <header class="shrink-0 flex items-center justify-between px-6 py-4 border-b border-white/8">
      <div class="flex items-center gap-3">
        <button
          class="w-8 h-8 flex items-center justify-center rounded-lg text-slate-400
                 hover:text-white hover:bg-slate-700 transition-colors"
          @click="router.push('/assignments')"
        >
          <ArrowLeft class="w-4 h-4" />
        </button>
        <div>
          <h1 class="text-lg font-bold text-white leading-tight">Communication Bénévoles</h1>
          <p class="text-xs text-slate-500 mt-0.5">Rédigez et envoyez les mails d'affectations personnalisés</p>
        </div>
      </div>

      <!-- Stats rapides -->
      <div class="hidden sm:flex items-center gap-5">
        <div class="text-center">
          <p class="text-lg font-bold text-white leading-none">{{ volunteers.length }}</p>
          <p class="text-[10px] text-slate-500 mt-0.5">Bénévoles</p>
        </div>
        <div class="w-px h-8 bg-white/8" />
        <div class="text-center">
          <p class="text-lg font-bold text-emerald-400 leading-none">{{ assignedCount }}</p>
          <p class="text-[10px] text-slate-500 mt-0.5">Affectés</p>
        </div>
        <div class="w-px h-8 bg-white/8" />
        <div class="text-center">
          <p class="text-lg font-bold text-cyan-400 leading-none">{{ store.jobs.length }}</p>
          <p class="text-[10px] text-slate-500 mt-0.5">Postes</p>
        </div>
      </div>
    </header>

    <div v-if="isLoading" class="flex flex-col items-center justify-center flex-1 gap-3 text-slate-500">
      <Loader2 class="w-8 h-8 animate-spin text-cyan-400" />
      <span class="animate-pulse text-sm">Chargement…</span>
    </div>

    <div v-else class="flex flex-1 overflow-hidden gap-0">

      <!-- Colonne gauche : destinataires -->
      <aside class="shrink-0 w-64 flex flex-col border-r border-white/8 px-4 py-4 overflow-hidden">
        <MailRecipientList
          :volunteers="volunteers"
          :assignments-by-volunteer="store.assignmentsByVolunteer"
          @update:selected-ids="selectedIds = $event"
        />
      </aside>

      <!-- Zone centrale : éditeur -->
      <main class="flex-1 flex flex-col overflow-hidden px-5 py-4 gap-4 min-w-0">

        <div class="flex-1 flex gap-4 overflow-hidden min-h-0">

          <!-- Colonne éditeur -->
          <div class="flex-1 flex flex-col gap-3 overflow-y-auto min-w-0">
            <MailTemplateEditor
              ref="editorRef"
              :subject="subject"
              :body="bodyHtml"
              :api-base-url="API_BASE_URL"
              @update:subject="subject = $event"
              @update:body="bodyHtml = $event"
              @saved="onTemplateSaved"
              @deleted="onTemplateDeleted"
              @error="showToast($event, 'error')"
            />
          </div>

          <!-- Colonne variables -->
          <aside class="shrink-0 w-56 flex flex-col overflow-y-auto">
            <MailVariablesPanel @insert="insertVariable" />
          </aside>

        </div>

        <!-- Barre d'actions -->
        <MailDownloadBar
          :volunteers="selectedVolunteers"
          :jobs="store.jobs"
          :all-volunteers="volunteers"
          :assignments-by-job="store.assignmentsByJob"
          :assignments-by-volunteer="store.assignmentsByVolunteer"
          :can-send="canSend"
          :is-sending="isSending"
          :recipient-count="selectedIds.size"
          :include-schedule="includeSchedule"
          @update:include-schedule="includeSchedule = $event"
          @preview="openPreview"
          @send="handleSend"
        />

      </main>
    </div>

    <!-- Modales -->
    <MailPreviewModal
      :show="showPreview"
      :volunteer="previewVolunteer"
      :volunteers="volunteers"
      :selected-id="previewVolunteerId"
      :subject="subject"
      :body-html="bodyHtml"
      :volunteer-jobs="previewVolunteerJobs"
      :all-volunteers="volunteers"
      :assignments-by-job="store.assignmentsByJob"
      :festival-config="festivalConfig"
      @close="showPreview = false"
      @select="previewVolunteerId = $event"
    />

    <MailSendProgressModal
      :show="showProgress"
      :done="progressDone"
      :total="progressTotal"
      :results="sendResults"
      @close="showProgress = false"
      @retry-errors="handleRetryErrors"
    />

    <AppToast
      :show="toast.show"
      :message="toast.message"
      :type="toast.type"
      @close="hideToast"
    />

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter }     from 'vue-router'
import { ArrowLeft, Loader2 } from 'lucide-vue-next'
import { storeToRefs }   from 'pinia'

import { useAssignmentStore }  from '../../stores/useAssignmentStore'
import { useFestivalStore }    from '../../stores/useFestivalStore'
import { useBenevoles }        from '../../composables/useBenevoles'
import {
  useMailTemplate,
  sendBatchMails,
  type SendResult,
  type MailTemplateRecord,
  type FestivalConfig,
} from '../../composables/useMailTemplate'
import { useToast }            from '../../composables/useToast'
import type { Volunteer }      from '../../types/benevole.types'
import type { JobWithRelations } from '../../types/planning.types'

import MailRecipientList     from './MailRecipientList.vue'
import MailTemplateEditor    from './MailTemplateEditor.vue'
import MailVariablesPanel    from './MailVariablesPanel.vue'
import MailDownloadBar       from './MailDownloadBar.vue'
import MailPreviewModal      from './MailPreviewModal.vue'
import MailSendProgressModal from './MailSendProgressModal.vue'
import AppToast              from '../shared/Toast.vue'

// ── Config ─────────────────────────────────────────────────────────────────────
const router       = useRouter()
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

// ── Store & composables ────────────────────────────────────────────────────────
const store                           = useAssignmentStore()
const festivalStore                   = useFestivalStore()
const { isLoading }                   = storeToRefs(store)
const { volunteers, fetchVolunteers } = useBenevoles()
const { subject, bodyHtml }           = useMailTemplate()
const { toast, showToast, hideToast } = useToast()

// ── Festival config (pour l'interpolation des variables {{festival_*}}) ────────
const festivalConfig = computed<FestivalConfig | undefined>(() => {
  const f = festivalStore.festival
  if (!f) return undefined
  return {
    name:          f.name,
    edition:       f.edition,
    location_name: f.location_name,
    location_city: f.location_city,
    start_date:    f.start_date,
    end_date:      f.end_date,
  }
})

// ── Chargement ─────────────────────────────────────────────────────────────────
onMounted(async () => {
  await Promise.all([
    store.jobs.length === 0 || volunteers.value.length === 0 ? store.fetchAll() : Promise.resolve(),
    volunteers.value.length === 0 ? fetchVolunteers() : Promise.resolve(),
    festivalStore.festival === null ? festivalStore.fetchFestival() : Promise.resolve(),
  ])
})

// ── Stats ───────────────────────────────────────────────────────────────────────
const assignedCount = computed(() =>
  volunteers.value.filter(v => (store.assignmentsByVolunteer.get(v.id)?.length ?? 0) > 0).length
)

// ── Sélection des destinataires ────────────────────────────────────────────────
const selectedIds = ref<Set<string>>(new Set())
const selectedVolunteers = computed(() =>
  volunteers.value.filter(v => selectedIds.value.has(v.id))
)

// ── Template editor ref ────────────────────────────────────────────────────────
const editorRef = ref<InstanceType<typeof MailTemplateEditor> | null>(null)

function insertVariable(key: string) {
  editorRef.value?.insertAtCursor(key)
}

// ── Callbacks templates ────────────────────────────────────────────────────────
function onTemplateSaved(t: MailTemplateRecord) {
  showToast(`Template «${t.title}» sauvegardé`, 'success')
}
function onTemplateDeleted(_id: string) {
  showToast('Template supprimé', 'success')
}

// ── Pièce jointe ───────────────────────────────────────────────────────────────
const includeSchedule = ref(true)

// ── Validation envoi ───────────────────────────────────────────────────────────
const canSend = computed(() =>
  selectedIds.value.size > 0 &&
  bodyHtml.value.trim().length > 0 &&
  subject.value.trim().length > 0
)

// ── Progression envoi ──────────────────────────────────────────────────────────
const isSending      = ref(false)
const showProgress   = ref(false)
const progressDone   = ref(0)
const progressTotal  = ref(0)
const sendResults    = ref<SendResult[]>([])

async function handleSend() {
  if (!canSend.value) return
  isSending.value     = true
  showProgress.value  = true
  progressDone.value  = 0
  progressTotal.value = selectedVolunteers.value.length
  sendResults.value   = []

  try {
    sendResults.value = await sendBatchMails({
      apiBaseUrl:             API_BASE_URL,
      volunteers:             selectedVolunteers.value,
      subject:                subject.value,
      bodyHtml:               bodyHtml.value,
      jobs:                   store.jobs,
      assignmentsByVolunteer: store.assignmentsByVolunteer,
      allVolunteers:          volunteers.value,
      assignmentsByJob:       store.assignmentsByJob,
      includeSchedule:        includeSchedule.value,
      onProgress: (done, total) => {
        progressDone.value  = done
        progressTotal.value = total
      },
    })

    const errorCount = sendResults.value.filter(r => !r.success).length
    if (errorCount === 0) {
      showToast(`${selectedVolunteers.value.length} mail(s) envoyé(s) avec succès`, 'success')
    } else {
      showToast(`${errorCount} échec(s) sur ${selectedVolunteers.value.length} envois`, 'error')
    }
  } catch (e) {
    showToast("Erreur inattendue lors de l'envoi", 'error')
  } finally {
    isSending.value = false
  }
}

async function handleRetryErrors() {
  const failed = sendResults.value
    .filter(r => !r.success)
    .map(r => volunteers.value.find(v => v.email === r.email))
    .filter(Boolean) as Volunteer[]

  if (!failed.length) return

  progressDone.value  = 0
  progressTotal.value = failed.length
  sendResults.value   = []

  try {
    sendResults.value = await sendBatchMails({
      apiBaseUrl:             API_BASE_URL,
      volunteers:             failed,
      subject:                subject.value,
      bodyHtml:               bodyHtml.value,
      jobs:                   store.jobs,
      assignmentsByVolunteer: store.assignmentsByVolunteer,
      allVolunteers:          volunteers.value,
      assignmentsByJob:       store.assignmentsByJob,
      includeSchedule:        includeSchedule.value,
      onProgress: (done, total) => {
        progressDone.value  = done
        progressTotal.value = total
      },
    })
  } catch {
    showToast('Erreur lors du réessai', 'error')
  }
}

// ── Prévisualisation ───────────────────────────────────────────────────────────
const showPreview        = ref(false)
const previewVolunteerId = ref<string>('')

const previewVolunteer = computed(() =>
  volunteers.value.find(v => v.id === previewVolunteerId.value) ?? volunteers.value[0] ?? null
)

const previewVolunteerJobs = computed<JobWithRelations[]>(() => {
  const id = previewVolunteer.value?.id
  if (!id) return []
  return (store.assignmentsByVolunteer.get(id) ?? [])
    .map(a => store.jobs.find(j => j.id === a.job_id))
    .filter(Boolean) as JobWithRelations[]
})

function openPreview() {
  if (!volunteers.value.length) return
  previewVolunteerId.value = volunteers.value[0]!.id
  showPreview.value = true
}
</script>