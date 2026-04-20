<template>
  <div class="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 overflow-hidden">
    <div class="p-6 border-b border-slate-700/50">
      <div class="flex flex-col gap-4">

        <!-- Ligne titre + recherche -->
        <div class="flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between flex-wrap">
          <h2 class="text-2xl font-bold shrink-0">Liste des Bénévoles</h2>

          <div class="relative w-full sm:w-auto sm:min-w-64">
            <Search class="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
            <input
              id="search-volunteer"
              v-model="searchQuery"
              type="text"
              placeholder="Rechercher un bénévole..."
              class="w-full pl-9 pr-4 py-1.5 bg-slate-700/50 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            />
          </div>
        </div>

        <!-- Filtre disponibilité — pleine largeur sous la recherche -->
        <div class="w-full pt-1 border-t border-slate-700/40">
          <AvailabilityFilter
            :volunteers="props.benevoles"
            :filtered-volunteers-lenght="filteredVolunteers.length"
            @filter="onAvailabilityFilter"
          />
        </div>

      </div>
    </div>

    <div class="overflow-x-auto">
      <table class="w-full">
        <thead class="bg-slate-700/30">
          <tr>
            <th
              v-for="column in columns"
              :key="column.key"
              class="px-6 py-4 text-left text-xs font-medium text-slate-300 uppercase tracking-wider transition-colors"
              :class="column.sortable ? 'cursor-pointer hover:bg-slate-700/50' : 'cursor-default'"
              @click="handleSort(column.key)"
            >
              <div class="flex items-center gap-2">
                <span>{{ column.label }}</span>
                <ArrowUpDown
                  v-if="column.sortable"
                  class="w-4 h-4"
                  :class="sortColumn === column.key ? 'text-blue-400' : 'text-slate-500'"
                />
              </div>
            </th>
          </tr>
        </thead>

        <tbody class="divide-y divide-slate-700/50">

          <!-- Chargement -->
          <tr v-if="isLoading" class="bg-slate-800/30">
            <td :colspan="columns.length" class="px-6 py-12 text-center">
              <Loader2 class="w-8 h-8 animate-spin mx-auto text-blue-400" />
              <p class="mt-2 text-slate-400">Chargement...</p>
            </td>
          </tr>

          <!-- Vide -->
          <tr v-else-if="filteredVolunteers.length === 0" class="bg-slate-800/30">
            <td :colspan="columns.length" class="px-6 py-12 text-center text-slate-400">
              <Users class="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p>{{ searchQuery || availabilityIds !== null ? 'Aucun bénévole trouvé' : 'Aucun bénévole enregistré' }}</p>
            </td>
          </tr>

          <!-- Lignes -->
          <tr
            v-else
            v-for="volunteer in paginatedVolunteers"
            :key="volunteer.id"
            class="bg-slate-800/30 hover:bg-slate-700/50 transition-colors"
          >
            <!-- Nom -->
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-linear-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold shrink-0">
                  {{ volunteer.first_name[0] }}{{ volunteer.last_name[0] }}
                </div>
                <span class="text-sm font-medium text-white">{{ volunteer.fullName }}</span>
              </div>
            </td>

            <!-- Type -->
            <td class="px-6 py-4 whitespace-nowrap">
              <span
                class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border"
                :class="volunteer.volunteer_type === 'Specialise'
                  ? 'bg-amber-500/20 text-amber-400 border-amber-500/30'
                  : 'bg-slate-500/20 text-slate-400 border-slate-500/30'"
              >
                {{ volunteer.volunteer_type === 'Specialise' ? 'Spécialisé' : 'Normal' }}
              </span>
            </td>

            <!-- Email -->
            <td class="px-6 py-4 whitespace-nowrap">
              <span class="text-sm text-slate-300">{{ volunteer.email }}</span>
            </td>

            <!-- Téléphone -->
            <td class="px-6 py-4 whitespace-nowrap">
              <span class="text-sm text-white">{{ volunteer.phone_number }}</span>
            </td>

            <!-- Préférence #1 -->
            <td class="px-6 py-4 whitespace-nowrap text-center">
              <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-purple-500/20 text-purple-400">
                {{ topPreferenceLabel(volunteer) }}
              </span>
            </td>

            <!-- Actions -->
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <div class="flex items-center justify-end gap-2">
                <button
                  class="p-2 text-blue-400 hover:bg-blue-500/20 rounded-lg transition-colors"
                  title="Voir les détails"
                  @click="$emit('view', volunteer.id)"
                >
                  <Eye class="w-4 h-4" />
                </button>
                <button
                  class="p-2 text-red-400 hover:bg-red-500/20 rounded-lg transition-colors"
                  title="Supprimer"
                  @click="$emit('delete', volunteer.id)"
                >
                  <Trash2 class="w-4 h-4" />
                </button>
              </div>
            </td>
          </tr>

        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div
      v-if="!isLoading && filteredVolunteers.length > 0"
      class="px-6 py-4 border-t border-slate-700/50 flex items-center justify-between"
    >
      <span class="text-sm text-slate-400">
        Affichage de {{ startIndex + 1 }} à {{ Math.min(endIndex, filteredVolunteers.length) }}
        sur {{ filteredVolunteers.length }} bénévoles
      </span>
      <div class="flex items-center gap-2">
        <button
          class="px-3 py-2 bg-slate-700 hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-colors"
          :disabled="currentPage === 1"
          @click="previousPage"
        >
          <ChevronLeft class="w-4 h-4" />
        </button>
        <button
          v-for="page in visiblePages"
          :key="page"
          class="px-3 py-2 rounded-lg transition-colors"
          :class="currentPage === page
            ? 'bg-blue-600 text-white'
            : 'bg-slate-700 hover:bg-slate-600 text-slate-300'"
          @click="currentPage = page"
        >
          {{ page }}
        </button>
        <button
          class="px-3 py-2 bg-slate-700 hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-colors"
          :disabled="currentPage === totalPages"
          @click="nextPage"
        >
          <ChevronRight class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { VolunteerTableRow } from '../../types/benevole.types'
import { Search, ArrowUpDown, Eye, Trash2, ChevronLeft, ChevronRight, Loader2, Users } from 'lucide-vue-next'
import AvailabilityFilter from './AvailabilityFilter.vue'

const props = defineProps<{ benevoles: VolunteerTableRow[]; isLoading: boolean }>()
defineEmits<{ view: [id: string]; delete: [id: string] }>()

const searchQuery    = ref('')
const sortColumn     = ref('fullName')
const sortDirection  = ref<'asc' | 'desc'>('asc')
const currentPage    = ref(1)
const itemsPerPage   = 10
const availabilityIds = ref<string[] | null>(null)

const columns = [
  { key: 'fullName',       label: 'Nom',      sortable: true  },
  { key: 'volunteer_type', label: 'Type',      sortable: true  },
  { key: 'email',          label: 'Email',     sortable: false },
  { key: 'phone_number',   label: 'Téléphone', sortable: false },
  { key: 'preferences',    label: 'Préf. #1',  sortable: true  },
  { key: 'actions',        label: 'Actions',   sortable: false },
]

const topPreferenceLabel = (v: VolunteerTableRow): string => {
  if (!v.preferences.length) return 'Aucune'
  const top = [...v.preferences].sort((a, b) => a.rank - b.rank)[0]
  return top?.preference.label ?? 'Aucune'
}

function onAvailabilityFilter(ids: Set<string> | null) {
  availabilityIds.value = ids ? [...ids] : null
  currentPage.value = 1
}

const handleSort = (key: string) => {
  const col = columns.find(c => c.key === key)
  if (!col?.sortable) return
  if (sortColumn.value === key) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortColumn.value    = key
    sortDirection.value = 'asc'
  }
}

const filteredVolunteers = computed(() => {
  let result = [...props.benevoles]

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(v =>
      v.fullName.toLowerCase().includes(q) ||
      v.email.toLowerCase().includes(q) ||
      v.phone_number.includes(q) ||
      v.preferences[0]?.preference.label.toLowerCase().includes(q),
    )
  }

  if (availabilityIds.value !== null) {
    result = result.filter(v => availabilityIds.value!.includes(v.id))
  }

  result.sort((a, b) => {
    let av: unknown
    let bv: unknown
    if (sortColumn.value === 'preferences') {
      av = topPreferenceLabel(a)
      bv = topPreferenceLabel(b)
    } else {
      av = a[sortColumn.value as keyof VolunteerTableRow]
      bv = b[sortColumn.value as keyof VolunteerTableRow]
    }

    let cmp = 0
    if (typeof av === 'number' && typeof bv === 'number') cmp = av - bv
    else if (Array.isArray(av) && Array.isArray(bv))      cmp = av.length - bv.length
    else                                                   cmp = String(av).localeCompare(String(bv))
    return sortDirection.value === 'asc' ? cmp : -cmp
  })

  return result
})

const totalPages = computed(() => Math.ceil(filteredVolunteers.value.length / itemsPerPage))
const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage)
const endIndex   = computed(() => startIndex.value + itemsPerPage)

const paginatedVolunteers = computed(() =>
  filteredVolunteers.value.slice(startIndex.value, endIndex.value),
)

const visiblePages = computed(() => {
  const max = 5
  let start = Math.max(1, currentPage.value - Math.floor(max / 2))
  let end   = Math.min(totalPages.value, start + max - 1)
  if (end - start < max - 1) start = Math.max(1, end - max + 1)
  return Array.from({ length: end - start + 1 }, (_, i) => start + i)
})

const previousPage = () => { if (currentPage.value > 1) currentPage.value-- }
const nextPage     = () => { if (currentPage.value < totalPages.value) currentPage.value++ }
</script>