<template>
  <div
    class="ocean-card"
    :class="{ 'ocean-card--highlight': highlight }"
    :style="`animation-delay: ${delay}ms`"
    @mouseenter="ripple"
    ref="cardRef"
  >
    <!-- Reflet hover -->
    <span class="card-shine" />

    <div class="card-icon">{{ icon }}</div>
    <div class="card-content">
      <div class="card-label">{{ label }}</div>
      <div class="card-sublabel">{{ sublabel }}</div>
    </div>

    <!-- Ripple canvas -->
    <span v-if="showRipple" class="ripple-el" :style="rippleStyle" @animationend="showRipple = false" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Props {
  icon: string; label: string; sublabel: string
  highlight?: boolean; delay?: number
}
withDefaults(defineProps<Props>(), { highlight: false, delay: 0 })

const showRipple = ref(false)
const rippleStyle = ref('')
const cardRef = ref<HTMLElement | null>(null)

function ripple(e: MouseEvent) {
  if (!cardRef.value) return
  const rect = cardRef.value.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  rippleStyle.value = `left:${x}px;top:${y}px`
  showRipple.value = false
  setTimeout(() => (showRipple.value = true), 10)
}
</script>

<style scoped>
.ocean-card {
  position: relative; overflow: hidden;
  display: flex; align-items: center; gap: 12px;
  padding: 12px 16px; border-radius: 14px;
  background: rgba(4, 24, 40, 0.80);
  border: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(12px);
  cursor: pointer; min-width: 190px;
  transition: transform 0.25s cubic-bezier(0.34,1.56,0.64,1),
              border-color 0.2s, box-shadow 0.2s;
  animation: cardFloat 0.5s cubic-bezier(0.22,1,0.36,1) both;
}
.ocean-card:hover {
  transform: translateY(-4px) scale(1.02);
  border-color: rgba(34, 211, 238, 0.3);
  box-shadow: 0 8px 32px rgba(6, 182, 212, 0.15);
}
.ocean-card--highlight {
  background: rgba(6, 182, 212, 0.1);
  border-color: rgba(34, 211, 238, 0.3);
  box-shadow: 0 0 20px rgba(6, 182, 212, 0.1);
}
@keyframes cardFloat {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* Reflet lumineux au hover */
.card-shine {
  position: absolute; inset: 0;
  background: linear-gradient(105deg, transparent 40%, rgba(255,255,255,0.05) 50%, transparent 60%);
  transform: translateX(-100%);
  transition: transform 0.5s ease;
  pointer-events: none;
}
.ocean-card:hover .card-shine { transform: translateX(100%); }

.card-icon {
  font-size: 1.4rem; flex-shrink: 0;
  transition: transform 0.3s cubic-bezier(0.34,1.56,0.64,1);
}
.ocean-card:hover .card-icon { transform: scale(1.2) rotate(-5deg); }

.card-content { flex: 1; min-width: 0; }
.card-label {
  font-size: 0.85rem; font-weight: 600;
  color: #f0f9ff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.ocean-card--highlight .card-label { color: #22d3ee; }
.card-sublabel {
  font-size: 0.7rem; color: #64748b; margin-top: 1px;
  font-family: 'Courier New', monospace; letter-spacing: 0.05em;
}

/* Ripple */
.ripple-el {
  position: absolute; width: 8px; height: 8px;
  border-radius: 50%; margin: -4px;
  background: rgba(34, 211, 238, 0.35);
  animation: rippleAnim 0.5s ease-out forwards;
  pointer-events: none;
}
@keyframes rippleAnim {
  to { transform: scale(18); opacity: 0; }
}
</style>