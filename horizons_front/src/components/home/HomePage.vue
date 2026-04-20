<template>
  <div class="bg-linear-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
    <main class="container mx-auto px-6 py-8 max-w-7xl">
      <WelcomeSection
        v-if="userStore.user"
        :user="userStore.user"
        :festival="festival"
        :is-loading="isLoading"
      />
      <RecentActivity
        :activities="activities"
        class="mt-4"
      />
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import WelcomeSection from './WelcomeSection.vue'
import RecentActivity from './recentActivities/RecentActivity.vue'
import { useUserStore } from '../../stores/useUserStore'
import { useActivity } from '../../composables/Activity/useActivity'
import { useFestivalStore } from '../../stores/useFestivalStore'
import { storeToRefs } from 'pinia'

const userStore = useUserStore()
const { fetchActivities, activities } = useActivity()
const { festival, isLoading } = storeToRefs(useFestivalStore())
const { fetchFestival } = useFestivalStore()

onMounted(async () => {
  await Promise.all([fetchActivities(25), fetchFestival()])
})
</script>

<style scoped>
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}
.container { animation: fadeIn 0.6s ease-out; }
</style>