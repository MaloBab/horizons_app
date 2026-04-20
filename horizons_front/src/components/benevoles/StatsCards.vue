<template>
  <div class="grid grid-cols-1 gap-3 md:grid-cols-3">
    <StatCard title="Total Bénévoles"    :value="stats.total.toString()"
      icon="users"    color="purple" sub="inscrits cette année" />
    <StatCard title="Moy. Disponibilités" :value="stats.avgSlots.toString()"
      icon="calendar" color="cyan"   suffix="créneaux" />
    <StatCard title="Avec Affinités"     :value="stats.withMates.toString()"
      icon="heart"    color="pink"
      :progress="stats.total > 0 ? Math.round((stats.withMates / stats.total) * 100) : 0" />
  </div>
</template>

<script setup lang="ts">
import StatCard from './StatCard.vue'

interface Stats {
  total: number
  avgSlots: string
  withMates: number
}

defineProps<{ stats: Stats }>()
</script>