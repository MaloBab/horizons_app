<template>
  <div class="relative overflow-hidden rounded-xl border border-white/7 bg-slate-950/85 backdrop-blur-lg">
    <MusicBackground />

    <div class="relative z-10 flex flex-wrap items-center justify-between gap-3 px-4 py-4 pr-16">

      <!-- ── ZONE IMPORT ── -->
      <div v-if="showImport" class="flex flex-wrap items-center gap-2.5">

        <!-- Dropzone -->
        <div
          class="relative flex h-10 min-w-52 cursor-pointer items-center overflow-hidden rounded-lg border border-dashed border-cyan-400/40 bg-cyan-400/4 px-3.5 transition-all duration-200 hover:border-cyan-400/50 hover:bg-cyan-400/8 hover:shadow-[0_0_16px_rgba(34,211,238,0.1)]"
          :class="{
            'border-solid border-cyan-500! bg-cyan-500/20! shadow-[0_0_24px_rgba(34,211,238,0.22)] scale-[1.01]': isDragging,
            'border-solid border-purple-600/45! bg-purple-600/7! shadow-[0_0_14px_rgba(168,85,247,0.12)]': selectedFile,
            'pointer-events-none opacity-40': isLoading,
          }"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="handleDrop"
          @click="!isLoading && triggerInput()"
        >
          <input id="import-input" ref="fileInputRef" type="file" :accept="importAccept"
            class="hidden" @change="handleFileChange" :disabled="isLoading" />

          <Transition name="swap" mode="out-in">
            <div v-if="selectedFile" key="file" class="flex w-full items-center gap-2">
              <div class="flex h-6 w-6 shrink-0 items-center justify-center rounded-md border border-purple-500/35 bg-linear-to-br from-purple-500/30 to-pink-500/25 text-purple-300">
                <FileSpreadsheet class="h-3.5 w-3.5" />
              </div>
              <span class="max-w-40 flex-1 truncate text-xs text-slate-200/90">{{ selectedFile.name }}</span>
              <button
                class="flex h-5 w-5 shrink-0 items-center justify-center rounded text-slate-400/50 transition-all hover:bg-red-500/30 hover:text-red-400"
                @click.stop="clearFile"
              >
                <X class="h-3 w-3" />
              </button>
            </div>

            <div v-else-if="isDragging" key="drag" class="flex items-center gap-2 text-sm font-semibold text-cyan-400">
              <ArrowDownToLine class="h-4 w-4" />
              <span>Déposer ici</span>
            </div>

            <div v-else key="idle" class="flex items-center gap-2 text-slate-400/75">
              <Upload class="h-4 w-4 shrink-0" />
              <span class="text-sm">{{ importLabel }}</span>
              <span class="text-[10px] uppercase tracking-widest text-slate-500/50">.ods</span>
            </div>
          </Transition>
        </div>

        <slot name="left" />
      </div>

      <!-- ── ZONE ACTIONS ── -->
      <div class="flex flex-wrap items-center gap-2">
        <slot name="actions" />
        <button
          v-if="showDeleteAll"
          @click="$emit('delete-all')"
          :disabled="!hasData || isLoading"
          class="flex h-10 items-center gap-2 rounded-lg border border-red-500/30 bg-red-500/5 px-4 text-sm font-medium text-red-300/65 whitespace-nowrap transition-all duration-200 hover:border-red-500/55 hover:bg-linear-to-br hover:from-red-500/15 hover:to-pink-500/10 hover:text-red-300 hover:shadow-[0_0_14px_rgba(239,68,68,0.18)] hover:scale-[1.02] disabled:cursor-not-allowed disabled:opacity-20"
        >
          <Trash2 class="h-4 w-4" />
          <span>{{ deleteLabel }}</span>
        </button>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Upload, Trash2, X, FileSpreadsheet, ArrowDownToLine } from 'lucide-vue-next'
import MusicBackground from '../style/MusicBackground.vue'

interface Props {
  isLoading?:    boolean
  hasData?:      boolean
  showImport?:   boolean
  showDeleteAll?: boolean
  importLabel?:  string
  exportLabel?:  string
  deleteLabel?:  string
  importAccept?: string
}

withDefaults(defineProps<Props>(), {
  isLoading:    false,
  hasData:      false,
  showImport:   true,
  showDeleteAll: true,
  importLabel:  'Importer',
  exportLabel:  'Exporter',
  deleteLabel:  'Tout supprimer',
  importAccept: '.ods',
})

const emit = defineEmits<{
  import:       [file: File]
  'delete-all': []
}>()

const selectedFile = ref<File | null>(null)
const isDragging   = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)

const triggerInput = () => fileInputRef.value?.click()

const clearFile = () => {
  selectedFile.value = null
  if (fileInputRef.value) fileInputRef.value.value = ''
}

const handleFileChange = (e: Event) => {
  const f = (e.target as HTMLInputElement).files?.[0]
  if (f) { selectedFile.value = f; emit('import', f) }
}

const handleDrop = (e: DragEvent) => {
  isDragging.value = false
  const f = e.dataTransfer?.files?.[0]
  if (f) { selectedFile.value = f; emit('import', f) }
}
</script>

<style scoped>
.swap-enter-active, .swap-leave-active { transition: opacity .15s ease, transform .15s ease; }
.swap-enter-from { opacity: 0; transform: translateY(4px); }
.swap-leave-to   { opacity: 0; transform: translateY(-4px); }

.slide-in-enter-active { transition: opacity .2s ease, transform .25s cubic-bezier(0.34,1.56,0.64,1); }
.slide-in-leave-active { transition: opacity .15s ease, transform .15s ease; }
.slide-in-enter-from   { opacity: 0; transform: translateX(-8px) scale(.93); }
.slide-in-leave-to     { opacity: 0; transform: translateX(8px) scale(.95); }
</style>