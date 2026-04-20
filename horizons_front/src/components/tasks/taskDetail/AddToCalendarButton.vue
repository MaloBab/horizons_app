<template>
  <div class="relative">
    <button
      @click="handleToggle"
      :disabled="isLoading"
      class="inline-flex items-center gap-2 px-3.5 py-2 text-sm font-medium rounded-lg transition-all border shadow-sm group"
      :class="[
        localIsExported 
          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20 hover:bg-red-500/10 hover:text-red-400 hover:border-red-500/20'
          : 'bg-slate-800 text-slate-300 border-white/10 hover:bg-slate-700 hover:text-white',
        isLoading ? 'opacity-50 cursor-wait' : 'cursor-pointer active:scale-95'
      ]"
      :title="localIsExported ? 'Retirer de Google Agenda' : 'Ajouter à Google Agenda'"
    >
      <Loader2 v-if="isLoading" class="w-4 h-4 animate-spin" />
      
      <template v-else>
        <template v-if="localIsExported">
          <Check class="w-4 h-4 block group-hover:hidden" />
          <Trash2 class="w-4 h-4 hidden group-hover:block" />
        </template>
        
        <svg v-else class="w-4 h-4" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
          <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"></path>
          <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"></path>
          <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"></path>
          <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"></path>
          <path fill="none" d="M0 0h48v48H0z"></path>
        </svg>
      </template>

      <span>{{ buttonText }}</span>
    </button>

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
import { ref, computed, watch } from 'vue'
import { Loader2, Trash2, Check } from 'lucide-vue-next' 
import { useTasks } from '../../../composables/useTasks'
import Toast from '../../shared/Toast.vue'
import { useToast } from '../../../composables/useToast'
import { useActivityLogger } from '../../../composables/Activity/useActivityLogger'

const props = defineProps<{ 
  taskId: string,
  isExported: boolean,
  taskTitle: string,
  dueDate?: string
}>()

const emit = defineEmits(['toggled'])

const { exportToCalendar } = useTasks()
const { calendarAdded, calendarRemoved } = useActivityLogger()
const { showToast, toast, hideToast } = useToast()

const isLoading = ref(false)
const localIsExported = ref(props.isExported)

watch(() => props.isExported, (newVal) => {
  localIsExported.value = newVal
})

const buttonText = computed(() => {
  if (isLoading.value) return 'Action en cours...'
  return localIsExported.value ? "Dans l'agenda" : "Ajouter à l'agenda"
})

const handleToggle = async () => {
  if (isLoading.value) return

  if (!localIsExported.value && !props.dueDate) {
    showToast("Aucune date limite définie pour cette tâche.", 'warning')
    return
  }

  isLoading.value = true
  
  try {
    const result = await exportToCalendar(props.taskId)
    
    if (result !== undefined) {
      localIsExported.value = !localIsExported.value
      emit('toggled', localIsExported.value)
      
      showToast(localIsExported.value ? "Tâche ajoutée au calendrier." : "Tâche retirée du calendrier.", 'info')

      if (localIsExported.value) {
        calendarAdded(props.taskTitle) 
      } else {
        calendarRemoved(props.taskTitle)
      }
    }
  } catch (err) {
    showToast("Erreur de synchronisation avec Google.", 'error')
  } finally {
    isLoading.value = false
  }
}
</script>