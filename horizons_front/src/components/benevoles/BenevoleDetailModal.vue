<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
        @click.self="handleClose"
      >
        <div
          class="bg-slate-800 rounded-2xl shadow-2xl max-w-5xl w-full max-h-[90vh] overflow-hidden border border-slate-700 flex flex-col"
          @click.stop
        >
          <ModalHeader :volunteer="volunteer" @close="handleClose" />

          <div class="flex-1 p-4 overflow-y-auto">
            <div class="grid grid-cols-2 gap-4">

              <!-- Colonne gauche -->
              <div class="flex flex-col gap-4">
                <InfoSection
                  :volunteer="volunteer"
                  :is-editing="editSection === 'info'"
                  :is-saving="isSaving"
                  :model-email="editEmail"
                  :model-phone="editPhone"
                  @toggle-edit="toggleEdit('info')"
                  @update:model-email="editEmail = $event"
                  @update:model-phone="editPhone = $event"
                  @save="saveInfo"
                  @cancel="cancelEdit"
                />

                <PreferencesSection
                  :volunteer="volunteer"
                  :is-editing="editSection === 'prefs'"
                  :is-saving="isSaving"
                  :edit-prefs="editPrefs"
                  :drag-over-index="dragOverIndex"
                  @toggle-edit="toggleEdit('prefs')"
                  @drag-start="dragStart"
                  @drag-over="dragOver"
                  @drag-end="dragEnd"
                  @save="savePrefs"
                  @cancel="cancelEdit"
                />

                <AffinitesSection
                  :volunteer="volunteer"
                  :is-editing="editSection === 'mates'"
                  :loading-mate-id="mateLoadingId"
                  :search-query="mateSearch"
                  :show-dropdown="showMateDropdown"
                  :candidates="filteredMateCandidates"
                  @toggle-edit="toggleEdit('mates')"
                  @remove-mate="removeMateLocal"
                  @add-mate="addMateLocal"
                  @update:search-query="mateSearch = $event"
                  @search-focus="showMateDropdown = true"
                  @search-blur="onSearchBlur"
                />
              </div>

              <!-- Colonne droite -->
              <div>
                <DisponibilitesSection
                  :volunteer="volunteer"
                  :is-editing="editSection === 'slots'"
                  :loading-slot-key="slotLoadingKey"
                  :consumed-slot-keys="assignmentStore.consumedSlotKeys"
                  @toggle-edit="toggleEdit('slots')"
                  @toggle-slot="toggleSlot"
                />
              </div>

            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { Volunteer, VolunteerPreference } from '../../types/benevole.types'
import { useBenevoles } from '../../composables/useBenevoles'

import ModalHeader           from './DetailModal/ModalHeader.vue'
import InfoSection           from './DetailModal/InfoSection.vue'
import PreferencesSection    from './DetailModal/PreferencesSection.vue'
import AffinitesSection      from './DetailModal/AffinitesSection.vue'
import DisponibilitesSection from './DetailModal/DisponibilitesSection.vue'
import { useAssignmentStore } from '../../stores/useAssignmentStore'

// ── Props & emits ─────────────────────────────────────────────────────────────
interface Props {
  volunteer:     Volunteer
  allVolunteers: Volunteer[]
}
const props = defineProps<Props>()
const emit  = defineEmits<{ close: [] }>()

// ── Composable ────────────────────────────────────────────────────────────────
const assignmentStore = useAssignmentStore()

const {
  updateEmail, updatePhone, addAvailability, removeSlot,
  addMate, removeMate, reorderPreferences,
} = useBenevoles()

// ── Section active ────────────────────────────────────────────────────────────
type Section = 'info' | 'prefs' | 'slots' | 'mates' | null
const editSection = ref<Section>(null)
const isSaving    = ref(false)

function toggleEdit(section: Section) {
  if (editSection.value === section) { cancelEdit(); return }
  editSection.value = section
  if (section === 'info') {
    editEmail.value = props.volunteer.email
    editPhone.value = props.volunteer.phone_number
  }
  if (section === 'prefs') initPrefs()
  if (section === 'mates') { mateSearch.value = ''; showMateDropdown.value = false }
}
function cancelEdit() { editSection.value = null }
function handleClose() { cancelEdit(); emit('close') }

// ── Infos perso ───────────────────────────────────────────────────────────────
const editEmail = ref('')
const editPhone = ref('')

async function saveInfo() {
  isSaving.value = true
  try {
    if (editEmail.value !== props.volunteer.email)
      await updateEmail(props.volunteer.id, editEmail.value)
    if (editPhone.value !== props.volunteer.phone_number)
      await updatePhone(props.volunteer.id, editPhone.value)
    editSection.value = null
  } catch (e) { console.error(e) }
  finally { isSaving.value = false }
}

// ── Préférences drag & drop ───────────────────────────────────────────────────
const editPrefs     = ref<VolunteerPreference[]>([])
const dragIndex     = ref<number | null>(null)
const dragOverIndex = ref<number | null>(null)

watch(() => props.volunteer, () => {
  if (editSection.value === 'prefs') initPrefs()
}, { deep: true })

function initPrefs() {
  editPrefs.value = [...props.volunteer.preferences]
    .sort((a, b) => a.rank - b.rank)
    .map(p => ({ rank: p.rank, preference: { ...p.preference } }))
}

function dragStart(index: number) { dragIndex.value = index }
function dragOver(index: number) {
  if (dragIndex.value === null || dragIndex.value === index) return
  dragOverIndex.value = index
  const items = [...editPrefs.value]
  const moved = items.splice(dragIndex.value, 1)[0]
  if (!moved) return
  items.splice(index, 0, moved)
  editPrefs.value = items
  dragIndex.value = index
}
function dragEnd() { dragOverIndex.value = null; dragIndex.value = null }

async function savePrefs() {
  isSaving.value = true
  try {
    const orderedIds = editPrefs.value.map(p => p.preference.id)
    await reorderPreferences(props.volunteer.id, orderedIds)
    editSection.value = null
  } catch (e) { console.error(e) }
  finally { isSaving.value = false }
}

// ── Slots ─────────────────────────────────────────────────────────────────────
const slotLoadingKey = ref<string | null>(null)

async function toggleSlot(dayIndex: number, hour: number) {
  const key = `${dayIndex}-${hour}`
  if (slotLoadingKey.value === key) return
  slotLoadingKey.value = key
  try {
    const existing = props.volunteer.slots.find(
      vs => vs.slot.day_index === dayIndex
         && vs.slot.start_time === hour
         && vs.slot.end_time   === hour + 1
    )
    if (existing) {
      await removeSlot(props.volunteer.id, existing.slot_id)
    } else {
      await addAvailability(props.volunteer.id, dayIndex, hour, hour + 1)
    }
  } catch (e) { console.error(e) }
  finally { slotLoadingKey.value = null }
}

// ── Affinités ─────────────────────────────────────────────────────────────────
const mateSearch       = ref('')
const showMateDropdown = ref(false)
const mateLoadingId    = ref<string | null>(null)
// Empêche le blur de fermer le dropdown quand on vient de cliquer un candidat
const addingMate       = ref(false)

const existingMateIds = computed(() => new Set(props.volunteer.mates.map(m => m.id)))

const filteredMateCandidates = computed(() => {
  const query = mateSearch.value.toLowerCase().trim()
  return props.allVolunteers.filter(v => {
    if (v.id === props.volunteer.id) return false
    if (existingMateIds.value.has(v.id)) return false
    if (!query) return true
    return `${v.first_name} ${v.last_name} ${v.email}`.toLowerCase().includes(query)
  })
})

function onSearchBlur() {
  // Si on est en train d'ajouter un mate (clic sur candidat), on ignore ce blur
  if (addingMate.value) return
  setTimeout(() => { showMateDropdown.value = false }, 150)
}

async function addMateLocal(candidate: Volunteer) {
  addingMate.value    = true
  mateLoadingId.value = candidate.id
  try {
    await addMate(props.volunteer.id, candidate.id)
    // Dropdown reste ouvert, la liste se met à jour automatiquement
    // via filteredMateCandidates (le candidat ajouté disparaît des suggestions)
    showMateDropdown.value = true
  } catch (e) {
    console.error(e)
  } finally {
    mateLoadingId.value = null
    addingMate.value    = false
  }
}

async function removeMateLocal(mateId: string) {
  mateLoadingId.value = mateId
  try {
    await removeMate(props.volunteer.id, mateId)
  } catch (e) { console.error(e) }
  finally { mateLoadingId.value = null }
}
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active { transition: opacity 0.25s ease; }
.modal-enter-active > div,
.modal-leave-active > div { transition: transform 0.25s ease; }
.modal-enter-from,
.modal-leave-to { opacity: 0; }
.modal-enter-from > div,
.modal-leave-to > div { transform: scale(0.96); }
</style>