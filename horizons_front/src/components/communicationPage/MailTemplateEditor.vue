<template>
  <div class="flex flex-col gap-3">

    <!-- ── Barre de gestion des templates ── -->
    <div class="flex items-center gap-2 px-3 py-2.5 bg-slate-800/60 border border-white/8 rounded-xl">

      <!-- Sélecteur de template -->
      <div class="relative flex-1 min-w-0" data-template-dropdown>
        <button
          class="w-full flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs text-left
                 bg-slate-900/60 border border-white/8 hover:border-white/15
                 text-slate-300 hover:text-white transition-all truncate"
          @click="showDropdown = !showDropdown"
        >
          <BookOpen class="w-3.5 h-3.5 shrink-0 text-slate-500" />
          <span class="flex-1 truncate">
            {{ activeTemplate ? activeTemplate.title : 'Choisir un template…' }}
          </span>
          <ChevronDown
            class="w-3 h-3 shrink-0 text-slate-500 transition-transform"
            :class="showDropdown && 'rotate-180'"
          />
        </button>

        <!-- Dropdown liste des templates -->
        <Transition
          enter-active-class="transition-all duration-150 ease-out"
          leave-active-class="transition-all duration-100 ease-in"
          enter-from-class="opacity-0 translate-y-1"
          leave-to-class="opacity-0 translate-y-1"
        >
          <div
            v-if="showDropdown"
            class="absolute top-full mt-1 left-0 right-0 z-30
                   bg-slate-800 border border-white/10 rounded-xl shadow-2xl overflow-hidden"
          >
            <!-- Chargement -->
            <div v-if="isLoading" class="flex items-center justify-center gap-2 py-4 text-xs text-slate-500">
              <Loader2 class="w-3.5 h-3.5 animate-spin" />
              Chargement…
            </div>

            <!-- Liste vide -->
            <div v-else-if="templates.length === 0" class="py-4 text-center text-xs text-slate-600">
              Aucun template enregistré
            </div>

            <!-- Liste des templates -->
            <div v-else class="max-h-52 overflow-y-auto p-1">
              <button
                v-for="t in templates"
                :key="t.id"
                class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left
                       text-xs transition-colors group"
                :class="activeTemplate?.id === t.id
                  ? 'bg-cyan-500/12 text-cyan-300'
                  : 'text-slate-300 hover:text-white hover:bg-slate-700/60'"
                @click="loadTemplate(t)"
              >
                <FileText class="w-3.5 h-3.5 shrink-0 opacity-60" />
                <div class="flex-1 min-w-0">
                  <p class="font-medium truncate">{{ t.title }}</p>
                  <p class="text-[10px] text-slate-500 truncate mt-0.5">{{ t.subject }}</p>
                </div>
                <!-- Supprimer -->
                <button
                  class="shrink-0 w-5 h-5 flex items-center justify-center rounded opacity-0
                         group-hover:opacity-100 text-slate-500 hover:text-red-400 transition-all"
                  :title="`Supprimer «${t.title}»`"
                  @click.stop="confirmDelete(t)"
                >
                  <Trash2 class="w-3 h-3" />
                </button>
              </button>
            </div>

            <!-- Créer nouveau -->
            <div class="border-t border-white/6 p-1">
              <button
                class="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-xs
                       text-slate-400 hover:text-cyan-300 hover:bg-slate-700/50 transition-colors"
                @click="startCreate"
              >
                <Plus class="w-3.5 h-3.5" />
                Nouveau template
              </button>
            </div>
          </div>
        </Transition>
      </div>

      <!-- Divider -->
      <div class="h-5 w-px bg-white/8 shrink-0" />

      <!-- Sauvegarder / Mettre à jour -->
      <button
        v-if="activeTemplate"
        class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium
               bg-cyan-500/12 border border-cyan-500/20 text-cyan-400
               hover:bg-cyan-500/20 hover:text-cyan-300 transition-all disabled:opacity-50"
        :disabled="isSaving"
        :title="`Mettre à jour «${activeTemplate.title}»`"
        @click="handleUpdate"
      >
        <Loader2 v-if="isSaving" class="w-3 h-3 animate-spin" />
        <Save v-else class="w-3 h-3" />
        Mettre à jour
      </button>

      <button
        class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium
               bg-slate-700 border border-white/8 text-slate-300
               hover:bg-slate-600 hover:text-white transition-all disabled:opacity-50"
        :disabled="isSaving"
        title="Enregistrer comme nouveau template"
        @click="startCreate"
      >
        <Plus class="w-3 h-3" />
        Enregistrer
      </button>

      <!-- Réinitialiser (si template actif) -->
      <button
        v-if="activeTemplate"
        class="w-7 h-7 flex items-center justify-center rounded-lg text-slate-500
               hover:text-slate-300 hover:bg-slate-700 transition-colors"
        title="Détacher le template (édition libre)"
        @click="detachTemplate"
      >
        <X class="w-3.5 h-3.5" />
      </button>

    </div>

    <!-- Objet du mail -->
    <div class="flex items-center gap-3 px-4 py-2.5 bg-slate-800/50 border border-white/10 rounded-xl">
      <span class="shrink-0 text-xs font-semibold uppercase tracking-widest text-slate-500">Objet</span>
      <input
        v-model="subjectModel"
        type="text"
        placeholder="Objet du mail…"
        class="flex-1 bg-transparent text-sm text-slate-100 placeholder-slate-600 outline-none"
      />
    </div>

    <!-- Éditeur riche -->
    <RichEditor
      ref="editorRef"
      v-model="bodyModel"
      placeholder="Rédigez votre message ici. Utilisez les variables à droite pour personnaliser chaque mail."
    />

    <!-- ── Modal : nommer le template ── -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition-all duration-150 ease-out"
        leave-active-class="transition-all duration-100 ease-in"
        enter-from-class="opacity-0"
        leave-to-class="opacity-0"
      >
        <div
          v-if="showSaveModal"
          class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
          @click.self="showSaveModal = false"
        >
          <div class="bg-slate-900 border border-white/10 rounded-2xl shadow-2xl p-6 w-80">
            <h3 class="text-sm font-semibold text-white mb-4">Enregistrer le template</h3>
            <input
              v-model="newTemplateName"
              ref="saveInputRef"
              type="text"
              placeholder="Nom du template…"
              class="w-full px-3 py-2 text-sm bg-slate-800 border border-white/10 rounded-lg
                     text-slate-100 placeholder-slate-600 outline-none focus:border-cyan-500/40
                     transition-colors mb-4"
              @keydown.enter="handleCreate"
              @keydown.escape="showSaveModal = false"
            />
            <div class="flex gap-2 justify-end">
              <button
                class="px-4 py-2 text-xs text-slate-400 hover:text-white transition-colors"
                @click="showSaveModal = false"
              >
                Annuler
              </button>
              <button
                class="px-4 py-2 text-xs font-medium bg-cyan-600 hover:bg-cyan-500
                       text-white rounded-lg transition-colors disabled:opacity-50"
                :disabled="!newTemplateName.trim() || isSaving"
                @click="handleCreate"
              >
                <Loader2 v-if="isSaving" class="w-3 h-3 animate-spin inline mr-1" />
                Enregistrer
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- ── Modal : confirmer suppression ── -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition-all duration-150 ease-out"
        leave-active-class="transition-all duration-100 ease-in"
        enter-from-class="opacity-0"
        leave-to-class="opacity-0"
      >
        <div
          v-if="templateToDelete"
          class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
          @click.self="templateToDelete = null"
        >
          <div class="bg-slate-900 border border-white/10 rounded-2xl shadow-2xl p-6 w-80">
            <h3 class="text-sm font-semibold text-white mb-2">Supprimer le template ?</h3>
            <p class="text-xs text-slate-400 mb-5">
              «<strong class="text-slate-200">{{ templateToDelete.title }}</strong>» sera supprimé définitivement.
            </p>
            <div class="flex gap-2 justify-end">
              <button
                class="px-4 py-2 text-xs text-slate-400 hover:text-white transition-colors"
                @click="templateToDelete = null"
              >
                Annuler
              </button>
              <button
                class="px-4 py-2 text-xs font-medium bg-red-600 hover:bg-red-500
                       text-white rounded-lg transition-colors"
                @click="handleDelete"
              >
                Supprimer
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import {
  BookOpen, ChevronDown, FileText, Trash2, Plus, Save,
  X, Loader2,
} from 'lucide-vue-next'
import RichEditor from '../tasks/richTextEditor/TextEditorView.vue'
import {
  fetchMailTemplates,
  createMailTemplate,
  updateMailTemplate,
  deleteMailTemplate,
  type MailTemplateRecord,
} from '../../composables/useMailTemplate'

// ── Props & emits ──────────────────────────────────────────────────────────────
const props = defineProps<{
  subject:    string
  body:       string
  apiBaseUrl: string
}>()

const emit = defineEmits<{
  'update:subject': [v: string]
  'update:body':    [v: string]
  saved:            [template: MailTemplateRecord]
  deleted:          [id: string]
  error:            [message: string]
}>()

// ── Modèles ────────────────────────────────────────────────────────────────────
const subjectModel = computed({
  get: () => props.subject,
  set: (v) => emit('update:subject', v),
})
const bodyModel = computed({
  get: () => props.body,
  set: (v) => emit('update:body', v),
})

// ── Éditeur ────────────────────────────────────────────────────────────────────
const editorRef = ref<InstanceType<typeof RichEditor> | null>(null)

function insertAtCursor(text: string) {
  editorRef.value?.insertAtCursor(text)
}
defineExpose({ insertAtCursor })

// ── État templates ─────────────────────────────────────────────────────────────
const templates      = ref<MailTemplateRecord[]>([])
const activeTemplate = ref<MailTemplateRecord | null>(null)
const isLoading      = ref(false)
const isSaving       = ref(false)
const showDropdown   = ref(false)

// ── Charger les templates au montage ──────────────────────────────────────────
onMounted(async () => {
  isLoading.value = true
  try {
    templates.value = await fetchMailTemplates(props.apiBaseUrl)
  } catch {
    emit('error', 'Impossible de charger les templates')
  } finally {
    isLoading.value = false
  }
  document.addEventListener('click', onDocumentClick)
})

onUnmounted(() => {
  document.removeEventListener('click', onDocumentClick)
})



// Fermer le dropdown si clic à l'extérieur
function onDocumentClick(e: MouseEvent) {
  if (!(e.target as HTMLElement).closest('[data-template-dropdown]')) {
    showDropdown.value = false
  }
}

// ── Charger un template dans l'éditeur ────────────────────────────────────────
function loadTemplate(t: MailTemplateRecord) {
  activeTemplate.value = t
  emit('update:subject', t.subject)
  emit('update:body', t.content)
  showDropdown.value = false
}

function detachTemplate() {
  activeTemplate.value = null
}

// ── Mettre à jour le template actif ───────────────────────────────────────────
async function handleUpdate() {
  if (!activeTemplate.value) return
  isSaving.value = true
  try {
    const updated = await updateMailTemplate(props.apiBaseUrl, activeTemplate.value.id, {
      subject: props.subject,
      content: props.body,
    })
    // Synchroniser la liste locale
    const idx = templates.value.findIndex(t => t.id === updated.id)
    if (idx !== -1) templates.value[idx] = updated
    activeTemplate.value = updated
    emit('saved', updated)
  } catch {
    emit('error', 'Échec de la mise à jour du template')
  } finally {
    isSaving.value = false
  }
}

// ── Créer un nouveau template ──────────────────────────────────────────────────
const showSaveModal   = ref(false)
const newTemplateName = ref('')
const saveInputRef    = ref<HTMLInputElement | null>(null)

function startCreate() {
  showDropdown.value  = false
  newTemplateName.value = activeTemplate.value ? `${activeTemplate.value.title} (copie)` : ''
  showSaveModal.value = true
  nextTick(() => saveInputRef.value?.focus())
}

async function handleCreate() {
  if (!newTemplateName.value.trim()) return
  isSaving.value = true
  try {
    const created = await createMailTemplate(props.apiBaseUrl, {
      title:   newTemplateName.value.trim(),
      subject: props.subject,
      content: props.body,
    })
    templates.value.unshift(created)
    activeTemplate.value = created
    showSaveModal.value  = false
    newTemplateName.value = ''
    emit('saved', created)
  } catch {
    emit('error', 'Échec de la sauvegarde du template')
  } finally {
    isSaving.value = false
  }
}

// ── Supprimer un template ──────────────────────────────────────────────────────
const templateToDelete = ref<MailTemplateRecord | null>(null)

function confirmDelete(t: MailTemplateRecord) {
  showDropdown.value  = false
  templateToDelete.value = t
}

async function handleDelete() {
  if (!templateToDelete.value) return
  const id = templateToDelete.value.id
  try {
    await deleteMailTemplate(props.apiBaseUrl, id)
    templates.value = templates.value.filter(t => t.id !== id)
    if (activeTemplate.value?.id === id) activeTemplate.value = null
    emit('deleted', id)
  } catch {
    emit('error', 'Échec de la suppression du template')
  } finally {
    templateToDelete.value = null
  }
}
</script>