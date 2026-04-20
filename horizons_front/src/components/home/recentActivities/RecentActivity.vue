<template>
  <section class="mt-5">
    <div class="flex items-center justify-between mb-3">
      <div class="flex items-center gap-2.5">
        <div class="activity-dot" />
        <h2 class="text-base font-semibold tracking-wide text-slate-200" style="font-family:'Courier New',monospace;letter-spacing:0.08em;text-transform:uppercase;font-size:0.75rem;">
          Activité récente
        </h2>
        <span v-if="activities.length > 0"
          class="text-xs font-medium px-2 py-0.5 rounded-full bg-white/5 text-slate-400 border border-white/10">
          {{ activities.length }}
        </span>
      </div>
    </div>

    <div class="bg-slate-900/60 border border-white/8 rounded-xl overflow-hidden backdrop-blur-sm">
      <div class="max-h-72 h-72 overflow-y-auto custom-scrollbar">
        <ActivityItem
          v-for="(activity, index) in activities" :key="activity.id"
          :activity="activity" :is-last="index === activities.length - 1"
        />
        <div v-if="activities.length === 0" class="p-10 text-center text-slate-600">
          <div class="text-4xl mb-3 opacity-30">〰️</div>
          <p class="text-sm tracking-widest uppercase" style="font-family:'Courier New',monospace;">Calme plat</p>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import ActivityItem from './ActivityItem.vue'
import type { Activity } from '../../../types/activity.types'
defineProps<{ activities: Activity[] }>()
</script>

<style scoped>
.activity-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: #22d3ee;
  box-shadow: 0 0 8px #22d3ee;
  animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.4); opacity: 0.6; }
}
</style>