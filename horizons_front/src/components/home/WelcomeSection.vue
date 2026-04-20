<template>
  <section class="welcome-section relative overflow-hidden rounded-2xl border border-white/10" style="min-height: 280px;">

    <OceanBackground />

    <!-- ── Contenu ── -->
    <div class="relative z-10 flex flex-col md:flex-row md:items-start md:justify-between gap-6 p-8 pb-20">

      <div class="flex-1 reveal-left">
        <div class="festival-eyebrow mb-2" v-if="festival">
          <span class="eyebrow-dot" />
          {{ festival.name }} · Édition {{ festival.edition }}
        </div>
        <h1 class="welcome-title">
          Bienvenue,<br/>
          <span class="username-gradient">{{ user?.username }}</span>
        </h1>
      </div>

      <div class="flex flex-col sm:flex-row md:flex-col gap-3 reveal-right">
        <template v-if="isLoading">
          <div v-for="i in 3" :key="i" class="skeleton" style="width:200px;height:64px;border-radius:14px" />
        </template>
        <template v-else-if="festival">
          <OceanCard
            v-for="(card, i) in cards" :key="i"
            :icon="card.icon"
            :label="card.label"
            :sublabel="card.sublabel"
            :highlight="card.highlight"
            :delay="i * 80"
          />
        </template>
        <div v-else class="no-festival-badge">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          Aucun festival configuré
        </div>
      </div>
    </div>

    <div v-if="festival && countdown" class="countdown-ribbon" :class="countdown.ribbonClass">
      <span class="countdown-number">{{ countdown.label }}</span>
    </div>

  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import OceanCard from './FestivalCard.vue'
import OceanBackground from '../style/OceanBackground.vue'
import type { FestivalResponse } from '../../types/festival.types'
import type { UserResponse } from '../../types/user.types'
import { useWeather } from '../../composables/useWeather'

interface Props {
  user: UserResponse | null
  festival: FestivalResponse | null
  isLoading: boolean
}
const props = defineProps<Props>()

const { weather, fetchWeatherForDate } = useWeather()

onMounted(() => {
  fetchWeatherForDate(new Date().toLocaleDateString('en-CA'))
})

watch(
  () => props.festival,
  (festival) => {
    if (festival) fetchWeatherForDate(new Date().toLocaleDateString('en-CA'))
  },
)

// ── Countdown ────────────────────────────────────────────────
const now = ref(new Date())
let timer: ReturnType<typeof setInterval> | null = null

function getIntervalMs(): number {
  if (!props.festival) return 60_000
  const start = new Date(props.festival.start_date)
  start.setHours(0, 0, 0, 0)
  const msUntilStart = start.getTime() - Date.now()
  if (msUntilStart > 0 && msUntilStart < 48 * 3_600_000) return 1_000
  return 60_000
}

function restartTimer() {
  if (timer) clearInterval(timer)
  const interval = getIntervalMs()
  timer = setInterval(() => { now.value = new Date() }, interval)
}

onMounted(() => restartTimer())
onUnmounted(() => { if (timer) clearInterval(timer) })

// Redémarre le timer si le festival change (ex: après une mise à jour)
watch(() => props.festival, () => restartTimer())

const countdown = computed(() => {
  if (!props.festival) return null

  const start = new Date(props.festival.start_date)
  start.setHours(0, 0, 0, 0)

  const end = new Date(props.festival.end_date)
  end.setHours(23, 59, 59, 999)

  const msUntilStart = start.getTime() - now.value.getTime()
  const msUntilEnd   = end.getTime()   - now.value.getTime()

  // Festival terminé
  if (msUntilEnd < 0) {
    return { label: 'Festival terminé', ribbonClass: 'ribbon-ended' }
  }

  // Festival en cours
  if (msUntilStart <= 0) {
    return { label: 'Festival en cours', ribbonClass: 'ribbon-live' }
  }

  const hoursUntil = msUntilStart / 3_600_000

  // Moins de 48h → h/m/s
  if (hoursUntil < 48) {
    const h = Math.floor(hoursUntil)
    const m = Math.floor((msUntilStart % 3_600_000) / 60_000)
    const s = Math.floor((msUntilStart % 60_000) / 1_000)
    const parts: string[] = []
    if (h > 0) parts.push(`${h}h`)
    if (m > 0 || h > 0) parts.push(`${m}m`)
    parts.push(`${s}s`)
    return { label: `${parts.join(' ')} avant le festival`, ribbonClass: 'ribbon-soon' }
  }

  // Plus de 48h → jours
  const daysUntil = Math.floor(msUntilStart / 86_400_000)
  return { label: `J-${daysUntil} avant le festival`, ribbonClass: '' }
})

// ── Helpers ──────────────────────────────────────────────────
function formatDateRange(start: string, end: string): string {
  const s = new Date(start)
  const e = new Date(end)
  if (s.getMonth() === e.getMonth() && s.getFullYear() === e.getFullYear()) {
    return `${s.getDate()} – ${e.toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })}`
  }
  return `${s.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })} – ${e.toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })}`
}

const cards = computed(() => props.festival ? [
  {
    icon: '🗓️',
    label: formatDateRange(props.festival.start_date, props.festival.end_date),
    sublabel: 'Dates du festival',
    highlight: false,
  },
  {
    icon: '⚓',
    label: props.festival.location_city,
    sublabel: props.festival.location_name,
    highlight: false,
  },
  {
    icon: weather.value?.icon ?? '🌊',
    label: weather.value?.description ?? 'Météo du jour',
    sublabel: weather.value ? `${weather.value.temperature}°C · ${weather.value.windspeed} km/h` : 'Chargement…',
    highlight: false,
  },
] : [])
</script>

<style scoped>
.welcome-section {
  background: linear-gradient(160deg, #020d1a 0%, #041828 40%, #062235 70%, #041525 100%);
  font-family: 'Georgia', 'Times New Roman', serif;
}

.festival-eyebrow {
  display: flex; align-items: center; gap: 8px;
  font-family: 'Courier New', monospace;
  font-size: 0.7rem; letter-spacing: 0.15em;
  text-transform: uppercase; color: #67e8f9;
}
.eyebrow-dot {
  display: inline-block; width: 6px; height: 6px;
  border-radius: 50%; background: #22d3ee;
  animation: blink 2s ease-in-out infinite;
}
@keyframes blink {
  0%, 100% { opacity: 1; } 50% { opacity: 0.3; }
}

.welcome-title {
  font-size: clamp(1.8rem, 4vw, 2.8rem);
  font-weight: 800; line-height: 1.1;
  color: #f0f9ff; letter-spacing: -0.02em;
}
.username-gradient {
  background: linear-gradient(90deg, #22d3ee, #818cf8, #22d3ee);
  background-size: 200% auto;
  -webkit-background-clip: text; background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: shimmer 3s linear infinite;
}
@keyframes shimmer {
  0%   { background-position: 0%   center; }
  100% { background-position: 200% center; }
}

/* ── Ribbon ── */
.countdown-ribbon {
  position: absolute; bottom: 18px; left: 50%;
  transform: translateX(-50%);
  display: flex; align-items: baseline; gap: 8px;
  background: rgba(6,182,212,0.12);
  border: 1px solid rgba(6,182,212,0.25);
  backdrop-filter: blur(8px);
  padding: 5px 20px; border-radius: 999px;
  white-space: nowrap; z-index: 3;
  transition: background 0.4s, border-color 0.4s;
}
.countdown-number {
  font-family: 'Courier New', monospace;
  font-size: 1.1rem; font-weight: 700; color: #22d3ee;
}

/* En cours */
.ribbon-live {
  background: rgba(16,185,129,0.12);
  border-color: rgba(16,185,129,0.3);
}
.ribbon-live .countdown-number {
  color: #34d399;
  animation: pulse-green 2s ease-in-out infinite;
}
@keyframes pulse-green {
  0%, 100% { opacity: 1; } 50% { opacity: 0.6; }
}

/* Bientôt < 48h */
.ribbon-soon {
  background: rgba(251,191,36,0.1);
  border-color: rgba(251,191,36,0.28);
}
.ribbon-soon .countdown-number { color: #fbbf24; }

/* Terminé */
.ribbon-ended {
  background: rgba(100,116,139,0.1);
  border-color: rgba(100,116,139,0.22);
}
.ribbon-ended .countdown-number { color: #64748b; }

.reveal-left  { animation: revealLeft  0.7s cubic-bezier(0.22,1,0.36,1) both; }
.reveal-right { animation: revealRight 0.7s 0.15s cubic-bezier(0.22,1,0.36,1) both; }
@keyframes revealLeft  {
  from { opacity: 0; transform: translateX(-24px); }
  to   { opacity: 1; transform: translateX(0); }
}
@keyframes revealRight {
  from { opacity: 0; transform: translateX(24px); }
  to   { opacity: 1; transform: translateX(0); }
}

.skeleton {
  animation: skeleton-pulse 1.4s ease-in-out infinite;
  background: rgba(255,255,255,0.06);
}
@keyframes skeleton-pulse {
  0%, 100% { opacity: 0.4; } 50% { opacity: 0.8; }
}

.no-festival-badge {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 16px; border-radius: 12px;
  background: rgba(245,158,11,0.1);
  border: 1px solid rgba(245,158,11,0.25);
  color: #fbbf24; font-size: 0.85rem;
}
</style>