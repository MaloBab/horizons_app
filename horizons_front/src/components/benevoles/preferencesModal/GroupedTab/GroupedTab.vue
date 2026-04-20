<template>
  <div class="flex gap-4 h-full min-h-96">
    <GroupList
      :preferences="preferences"
      :is-loading="isLoading"
      :selected-id="selectedPreference?.id ?? null"
      @select="selectedPreference = $event"
      @create="$emit('create-preference', $event)"
      @rename="$emit('rename-preference', $event.id, $event.label)"
      @delete="$emit('delete-preference', $event)"
    />

    <div class="w-px bg-white/5 self-stretch shrink-0" />

    <CategoryList
      :preference="selectedPreference"
      :other-preferences="otherPreferences"
      @create="onCreateCategory"
      @update="onUpdateCategory"
      @delete="onDeleteCategory"
      @move="onMoveCategory"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Preference, Category } from '../../../../types/planning.types'
import GroupList from './GroupList.vue'
import CategoryList from './CategoryList.vue'

const props = defineProps<{ preferences: Preference[]; isLoading: boolean }>()

const emit = defineEmits<{
  'create-preference': [label: string]
  'rename-preference': [id: number, label: string]
  'delete-preference': [pref: Preference]
  'create-category':   [label: string, preferenceId: number, poleId: number | null]
  'update-category':   [id: number, label: string, poleId: number | null, preferenceId: number]
  'delete-category':   [cat: Category, preferenceId: number]
  'move-category':     [cat: Category, fromId: number, toId: number]
}>()

const selectedPreference = ref<Preference | null>(null)
const otherPreferences   = computed(() => props.preferences.filter(p => p.id !== selectedPreference.value?.id))

const onCreateCategory = (label: string, poleId: number | null) => {
  if (!selectedPreference.value) return
  emit('create-category', label, selectedPreference.value.id, poleId)
}
const onUpdateCategory = (id: number, label: string, poleId: number | null) => {
  if (!selectedPreference.value) return
  emit('update-category', id, label, poleId, selectedPreference.value.id)
}
const onDeleteCategory = (cat: Category) => {
  if (!selectedPreference.value) return
  emit('delete-category', cat, selectedPreference.value.id)
}
const onMoveCategory = (cat: Category, toPreferenceId: number) => {
  if (!selectedPreference.value) return
  emit('move-category', cat, selectedPreference.value.id, toPreferenceId)
}
</script>