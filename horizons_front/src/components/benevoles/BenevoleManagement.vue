<template>
  <div class="min-h-screen bg-linear-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
    <main class="container mx-auto px-6 py-8 max-w-7xl">
      <div class="mb-8 flex items-center justify-between">
        <h2 class="text-4xl font-bold mb-2 bg-gray-400 bg-clip-text text-transparent">
          Gestion des Bénévoles
        </h2>

        <!-- Boutons groupés à droite -->
        <div class="flex items-center gap-2">
          <!-- Bouton préférences -->
          <button
            @click="showPreferencesModal = true"
            class="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 border border-slate-600 rounded-lg text-sm text-slate-300 hover:text-white transition-colors"
          >
            <Settings class="w-4 h-4" />
            Préférences & Pôles
          </button>

          <!-- Bouton création manuelle -->
          <button
            @click="showCreateModal = true"
            class="flex items-center gap-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 border border-cyan-500 rounded-lg text-sm text-white font-medium transition-colors"
          >
            <UserPlus class="w-4 h-4" />
            Nouveau bénévole
          </button>
        </div>
      </div>

      <StatsCards :stats="stats" class="mb-8" />

      <ActionBar
        :is-loading="isLoading"
        :has-data="volunteers.length > 0"
        @import="handleImport"
        @export="handleExport"
        @process="handleProcess"
        @delete-all="showDeleteAllConfirm = true"
        class="mb-3 p-1.5! py-1!"
      />

      <BenevolesTable
        :benevoles="volunteersTableData"
        :is-loading="isLoading"
        @view="handleView"
        @delete="handleDelete"
        class="mb-8" />

      <!-- Modal détail -->
      <BenevoleDetailModal
        v-if="selectedVolunteer"
        :volunteer="selectedVolunteer"
        :all-volunteers="volunteers"
        @close="selectedVolunteer = null" />

      <!-- Modal création manuelle -->
      <BenevoleCreateModal
        v-if="showCreateModal"
        @close="showCreateModal = false"
        @created="handleCreated"
      />

      <PreferencesModal
        v-if="showPreferencesModal"
        @close="showPreferencesModal = false" />

      <ConfirmDialog
        v-if="showDeleteAllConfirm"
        title="Supprimer tous les bénévoles"
        message="Êtes-vous sûr de vouloir supprimer tous les bénévoles ? Cette action est irréversible."
        confirm-text="Supprimer tout"
        cancel-text="Annuler"
        type="danger"
        @confirm="handleDeleteAll"
        @cancel="showDeleteAllConfirm = false" />

      <ImportReportModal
        :is-open="showImportReport"
        :report="importReport"
        mode="volunteer"
        @close="showImportReport = false" />

      <Toast
        v-if="toast.show"
        :show="toast.show"
        :message="toast.message"
        :type="toast.type"
        @close="hideToast" />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Settings, UserPlus } from 'lucide-vue-next'
import { useBenevoles } from '../../composables/useBenevoles'
import StatsCards from './StatsCards.vue'
import ActionBar from '../shared/ActionBar.vue'
import BenevolesTable from './BenevolesTable.vue'
import BenevoleDetailModal from './BenevoleDetailModal.vue'
import BenevoleCreateModal from './BenevoleCreateModal.vue'
import PreferencesModal from './preferencesModal/PreferencesModal.vue'
import ConfirmDialog from '../shared/ConfirmDialog.vue'
import ImportReportModal from '../shared/ImportReportModal.vue'
import Toast from '../shared/Toast.vue'
import { useToast } from '../../composables/useToast'
import { useActivityLogger } from '../../composables/Activity/useActivityLogger'
import type { VolunteerImportReport } from '../../types/import.types'
import { useAssignmentStore } from '../../stores/useAssignmentStore'

const { toast, showToast, hideToast } = useToast()
const { volunteerTableImported } = useActivityLogger()
const AssignmentStore = useAssignmentStore()

const {
  volunteers,
  volunteersTableData,
  isLoading,
  selectedVolunteer,
  stats,
  importFromExcel,
  deleteVolunteer,
  deleteAllVolunteers,
  fetchVolunteers,
  selectVolunteer,
  processVolunteers,
} = useBenevoles()

const showDeleteAllConfirm = ref(false)
const showPreferencesModal = ref(false)
const showImportReport     = ref(false)
const showCreateModal      = ref(false)
const importReport         = ref<VolunteerImportReport | null>(null)

onMounted(async () => {
  try {
    await fetchVolunteers()
  } catch (e) {
    showToast((e as Error).message, 'error')
  }
})

const handleImport = async (file: File) => {
  const result = await importFromExcel(file)

  if (!result.success) {
    showToast(result.message, 'error')
    return
  }

  importReport.value     = result.report
  showImportReport.value = true

  showToast(result.message, result.report?.total_errors ? 'warning' : 'success')
  volunteerTableImported(result.report?.total_persisted ?? 0)
}

const handleExport = async () => {
  try {
    showToast('Export réussi', 'success')
  } catch (e) {
    showToast((e as Error).message, 'error')
  }
}

const handleProcess = async () => {
  const result = await processVolunteers()
  showToast(result.message, result.success ? 'success' : 'error')
}

const handleView   = (id: string) => selectVolunteer(id)

const handleDelete = async (id: string) => {
  try {
    await deleteVolunteer(id)
    showToast('Bénévole supprimé avec succès', 'success')
  } catch (e) {
    showToast((e as Error).message, 'error')
  }
}

const handleDeleteAll = async () => {
  try {
    await deleteAllVolunteers()
    await AssignmentStore.clearAll()
    showDeleteAllConfirm.value = false
    showToast('Tous les bénévoles ont été supprimés', 'success')
  } catch (e) {
    showDeleteAllConfirm.value = false
    showToast((e as Error).message, 'error')
  }
}

const handleCreated = async (id: string) => {
  showToast('Bénévole créé avec succès', 'success')
  selectVolunteer(id)
}
</script>

<style scoped>
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}
.container { animation: fadeIn 0.6s ease-out; }
</style>