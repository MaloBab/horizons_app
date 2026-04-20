<template>
  <Teleport to="body">
    <Transition name="modal">
      <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm" @click.self="$emit('cancel')">
        <div class="bg-slate-800 rounded-xl shadow-2xl max-w-md w-full border border-slate-700" @click.stop>
          <div class="p-6">
            <div class="flex items-center gap-4 mb-4">
              <div class="w-12 h-12 rounded-full flex items-center justify-center" :class="iconBgClass">
                <component :is="iconComponent" :class="iconColorClass" class="w-6 h-6" />
              </div>
              <h3 class="text-xl font-bold text-white">{{ title }}</h3>
            </div>
            <p class="text-slate-300">{{ message }}</p>
          </div>

          <div class="border-t border-slate-700 px-6 py-4 flex gap-3 justify-end">
            <button @click="$emit('cancel')"
              class="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition-colors">
              {{ cancelText }}
            </button>
            <button @click="$emit('confirm')"
              class="px-4 py-2 rounded-lg font-medium transition-colors" :class="confirmButtonClass">
              {{ confirmText }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { AlertTriangle, Info, CheckCircle, XCircle } from 'lucide-vue-next'

interface Props {
  title: string
  message: string
  confirmText?: string
  cancelText?: string
  type?: 'danger' | 'warning' | 'info' | 'success'
}

const props = withDefaults(defineProps<Props>(), {
  confirmText: 'Confirmer',
  cancelText: 'Annuler',
  type: 'warning'
})

defineEmits<{
  confirm: []
  cancel: []
}>()

const iconComponent = computed(() => {
  const icons = {
    danger: XCircle,
    warning: AlertTriangle,
    info: Info,
    success: CheckCircle
  }
  return icons[props.type]
})

const iconBgClass = computed(() => {
  const classes = {
    danger: 'bg-red-500/20',
    warning: 'bg-yellow-500/20',
    info: 'bg-blue-500/20',
    success: 'bg-green-500/20'
  }
  return classes[props.type]
})

const iconColorClass = computed(() => {
  const classes = {
    danger: 'text-red-400',
    warning: 'text-yellow-400',
    info: 'text-blue-400',
    success: 'text-green-400'
  }
  return classes[props.type]
})

const confirmButtonClass = computed(() => {
  const classes = {
    danger: 'bg-red-600 hover:bg-red-700 text-white',
    warning: 'bg-yellow-600 hover:bg-yellow-700 text-white',
    info: 'bg-blue-600 hover:bg-blue-700 text-white',
    success: 'bg-green-600 hover:bg-green-700 text-white'
  }
  return classes[props.type]
})
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-active > div,
.modal-leave-active > div {
  transition: transform 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from > div,
.modal-leave-to > div {
  transform: scale(0.95);
}
</style>