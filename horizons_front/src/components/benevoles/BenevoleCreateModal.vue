<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
        @click.self="handleClose"
      >
        <div
          class="bg-slate-800 rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden border border-slate-700 flex flex-col"
          @click.stop
        >
          <!-- En-tête -->
          <div class="flex items-center justify-between px-6 py-4 border-b border-slate-700 shrink-0">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-xl bg-linear-to-br from-cyan-500/20 to-blue-500/20 border border-cyan-500/20 flex items-center justify-center">
                <UserPlus class="w-5 h-5 text-cyan-400" />
              </div>
              <div>
                <h2 class="text-lg font-bold text-white">Nouveau bénévole</h2>
                <p class="text-xs text-slate-400">Création manuelle</p>
              </div>
            </div>
            <button
              @click="handleClose"
              class="p-2 rounded-lg hover:bg-slate-700 text-slate-400 hover:text-white transition-colors"
            >
              <X class="w-5 h-5" />
            </button>
          </div>

          <!-- Corps -->
          <div class="flex-1 overflow-y-auto p-6">
            <div class="flex flex-col gap-5">

              <!-- Identité -->
              <section class="bg-slate-700/30 rounded-xl p-4 border border-slate-600/40">
                <h3 class="text-sm font-semibold text-white flex items-center gap-2 mb-4">
                  <User class="w-4 h-4 text-cyan-400" />
                  Identité
                </h3>
                <div class="grid grid-cols-2 gap-3">
                  <div class="flex flex-col gap-1">
                    <label class="text-xs text-slate-400">Prénom <span class="text-red-400">*</span></label>
                    <input
                      v-model="form.first_name"
                      type="text"
                      placeholder="Jean"
                      class="input-field"
                      :class="{ 'input-error': errors.first_name }"
                    />
                    <span v-if="errors.first_name" class="text-xs text-red-400">{{ errors.first_name }}</span>
                  </div>
                  <div class="flex flex-col gap-1">
                    <label class="text-xs text-slate-400">Nom <span class="text-red-400">*</span></label>
                    <input
                      v-model="form.last_name"
                      type="text"
                      placeholder="Dupont"
                      class="input-field"
                      :class="{ 'input-error': errors.last_name }"
                    />
                    <span v-if="errors.last_name" class="text-xs text-red-400">{{ errors.last_name }}</span>
                  </div>
                  <div class="flex flex-col gap-1">
                    <label class="text-xs text-slate-400">Type <span class="text-red-400">*</span></label>
                    <AppSelect
                      v-model="form.volunteer_type"
                      :options="typeOptions"
                    />
                  </div>
                </div>
              </section>

              <!-- Contact -->
              <section class="bg-slate-700/30 rounded-xl p-4 border border-slate-600/40">
                <h3 class="text-sm font-semibold text-white flex items-center gap-2 mb-4">
                  <Mail class="w-4 h-4 text-blue-400" />
                  Contact
                </h3>
                <div class="grid grid-cols-2 gap-3">
                  <div class="flex flex-col gap-1 col-span-2">
                    <label class="text-xs text-slate-400">Email <span class="text-red-400">*</span></label>
                    <input
                      v-model="form.email"
                      type="email"
                      placeholder="jean.dupont@exemple.fr"
                      class="input-field"
                      :class="{ 'input-error': errors.email }"
                    />
                    <span v-if="errors.email" class="text-xs text-red-400">{{ errors.email }}</span>
                  </div>
                  <div class="flex flex-col gap-1">
                    <label class="text-xs text-slate-400">Téléphone <span class="text-red-400">*</span></label>
                    <input
                      v-model="form.phone_number"
                      type="tel"
                      placeholder="06 12 34 56 78"
                      class="input-field"
                      :class="{ 'input-error': errors.phone_number }"
                    />
                    <span v-if="errors.phone_number" class="text-xs text-red-400">{{ errors.phone_number }}</span>
                  </div>
                  <div class="flex flex-col gap-1">
                    <label class="text-xs text-slate-400">Adresse <span class="text-red-400">*</span></label>
                    <input
                      v-model="form.address"
                      type="text"
                      placeholder="12 rue des Lilas, Paris"
                      class="input-field"
                      :class="{ 'input-error': errors.address }"
                    />
                    <span v-if="errors.address" class="text-xs text-red-400">{{ errors.address }}</span>
                  </div>
                </div>
              </section>

              <!-- Préférences -->
              <section class="bg-slate-700/30 rounded-xl p-4 border border-slate-600/40">
                <h3 class="text-sm font-semibold text-white flex items-center gap-2 mb-4">
                  <Star class="w-4 h-4 text-yellow-400" />
                  Préférences
                  <span class="text-slate-400 text-xs font-normal">(optionnel)</span>
                </h3>

                <div v-if="preferencesLoading" class="flex items-center gap-2 text-slate-400 text-sm py-2">
                  <Loader2 class="w-4 h-4 animate-spin" />
                  Chargement…
                </div>

                <div v-else class="flex flex-col gap-2">
                  <!-- Préférences sélectionnées (drag sortable implicite par ordre) -->
                  <div v-if="selectedPrefs.length > 0" class="flex flex-col gap-1.5 mb-2">
                    <div
                      v-for="(pref, i) in selectedPrefs"
                      :key="pref.id"
                      class="flex items-center gap-2 bg-slate-700/60 rounded-lg px-3 py-2 border border-slate-600/50"
                    >
                      <span class="w-5 h-5 rounded-full bg-cyan-500/20 border border-cyan-500/30 text-cyan-400 text-xs flex items-center justify-center font-bold shrink-0">
                        {{ i + 1 }}
                      </span>
                      <span class="flex-1 text-sm text-white">{{ pref.label }}</span>
                      <button
                        @click="removePref(pref.id)"
                        class="p-1 rounded-md hover:bg-red-500/20 text-slate-400 hover:text-red-400 transition-colors"
                      >
                        <X class="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                  <p v-else class="text-slate-500 text-xs py-1">Aucune préférence sélectionnée</p>

                  <!-- Ajout d'une préférence -->
                  <div class="flex gap-2">
                    <select
                      v-model="prefToAdd"
                      class="flex-1 bg-slate-800/60 border border-white/10 rounded-lg px-3 py-2 text-sm text-slate-300 outline-none focus:border-cyan-500/50 transition-colors"
                    >
                      <option value="">Ajouter une préférence…</option>
                      <option
                        v-for="pref in availablePrefs"
                        :key="pref.id"
                        :value="pref.id"
                      >
                        {{ pref.label }}
                      </option>
                    </select>
                    <button
                      @click="addPref"
                      :disabled="!prefToAdd"
                      class="w-9 h-9 flex items-center justify-center rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 hover:bg-cyan-500/20 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                    >
                      <Plus class="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </section>

            </div>
          </div>

          <!-- Pied -->
          <div class="px-6 py-4 border-t border-slate-700 flex items-center justify-end gap-3 shrink-0">
            <button
              @click="handleClose"
              class="px-4 py-2 rounded-lg text-sm text-slate-300 hover:text-white hover:bg-slate-700 transition-colors"
            >
              Annuler
            </button>
            <button
              @click="handleSubmit"
              :disabled="isSaving"
              class="flex items-center gap-2 px-5 py-2 rounded-lg text-sm font-medium bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 disabled:cursor-not-allowed text-white transition-colors"
            >
              <Loader2 v-if="isSaving" class="w-4 h-4 animate-spin" />
              <UserPlus v-else class="w-4 h-4" />
              {{ isSaving ? 'Création…' : 'Créer le bénévole' }}
            </button>
          </div>

        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { UserPlus, X, User, Mail, Star, Plus, Loader2 } from 'lucide-vue-next'
import AppSelect from '../shared/AppSelect.vue'
import { useBenevoles } from '../../composables/useBenevoles'
import { fetchPreferences } from '../../composables/usePreference'
import type { Preference } from '../../types/planning.types'
import type { VolunteerType } from '../../types/benevole.types'

// ── Emits ─────────────────────────────────────────────────────────────────────

const emit = defineEmits<{
  close:   []
  created: [id: string]
}>()

// ── Composable ────────────────────────────────────────────────────────────────

const { createVolunteer } = useBenevoles()

// ── Formulaire ────────────────────────────────────────────────────────────────

interface Form {
  first_name:     string
  last_name:      string
  email:          string
  phone_number:   string
  address:        string
  volunteer_type: VolunteerType
}

const form = ref<Form>({
  first_name:     '',
  last_name:      '',
  email:          '',
  phone_number:   '',
  address:        '',
  volunteer_type: 'Normal',
})

const errors = ref<Partial<Record<keyof Form, string>>>({})

const typeOptions = [
  { label: 'Normal',    value: 'Normal'    },
  { label: 'Spécialisé', value: 'Specialise' },
]

// ── Préférences ───────────────────────────────────────────────────────────────

const allPreferences    = ref<Preference[]>([])
const preferencesLoading = ref(false)
const selectedPrefs     = ref<Preference[]>([])
const prefToAdd         = ref<number | ''>('')

const availablePrefs = computed(() =>
  allPreferences.value.filter(p => !selectedPrefs.value.some(s => s.id === p.id))
)

onMounted(async () => {
  preferencesLoading.value = true
  try {
    allPreferences.value = await fetchPreferences()
  } catch (e) {
    console.error('Impossible de charger les préférences', e)
  } finally {
    preferencesLoading.value = false
  }
})

function addPref() {
  if (!prefToAdd.value) return
  const pref = allPreferences.value.find(p => p.id === prefToAdd.value)
  if (pref) selectedPrefs.value.push(pref)
  prefToAdd.value = ''
}

function removePref(id: number) {
  selectedPrefs.value = selectedPrefs.value.filter(p => p.id !== id)
}

// ── Validation ────────────────────────────────────────────────────────────────

function validate(): boolean {
  const e: typeof errors.value = {}
  if (!form.value.first_name.trim())   e.first_name   = 'Prénom requis'
  if (!form.value.last_name.trim())    e.last_name    = 'Nom requis'
  if (!form.value.email.trim())        e.email        = 'Email requis'
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.value.email))
                                       e.email        = 'Email invalide'
  if (!form.value.phone_number.trim()) e.phone_number = 'Téléphone requis'
  if (!form.value.address.trim())      e.address      = 'Adresse requise'
  errors.value = e
  return Object.keys(e).length === 0
}

// ── Soumission ────────────────────────────────────────────────────────────────

const isSaving = ref(false)

async function handleSubmit() {
  if (!validate()) return
  isSaving.value = true
  try {
    const created = await createVolunteer({
      ...form.value,
      preference_ids: selectedPrefs.value.map(p => p.id),
      slot_ids:       [],
    })
    emit('created', created.id)
    emit('close')
  } catch (e) {
    throw e
  } finally {
    isSaving.value = false
  }
}

function handleClose() {
  if (isSaving.value) return
  emit('close')
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

.input-field {
  width: 100%;
  background-color: rgba(15, 23, 42, 0.6); /* bg-slate-800/60 */
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.5rem; /* rounded-lg */
  padding: 0.5rem 0.75rem; /* py-2 px-3 */
  font-size: 0.875rem; /* text-sm */
  color: #ffffff;
  outline: none;
  transition: border-color 0.2s ease, background-color 0.2s ease, color 0.2s ease;
}

.input-field::placeholder {
  color: rgba(148, 163, 184, 1); /* placeholder:text-slate-500 */
}

.input-error {
  border-color: rgba(239, 68, 68, 0.6);
}

.input-error:focus {
  border-color: rgba(239, 68, 68, 0.8);
}
</style>