<template>
  <div class="flex flex-col gap-5">

    <!-- Liste des commentaires -->
    <div v-if="comments.length" class="flex flex-col gap-5">
      <div v-for="c in comments" :key="c.id" class="flex gap-3 items-start group">
        <div class="shrink-0 mt-0.5">
          <div class="w-8 h-8 rounded-xl overflow-hidden ring-1 ring-white/10"
            :style="{ background: c.author.color + '22' }">
            <img v-if="c.author.avatar_url" :src="c.author.avatar_url" class="w-full h-full object-cover" />
            <div v-else class="w-full h-full flex items-center justify-center text-xs font-bold"
              :style="{ color: c.author.color }">{{ c.author.initials }}</div>
          </div>
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 mb-1.5">
            <span class="text-sm font-semibold text-white">{{ c.author.username }}</span>
            <span class="text-[11px] text-slate-500 tabular-nums">{{ fmtTime(c.created_at) }}</span>
            <button
              v-if="currentUser && c.author.id === currentUser.id"
              :disabled="deletingId === c.id"
              class="ml-auto text-[10px] text-slate-600 hover:text-red-400
                     opacity-0 group-hover:opacity-100
                     disabled:opacity-30 disabled:cursor-not-allowed
                     transition-all duration-150 cursor-pointer"
              @click="handleDelete(c.id)"
            >{{ deletingId === c.id ? 'Suppression…' : 'Supprimer' }}</button>
          </div>
          <div
            class="bg-slate-800/70 border border-white/[0.07] rounded-2xl rounded-tl-md px-4 py-3 text-sm text-slate-300 leading-relaxed prose-comments"
            v-html="c.content"
          />
        </div>
      </div>
    </div>

    <p v-else class="text-sm text-slate-600 italic">Aucun commentaire pour l'instant.</p>

    <!-- Zone de saisie -->
    <div class="flex gap-3 items-start pt-3 border-t border-white/6">
      <div v-if="currentUser" class="shrink-0 mt-0.5">
        <div class="w-8 h-8 rounded-xl overflow-hidden ring-1 ring-white/10"
          :style="{ background: currentUser.color + '22' }">
          <img v-if="currentUser.avatar_url" :src="currentUser.avatar_url" class="w-full h-full object-cover" />
          <div v-else class="w-full h-full flex items-center justify-center text-xs font-bold"
            :style="{ color: currentUser.color }">{{ currentUser.initials }}</div>
        </div>
      </div>
      <div class="flex-1 min-w-0">
        <textarea
          v-model="newComment"
          placeholder="Écrire un commentaire…"
          rows="2"
          class="w-full bg-slate-800/60 border border-white/10 rounded-xl px-3 py-2.5 text-sm text-slate-300 placeholder-slate-600 outline-none focus:border-cyan-500/40 resize-none transition-colors"
          @keydown.enter.ctrl.prevent="submit"
          @keydown.enter.meta.prevent="submit"
        />
        <div class="flex items-center justify-between mt-1.5">
          <span class="text-[10px] text-slate-600">Ctrl+Entrée pour envoyer</span>
          <button
            :disabled="!newComment.trim()"
            @click="submit"
            class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 hover:bg-cyan-500/25 transition-all disabled:opacity-30 disabled:cursor-not-allowed"
          >Commenter</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { Comment, User } from '../../../types/task.types'

const props = defineProps<{ comments: Comment[]; currentUser?: User; taskTitle: string }>()
const emit = defineEmits<{
  comment:       [content: string]
  deleteComment: [commentId: number]
}>()

const newComment = ref('')
const deletingId = ref<number | null>(null)

const fmtTime = (iso: string) => {
  const d    = new Date(iso)
  const diff = Date.now() - d.getTime()
  const m    = Math.floor(diff / 60000)
  const h    = Math.floor(diff / 3600000)
  const day  = Math.floor(diff / 86400000)
  if (m < 1)   return 'À l\'instant'
  if (m < 60)  return `Il y a ${m} min`
  if (h < 24)  return `Il y a ${h}h`
  if (day < 7) return `Il y a ${day}j`
  return d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })
}

const handleDelete = async (id: number) => {
  deletingId.value = id
  emit('deleteComment', id)
}

const submit = () => {
  if (!newComment.value.trim()) return
  emit('comment', newComment.value)
  newComment.value = ''
}
</script>

<style>
.prose-comments p      { margin: 0; }
.prose-comments ul     { list-style: disc; padding-left: 1.25rem; margin: 0.25rem 0; }
.prose-comments strong { color: rgba(255,255,255,0.9); }
</style>