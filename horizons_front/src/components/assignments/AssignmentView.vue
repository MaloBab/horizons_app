<template>
  <div class="flex flex-col h-full bg-linear-to-br from-slate-900 via-slate-800 to-slate-900 text-white overflow-hidden">

    <AssignmentSummaryBar
      class="shrink-0"
      @confirm-delete-all="handleDeleteAll"
      @run-algorithm="handleRunAlgorithm"
    />

    <div class="flex flex-1 overflow-hidden">

      <VolunteerSidebar
        v-if="isReady"
        @open-detail="openVolunteerDetail"
        @filter-volunteer="onFilterVolunteer"
        @dragstart="onSidebarDragStart"
        @dragend="onSidebarDragEnd"
      />

      <main class="flex-1 overflow-y-auto px-4 py-4">
        <h1 class="mb-4 text-3xl font-bold bg-gray-400 bg-clip-text text-transparent">Affectations</h1>

        <div v-if="!isReady" class="flex flex-col items-center justify-center h-64 gap-3 text-slate-500">
          <Loader2 class="w-8 h-8 animate-spin text-cyan-400" />
          <span class="animate-pulse text-sm">Chargement des données…</span>
        </div>

        <div
          v-else-if="error"
          class="mb-4 px-4 py-3 bg-red-500/20 border border-red-500/30 rounded-xl text-red-300 text-sm flex items-center gap-2"
        >
          <span>⚠️</span> {{ error }}
          <button @click="reload" class="ml-auto underline hover:no-underline">Réessayer</button>
        </div>

        <AssignmentGantt
          v-else
          ref="ganttRef"
          :key="ganttKey"
          @open-volunteer="openVolunteerDetail"
        />
      </main>

    </div>

    <BenevoleDetailModal
      v-if="selectedVolunteer"
      :volunteer="selectedVolunteer"
      :all-volunteers="volunteers"
      @close="selectedVolunteerId = null"
    />

    <ConfirmDialog
      v-if="showLeaveConfirm"
      title="Modifications non sauvegardées"
      message="Vous avez des modifications non sauvegardées. Voulez-vous quitter sans sauvegarder ?"
      confirm-text="Quitter sans sauvegarder"
      cancel-text="Rester"
      type="danger"
      @confirm="confirmLeave"
      @cancel="showLeaveConfirm = false"
    />

    <ConfirmDialog
      v-if="showDeleteConfirm"
      title="Confirmer la suppression"
      message="Êtes-vous sûr de vouloir supprimer toutes les affectations ? Cette action est irréversible."
      confirm-text="Supprimer tout"
      cancel-text="Annuler"
      type="danger"
      @confirm="deleteAll"
      @cancel="showDeleteConfirm = false"
    />

      <AlgorithmProgressModal
        v-model="showAlgorithmModal"
        :phase="algorithmPhase"
        :progress="algorithmProgress"
        :progress-message="algorithmMessage"
        :log-lines="algorithmLog"
        :stats="algorithmStats"
        :alert-msg="algorithmAlert"
        @run="store.runAlgorithm()"
        @cancel="showAlgorithmModal = false"
      />

    <Teleport to="body">
      <div
        v-if="showFloatingButton"
        class="fixed bottom-6 right-6 z-50 animate-in fade-in slide-in-from-bottom-4 duration-300"
      >
        <button
          @click="handleCommunication"
          class="group flex items-center gap-3 px-6 py-3 rounded-full bg-linear-to-r from-green-500 to-emerald-600 text-white font-medium shadow-lg hover:shadow-xl hover:shadow-green-500/30 hover:-translate-y-2 active:translate-y-0 active:shadow-md transition-all duration-300 border border-white/10"
        >
          <MailIcon class="w-5 h-5 transition-transform duration-300 group-hover:scale-110 group-hover:-rotate-8" />
          <span>Communication Bénévoles</span>
        </button>
      </div>
    </Teleport>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { onBeforeRouteLeave } from 'vue-router'
import { Loader2, MailIcon } from 'lucide-vue-next'
import { storeToRefs } from 'pinia'
import { useAssignmentStore } from '../../stores/useAssignmentStore'
import { useBenevoles } from '../../composables/useBenevoles'
import { useFestivalStore } from '../../stores/useFestivalStore'
import type { Volunteer } from '../../types/benevole.types'
import AssignmentSummaryBar from './AssignmentSummaryBar.vue'
import AssignmentGantt from './AssignmentGantt.vue'
import VolunteerSidebar from './VolunteerSidebar.vue'
import BenevoleDetailModal from '../benevoles/BenevoleDetailModal.vue'
import AlgorithmProgressModal from './AlgorithmProgressModal.vue'
import ConfirmDialog from '../shared/ConfirmDialog.vue'
import { useRouter } from 'vue-router'

const store = useAssignmentStore()
const {algorithmPhase, algorithmProgress, algorithmMessage, algorithmLog, algorithmStats, algorithmAlert, isLoading, error, saveState} = storeToRefs(store)
const { volunteers, fetchVolunteers } = useBenevoles()
const festivalStore = useFestivalStore()
const router = useRouter()

const dataFetched = ref(false)
const ganttRef = ref<InstanceType<typeof AssignmentGantt> | null>(null)

const isReady = computed(() =>
  dataFetched.value &&
  !isLoading.value &&
  festivalStore.festival !== null
)

function onFilterVolunteer(volunteer: Volunteer) {
  ganttRef.value?.setVolunteerFilter(volunteer.id)
}

const showAlgorithmModal = ref(false)
const ganttKey = ref(0)

async function reload() {
  ganttKey.value++
  dataFetched.value = false
  await store.fetchAll()
  dataFetched.value = true
}

onMounted(async () => {
  if (!festivalStore.festival && !festivalStore.isLoading) {
    await festivalStore.fetchFestival()
  }

  if (volunteers.value.length == 0) {
    await fetchVolunteers()
  }  
  
  await store.fetchAll()
  dataFetched.value = true
  pageLoaded.value = true
})

// ── Bouton flottant ───────────────────────────────────────────────────────────
const pageLoaded = ref(false)

const showFloatingButton = computed(() =>
  pageLoaded.value &&
  showAlgorithmModal.value === false &&
  saveState.value === 'saved' &&
  volunteers.value.length > 0
)

function handleCommunication() {
  router.push('/communication')
}
onBeforeUnmount(() => {
  pageLoaded.value = false
})

const selectedVolunteerId = ref<string | null>(null)

const selectedVolunteer = computed<Volunteer | null>(() =>
  selectedVolunteerId.value
    ? (volunteers.value.find(v => v.id === selectedVolunteerId.value) ?? null)
    : null
)

function openVolunteerDetail(volunteerOrId: Volunteer | string) {
  selectedVolunteerId.value = typeof volunteerOrId === 'string'
    ? volunteerOrId
    : volunteerOrId.id
}

// ── Drag ──────────────────────────────────────────────────────────────────────
function onSidebarDragStart(_id: string) {}
function onSidebarDragEnd() {}

// ── Guard navigation ──────────────────────────────────────────────────────────
const showLeaveConfirm  = ref(false)
const showDeleteConfirm = ref(false)
let leaveResolve: ((v: boolean) => void) | null = null

onBeforeRouteLeave(async () => {
  if (saveState.value !== 'unsaved') return true
  showLeaveConfirm.value = true
  return new Promise<boolean>(resolve => { leaveResolve = resolve })
})

function confirmLeave() {
  showLeaveConfirm.value = false
  leaveResolve?.(true)
}

async function deleteAll() {
  showDeleteConfirm.value = false
  await store.clearAll()
  leaveResolve?.(true)
}

const handleDeleteAll = () => {
  if (isLoading.value) return
  showDeleteConfirm.value = true
}

async function handleRunAlgorithm() {
  algorithmPhase.value = 'idle'
  showAlgorithmModal.value = true
}

function onBeforeUnload(e: BeforeUnloadEvent) {
  if (saveState.value === 'unsaved') e.preventDefault()
}

onMounted(()       => window.addEventListener('beforeunload', onBeforeUnload))
onBeforeUnmount(() => window.removeEventListener('beforeunload', onBeforeUnload))
</script>