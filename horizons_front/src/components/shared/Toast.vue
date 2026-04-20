<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-all duration-300 ease-[cubic-bezier(0.34,1.56,0.64,1)]"
      leave-active-class="transition-all duration-200 ease-in"
      enter-from-class="opacity-0 translate-x-6 scale-95"
      leave-to-class="opacity-0 translate-x-4 scale-95"
    >
      <div
        v-if="show"
        class="fixed top-4 right-4 z-50 overflow-hidden rounded-xl border shadow-2xl"
        :class="wrapClass"
        style="width: 340px; min-height: 80px"
        role="alert"
      >
        <!-- Arrière-plan animé -->
        <ToastBgSuccess v-if="type === 'success'" />
        <ToastBgError   v-else-if="type === 'error'" />
        <ToastBgWarning v-else-if="type === 'warning'" />
        <ToastBgInfo    v-else />

        <!-- Voile dégradé gauche pour lisibilité du texte -->
        <div
          class="absolute inset-0 pointer-events-none"
          :class="veilClass"
        />

        <!-- Contenu : centré verticalement, aligné à gauche -->
        <div class="absolute inset-0 flex items-center">
          <div class="flex items-center gap-2.5 px-4 pr-10">
            <component
              :is="iconComponent"
              class="w-5 h-5 shrink-0"
              :class="iconClass"
            />
            <p class="text-sm font-semibold leading-snug" :class="textClass">
              {{ message }}
            </p>
          </div>
        </div>

        <!-- Bouton fermer en coin haut droit -->
        <button
          class="absolute top-2.5 right-2.5 opacity-40 hover:opacity-90 transition-opacity"
          :class="textClass"
          @click="$emit('close')"
        >
          <X class="w-3.5 h-3.5" />
        </button>

        <!-- Barre de progression auto-dismiss (5s) -->
        <div
          class="absolute bottom-0 left-0 h-px w-full origin-left opacity-60"
          :class="barClass"
          style="animation: progress-shrink 5s linear forwards"
        />
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { CheckCircle, XCircle, AlertTriangle, Info, X } from 'lucide-vue-next'
import ToastBgSuccess from '../style/ToastBgSuccess.vue'
import ToastBgError   from '../style/ToastBgError.vue'
import ToastBgWarning from '../style/ToastBgWarning.vue'
import ToastBgInfo    from '../style/ToastBgInfo.vue'

const props = withDefaults(defineProps<{
  show:    boolean
  message: string
  type?:   'success' | 'error' | 'warning' | 'info'
}>(), { type: 'success' })

defineEmits<{ close: [] }>()

const iconComponent = computed(() => ({
  success: CheckCircle,
  error:   XCircle,
  warning: AlertTriangle,
  info:    Info,
}[props.type]))

// Voile dégradé horizontal : sombre à gauche (texte), transparent à droite (laisse voir le bg)
const veilClass = computed(() => ({
  success: 'bg-gradient-to-r from-emerald-950/80 via-emerald-950/40 to-transparent',
  error:   'bg-gradient-to-r from-slate-950/80   via-slate-950/40   to-transparent',
  warning: 'bg-gradient-to-r from-amber-950/80   via-amber-950/35   to-transparent',
  info:    'bg-gradient-to-r from-slate-950/80   via-slate-950/40   to-transparent',
}[props.type]))

const wrapClass = computed(() => ({
  success: 'bg-emerald-950/70 border-emerald-500/25 backdrop-blur-sm',
  error:   'bg-slate-950/75   border-rose-500/20    backdrop-blur-sm',
  warning: 'bg-amber-950/70   border-amber-500/20   backdrop-blur-sm',
  info:    'bg-slate-950/75   border-sky-500/25     backdrop-blur-sm',
}[props.type]))

const iconClass = computed(() => ({
  success: 'text-emerald-400',
  error:   'text-rose-400',
  warning: 'text-amber-400',
  info:    'text-sky-400',
}[props.type]))

const textClass = computed(() => ({
  success: 'text-emerald-100',
  error:   'text-rose-100',
  warning: 'text-amber-100',
  info:    'text-sky-100',
}[props.type]))

const barClass = computed(() => ({
  success: 'bg-emerald-400',
  error:   'bg-rose-400',
  warning: 'bg-amber-400',
  info:    'bg-sky-400',
}[props.type]))
</script>