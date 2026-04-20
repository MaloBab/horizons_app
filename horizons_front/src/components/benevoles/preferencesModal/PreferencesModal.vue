<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-opacity duration-200 ease-out"
      leave-active-class="transition-opacity duration-200 ease-in"
      enter-from-class="opacity-0"
      leave-to-class="opacity-0"
    >
      <div
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
        @click.self="$emit('close')"
      >
        <Transition
          enter-active-class="transition-all duration-200 ease-out"
          leave-active-class="transition-all duration-150 ease-in"
          enter-from-class="opacity-0 scale-95 translate-y-2"
          leave-to-class="opacity-0 scale-95 translate-y-2"
        >
          <div
            class="bg-slate-900 backdrop-blur-sm border border-white/10 rounded-2xl shadow-2xl w-full max-w-4xl max-h-[75vh] flex flex-col overflow-hidden"
            @click.stop
          >
            <PreferencesModalHeader
              :preferences="preferences"
              :orphan-count="orphanCategories.length"
              @close="$emit('close')"
            />
            <PreferencesTabs v-model="activeTab" :orphan-count="orphanCategories.length" />
            <div class="flex-1 min-h-0 overflow-y-auto p-5">
              <GroupedTab
                v-if="activeTab === 'grouped'"
                :preferences="preferences"
                :is-loading="isLoading"
                @create-preference="handleCreatePreference"
                @rename-preference="handleRenamePreference"
                @delete-preference="handleDeletePreference"
                @create-category="handleCreateCategory"
                @update-category="handleUpdateCategory"
                @delete-category="handleDeleteCategory"
                @move-category="handleMoveCategory"
              />
              <OrphansTab
                v-else
                :orphan-categories="orphanCategories"
                :preferences="preferences"
                @attach-category="handleAttachCategory"
                @delete-category="handleDeleteCategory"
              />
            </div>
          </div>
        </Transition>
      </div>
    </Transition>

    <Toast
      v-if="toast.show"
      :show="toast.show"
      :message="toast.message"
      :type="toast.type"
      @close="hideToast"
    />
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { Preference, Category } from '../../../types/planning.types'
import Toast from '../../shared/Toast.vue'
import PreferencesModalHeader from './PreferencesModalHeader.vue'
import PreferencesTabs from './PreferencesTabs.vue'
import GroupedTab from './GroupedTab/GroupedTab.vue'
import OrphansTab from './OrphansTab.vue'
import { useToast } from '../../../composables/useToast'
import {
  fetchPreferences, fetchAllCategories,
  createPreference, renamePreference, deletePreference,
  createCategory, updateCategory, deleteCategory, attachCategory,
} from '../../../composables/usePreference'

defineEmits<{ close: [] }>()

const preferences   = ref<Preference[]>([])
const allCategories = ref<Category[]>([])
const isLoading     = ref(false)
const activeTab     = ref<'grouped' | 'orphans'>('grouped')
const { toast, showToast, hideToast } = useToast(5000)

const linkedCategoryIds = computed(() =>
  new Set(preferences.value.flatMap(p => p.categories.map(c => c.id)))
)
const orphanCategories = computed(() =>
  allCategories.value.filter(c => !linkedCategoryIds.value.has(c.id))
)

onMounted(async () => {
  isLoading.value = true
  try {
    ;[preferences.value, allCategories.value] = await Promise.all([
      fetchPreferences(), fetchAllCategories(),
    ])
  } catch (e) { showToast((e as Error).message, 'error') }
  finally { isLoading.value = false }
})

const handleCreatePreference = async (label: string) => {
  try {
    const created = await createPreference(label)
    preferences.value.push({ ...created, categories: [] })
    showToast(`Groupe « ${created.label} » créé`, 'success')
  } catch (e) { showToast((e as Error).message, 'error') }
}
const handleRenamePreference = async (id: number, label: string) => {
  try {
    const updated = await renamePreference(id, label)
    const pref = preferences.value.find(p => p.id === id)
    if (pref) pref.label = updated.label
    showToast('Groupe renommé', 'success')
  } catch (e) { showToast((e as Error).message, 'error') }
}
const handleDeletePreference = async (pref: Preference) => {
  if (pref.categories.length > 0) {
    showToast(`Impossible : « ${pref.label} » contient ${pref.categories.length} pôle(s)`, 'warning')
    return
  }
  try {
    await deletePreference(pref.id)
    preferences.value = preferences.value.filter(p => p.id !== pref.id)
    showToast('Groupe supprimé', 'success')
  } catch (e) { showToast((e as Error).message, 'error') }
}
const handleCreateCategory = async (label: string, preferenceId: number, poleId: number | null) => {
  try {
    const created = await createCategory(label, preferenceId, poleId)
    const pref = preferences.value.find(p => p.id === preferenceId)
    if (pref) pref.categories.push(created)
    allCategories.value.push(created)
    showToast(`Pôle « ${created.label} » ajouté`, 'success')
  } catch (e) { showToast((e as Error).message, 'error') }
}
const handleUpdateCategory = async (originalId: number, label: string, poleId: number | null, preferenceId: number) => {
  try {
    const updated = await updateCategory(originalId, label, poleId)
    const pref = preferences.value.find(p => p.id === preferenceId)
    if (pref) {
      const idx = pref.categories.findIndex(c => c.id === originalId)
      if (idx !== -1) pref.categories[idx] = updated
    }
    const allIdx = allCategories.value.findIndex(c => c.id === originalId)
    if (allIdx !== -1) allCategories.value[allIdx] = updated
    showToast('Pôle mis à jour', 'success')
  } catch (e) { showToast((e as Error).message, 'error') }
}
const handleDeleteCategory = async (cat: Category, preferenceId?: number) => {
  try {
    await deleteCategory(cat.id)
    allCategories.value = allCategories.value.filter(c => c.id !== cat.id)
    if (preferenceId) {
      const pref = preferences.value.find(p => p.id === preferenceId)
      if (pref) pref.categories = pref.categories.filter(c => c.id !== cat.id)
    }
    showToast(`Pôle « ${cat.label} » supprimé`, 'success')
  } catch (e) {
    const msg = (e as Error).message
    showToast(
      msg.includes('409') || msg.includes('foreign') || msg.includes('constraint')
        ? 'Impossible : ce pôle est utilisé dans des postes existants'
        : msg,
      'warning',
    )
  }
}
const handleAttachCategory = async (cat: Category, preferenceId: number) => {
  try {
    const updated = await attachCategory(cat.id, preferenceId)
    const pref = preferences.value.find(p => p.id === preferenceId)
    if (pref) pref.categories.push(updated)
    const allIdx = allCategories.value.findIndex(c => c.id === cat.id)
    if (allIdx !== -1) allCategories.value[allIdx] = updated
    showToast(`Pôle rattaché à « ${pref?.label} »`, 'success')
  } catch (e) { showToast((e as Error).message, 'error') }
}
const handleMoveCategory = async (cat: Category, fromPreferenceId: number, toPreferenceId: number) => {
  try {
    const updated = await attachCategory(cat.id, toPreferenceId)
    const fromPref = preferences.value.find(p => p.id === fromPreferenceId)
    if (fromPref) fromPref.categories = fromPref.categories.filter(c => c.id !== cat.id)
    const toPref = preferences.value.find(p => p.id === toPreferenceId)
    if (toPref) toPref.categories.push(updated)
    const allIdx = allCategories.value.findIndex(c => c.id === cat.id)
    if (allIdx !== -1) allCategories.value[allIdx] = updated
    showToast(`Pôle déplacé vers « ${toPref?.label} »`, 'success')
  } catch (e) { showToast((e as Error).message, 'error') }
}
</script>