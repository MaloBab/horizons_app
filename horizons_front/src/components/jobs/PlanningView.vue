<template>
  <div class="bg-linear-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
    <main class="px-4 py-8 w-full">
      <div class="mb-6">
        <h1 class="text-4xl font-bold mb-2 bg-gray-400 bg-clip-text text-transparent">
          Gestion des Postes
        </h1>
      </div>

      <!-- Erreur de chargement -->
      <div
        v-if="error"
        class="mb-4 px-4 py-3 bg-red-500/20 border border-red-500/30 rounded-xl text-red-300 text-sm flex items-center gap-2"
      >
        <span>⚠️</span> {{ error }}
        <button @click="loadData" class="ml-auto underline hover:no-underline">Réessayer</button>
      </div>

      <ActionBar
        :is-loading="isLoading"
        :has-data="categoryGroups.length > 0"
        import-label="Importer Excel"
        delete-label="Tout supprimer"
        @import="handleImport"
        @delete-all="showDeleteAllConfirm = true"
        class="mb-3 p-1.5! py-1!"
      />

      <PlanningFilters
        :category-groups="categoryGroups"
        :result-count="resultCount"
        class="mb-3"
        @update:filtered="filteredGroups = $event"
        @update:selected-day="selectedDay = $event"
      />

      <!-- Loading wheel -->
      <div v-if="isLoading && categoryGroups.length === 0" class="flex flex-col items-center justify-center h-48 gap-3 text-slate-500">
        <Loader2 class="w-8 h-8 animate-spin text-blue-400" />
        <span class="animate-pulse text-sm">Chargement des postes…</span>
      </div>

      <PlanningGantt
        v-else
        :category-groups="filteredGroups"
        :visible-days="selectedDay !== null ? [selectedDay] : undefined"
      />
    </main>

    <!-- Rapport d'import -->
    <ImportReportModal
      :is-open="showImportReport"
      :report="importReport"
      @close="showImportReport = false"
    />

    <!-- Confirmation suppression -->
    <ConfirmDialog
      v-if="showDeleteAllConfirm"
      title="Supprimer tous les postes"
      message="Êtes-vous sûr de vouloir supprimer tous les postes ? Cette action est irréversible."
      confirm-text="Supprimer tout"
      cancel-text="Annuler"
      type="danger"
      @confirm="handleDeleteAll"
      @cancel="showDeleteAllConfirm = false"
    />

    <Toast
      v-if="toast.show"
      :show="toast.show"
      :message="toast.message"
      :type="toast.type"
      @close="hideToast"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { Loader2 } from 'lucide-vue-next'
import ActionBar from '../shared/ActionBar.vue'
import PlanningGantt from './PlanningGantt.vue'
import PlanningFilters from './PlanningFilters.vue'
import ImportReportModal from '../shared/ImportReportModal.vue'
import ConfirmDialog from '../shared/ConfirmDialog.vue'
import Toast from '../shared/Toast.vue'
import type { CategoryGroup } from '../../types/planning.types'
import type { ImportReport } from '../../types/import.types'
import { fetchCategoryGroups, deleteAllJobs, importJobs, getTotalNormalVolunteers } from '../../composables/useJob'
import { useFestivalStore } from '../../stores/useFestivalStore'
import { useActivityLogger } from '../../composables/Activity/useActivityLogger'
import { useToast } from '../../composables/useToast'
import { useAssignmentStore } from '../../stores/useAssignmentStore'

const festivalStore = useFestivalStore()
const { jobTableImported } = useActivityLogger()
const { toast, showToast, hideToast } = useToast()
const AssignmentStore = useAssignmentStore()

const isLoading            = ref(false)
const error                = ref<string | null>(null)
const categoryGroups       = ref<CategoryGroup[]>([])
const filteredGroups       = ref<CategoryGroup[]>([])
const selectedDay          = ref<number | null>(null)
const showImportReport     = ref(false)
const showDeleteAllConfirm = ref(false)
const importReport         = ref<ImportReport | null>(null)

const resultCount = computed(() =>
  filteredGroups.value.reduce((acc, g) => acc + g.jobs.length, 0)
)

watch(categoryGroups, (val) => {
  filteredGroups.value = val
}, { immediate: true })

watch(
  () => festivalStore.festival,
  (festival) => { if (festival) loadData() },
  { immediate: true }
)

onMounted(() => {
  if (!festivalStore.festival && !festivalStore.isLoading) {
    festivalStore.fetchFestival()
  }
})

async function loadData() {
  isLoading.value = true
  error.value = null
  try {
    categoryGroups.value = await fetchCategoryGroups()
  } catch (e: any) {
    error.value = e.message ?? 'Erreur lors du chargement des postes'
    showToast(error.value!, 'error')
  } finally {
    isLoading.value = false
    console.log('nb de bénévoles normaux :', getTotalNormalVolunteers(categoryGroups.value))
  }
}

const handleImport = async (file: File) => {
  isLoading.value    = true
  error.value        = null
  importReport.value = null

  try {
    const report           = await importJobs(file)
    importReport.value     = report
    showImportReport.value = true

    await loadData()
    jobTableImported(report.total_persisted)
    showToast(`${report.total_persisted} poste(s) importé(s) avec succès`, 'success')
  } catch (e: any) {
    const msg = e.message ?? "Erreur lors de l'import"
    error.value = msg
    showToast(msg, 'error')
    await loadData()
  } finally {
    isLoading.value = false
  }
}

const handleDeleteAll = async () => {
  showDeleteAllConfirm.value = false
  isLoading.value = true
  try {
    await AssignmentStore.clearAll()
    await deleteAllJobs(categoryGroups.value)
    
    categoryGroups.value = []
    showToast('Tous les postes ont été supprimés', 'success')
  } catch (e: any) {
    const msg = e.message ?? 'Erreur lors de la suppression'
    error.value = msg
    showToast(msg, 'error')
  } finally {
    isLoading.value = false
  }
}
</script>