<template>
  <div class="flex flex-col items-center gap-4">
    <!-- Avatar + overlay upload -->
    <div
      class="relative group cursor-pointer"
      @click="triggerFileInput"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleDrop"
    >
      <!-- Avatar -->
      <div
        class="w-24 h-24 rounded-2xl overflow-hidden border-2 transition-all duration-200 shadow-lg"
        :class="isDragging
          ? 'border-cyan-400 shadow-cyan-500/30'
          : 'border-white/10 group-hover:border-cyan-400/60 group-hover:shadow-cyan-500/20'"
      >
        <img
          v-if="previewUrl || currentUrl"
          :src="previewUrl || currentUrl || ''"
          alt="Avatar"
          class="w-full h-full object-cover transition-opacity duration-200"
          :class="isUploading ? 'opacity-50' : 'opacity-100'"
        />
        <div
          v-else
          class="w-full h-full bg-linear-to-br from-cyan-500/20 to-blue-600/20 flex items-center justify-center"
        >
          <span class="text-3xl font-bold text-white/60">{{ initial }}</span>
        </div>
      </div>

      <!-- Hover overlay -->
      <div
        class="absolute inset-0 rounded-2xl bg-black/60 flex flex-col items-center justify-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200"
        :class="{ 'opacity-100': isDragging || isUploading }"
      >
        <!-- Progress ring pendant l'upload -->
        <template v-if="isUploading">
          <svg class="w-8 h-8 -rotate-90" viewBox="0 0 36 36">
            <circle cx="18" cy="18" r="14" fill="none" stroke="rgba(255,255,255,0.15)" stroke-width="3"/>
            <circle
              cx="18" cy="18" r="14" fill="none"
              stroke="#22d3ee" stroke-width="3"
              stroke-linecap="round"
              :stroke-dasharray="`${(progress / 100) * 88} 88`"
              class="transition-all duration-200"
            />
          </svg>
          <span class="text-xs text-white font-medium">{{ progress }}%</span>
        </template>
        <template v-else>
          <svg class="w-6 h-6 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="17 8 12 3 7 8"/>
            <line x1="12" y1="3" x2="12" y2="15"/>
          </svg>
          <span class="text-[10px] text-white/80 font-medium">{{ isDragging ? 'Déposer' : 'Changer' }}</span>
        </template>
      </div>
    </div>

    <div class="text-center">
      <p class="text-xs text-slate-400">JPG, PNG ou WEBP · max 5 Mo</p>
      <p v-if="uploadError" class="text-xs text-red-400 mt-1">{{ uploadError }}</p>
    </div>

    <input id="load-img"
      ref="fileInputRef"
      type="file"
      accept="image/jpeg,image/png,image/webp"
      class="hidden"
      @change="handleFileChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useCloudinary } from '../../composables/useCloudinary'

const props = defineProps<{
  currentUrl: string | null
  initial: string
}>()

const emit = defineEmits<{
  uploaded: [url: string]
}>()

const { uploadImage, isUploading, uploadError, uploadProgress: progress } = useCloudinary()

const fileInputRef = ref<HTMLInputElement | null>(null)
const previewUrl = ref<string | null>(null)
const isDragging = ref(false)

function triggerFileInput() {
  if (!isUploading.value) fileInputRef.value?.click()
}

async function processFile(file: File) {
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
    return
  }
  if (file.size > 5 * 1024 * 1024) {
    return
  }

  previewUrl.value = URL.createObjectURL(file)

  const result = await uploadImage(file)
  if (result) {
    emit('uploaded', result.url)
  } else {
    previewUrl.value = null
  }
}

function handleFileChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) processFile(file)
}

function handleDrop(e: DragEvent) {
  isDragging.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) processFile(file)
}
</script>