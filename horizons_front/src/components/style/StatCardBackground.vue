<template>
  <div class="stat-bg">

    <!-- ═══ VISUALIZER A : basses — barres larges et lentes (purple) ═══ -->
    <svg v-if="color === 'purple'" class="bg-svg" viewBox="0 0 200 60" preserveAspectRatio="xMidYMax slice">
      <rect class="bar bar-a1"  x="4"   y="0" width="10" height="60" rx="3" fill="rgba(168,85,247,0.15)"/>
      <rect class="bar bar-a2"  x="18"  y="0" width="10" height="60" rx="3" fill="rgba(139,92,246,0.13)"/>
      <rect class="bar bar-a3"  x="32"  y="0" width="10" height="60" rx="3" fill="rgba(168,85,247,0.16)"/>
      <rect class="bar bar-a4"  x="46"  y="0" width="10" height="60" rx="3" fill="rgba(139,92,246,0.13)"/>
      <rect class="bar bar-a5"  x="60"  y="0" width="10" height="60" rx="3" fill="rgba(168,85,247,0.15)"/>
      <rect class="bar bar-a6"  x="74"  y="0" width="10" height="60" rx="3" fill="rgba(139,92,246,0.12)"/>
      <rect class="bar bar-a7"  x="88"  y="0" width="10" height="60" rx="3" fill="rgba(168,85,247,0.14)"/>
      <rect class="bar bar-a8"  x="102" y="0" width="10" height="60" rx="3" fill="rgba(139,92,246,0.13)"/>
      <rect class="bar bar-a9"  x="116" y="0" width="10" height="60" rx="3" fill="rgba(168,85,247,0.15)"/>
      <rect class="bar bar-a10" x="130" y="0" width="10" height="60" rx="3" fill="rgba(139,92,246,0.12)"/>
      <rect class="bar bar-a11" x="144" y="0" width="10" height="60" rx="3" fill="rgba(168,85,247,0.13)"/>
      <rect class="bar bar-a12" x="158" y="0" width="10" height="60" rx="3" fill="rgba(139,92,246,0.12)"/>
      <rect class="bar bar-a13" x="172" y="0" width="10" height="60" rx="3" fill="rgba(168,85,247,0.11)"/>
      <rect class="bar bar-a14" x="186" y="0" width="10" height="60" rx="3" fill="rgba(139,92,246,0.10)"/>
    </svg>

    <!-- ═══ VISUALIZER B : hautes fréquences — barres fines et rapides (cyan) ═══ -->
    <svg v-else-if="color === 'cyan'" class="bg-svg" viewBox="0 0 200 60" preserveAspectRatio="xMidYMax slice">
      <rect class="bar bar-b1"  x="2"   y="0" width="5" height="60" rx="2" fill="rgba(34,211,238,0.14)"/>
      <rect class="bar bar-b2"  x="10"  y="0" width="5" height="60" rx="2" fill="rgba(6,182,212,0.12)"/>
      <rect class="bar bar-b3"  x="18"  y="0" width="5" height="60" rx="2" fill="rgba(34,211,238,0.15)"/>
      <rect class="bar bar-b4"  x="26"  y="0" width="5" height="60" rx="2" fill="rgba(6,182,212,0.12)"/>
      <rect class="bar bar-b5"  x="34"  y="0" width="5" height="60" rx="2" fill="rgba(34,211,238,0.14)"/>
      <rect class="bar bar-b6"  x="42"  y="0" width="5" height="60" rx="2" fill="rgba(6,182,212,0.12)"/>
      <rect class="bar bar-b7"  x="50"  y="0" width="5" height="60" rx="2" fill="rgba(34,211,238,0.15)"/>
      <rect class="bar bar-b8"  x="58"  y="0" width="5" height="60" rx="2" fill="rgba(6,182,212,0.13)"/>
      <rect class="bar bar-b9"  x="66"  y="0" width="5" height="60" rx="2" fill="rgba(34,211,238,0.14)"/>
      <rect class="bar bar-b10" x="74"  y="0" width="5" height="60" rx="2" fill="rgba(6,182,212,0.12)"/>
      <rect class="bar bar-b11" x="82"  y="0" width="5" height="60" rx="2" fill="rgba(34,211,238,0.13)"/>
      <rect class="bar bar-b12" x="90"  y="0" width="5" height="60" rx="2" fill="rgba(6,182,212,0.11)"/>
      <rect class="bar bar-b13" x="98"  y="0" width="5" height="60" rx="2" fill="rgba(34,211,238,0.12)"/>
      <rect class="bar bar-b14" x="106" y="0" width="5" height="60" rx="2" fill="rgba(6,182,212,0.11)"/>
      <rect class="bar bar-b15" x="114" y="0" width="5" height="60" rx="2" fill="rgba(34,211,238,0.12)"/>
      <rect class="bar bar-b16" x="122" y="0" width="5" height="60" rx="2" fill="rgba(6,182,212,0.10)"/>
      <rect class="bar bar-b17" x="130" y="0" width="5" height="60" rx="2" fill="rgba(34,211,238,0.11)"/>
      <rect class="bar bar-b18" x="138" y="0" width="5" height="60" rx="2" fill="rgba(6,182,212,0.10)"/>
      <rect class="bar bar-b19" x="146" y="0" width="5" height="60" rx="2" fill="rgba(34,211,238,0.10)"/>
      <rect class="bar bar-b20" x="154" y="0" width="5" height="60" rx="2" fill="rgba(6,182,212,0.09)"/>
      <rect class="bar bar-b21" x="162" y="0" width="5" height="60" rx="2" fill="rgba(34,211,238,0.09)"/>
      <rect class="bar bar-b22" x="170" y="0" width="5" height="60" rx="2" fill="rgba(6,182,212,0.08)"/>
      <rect class="bar bar-b23" x="178" y="0" width="5" height="60" rx="2" fill="rgba(34,211,238,0.08)"/>
      <rect class="bar bar-b24" x="186" y="0" width="5" height="60" rx="2" fill="rgba(6,182,212,0.07)"/>
      <rect class="bar bar-b25" x="194" y="0" width="5" height="60" rx="2" fill="rgba(34,211,238,0.07)"/>
    </svg>

    <!-- ═══ VISUALIZER C : médiums — barres moyennes et organiques (pink) ═══ -->
    <svg v-else-if="color === 'pink'" class="bg-svg" viewBox="0 0 200 60" preserveAspectRatio="xMidYMax slice">
      <rect class="bar bar-c1"  x="3"   y="0" width="8" height="60" rx="2" fill="rgba(236,72,153,0.14)"/>
      <rect class="bar bar-c2"  x="15"  y="0" width="8" height="60" rx="2" fill="rgba(244,114,182,0.12)"/>
      <rect class="bar bar-c3"  x="27"  y="0" width="8" height="60" rx="2" fill="rgba(236,72,153,0.15)"/>
      <rect class="bar bar-c4"  x="39"  y="0" width="8" height="60" rx="2" fill="rgba(244,114,182,0.12)"/>
      <rect class="bar bar-c5"  x="51"  y="0" width="8" height="60" rx="2" fill="rgba(236,72,153,0.14)"/>
      <rect class="bar bar-c6"  x="63"  y="0" width="8" height="60" rx="2" fill="rgba(244,114,182,0.12)"/>
      <rect class="bar bar-c7"  x="75"  y="0" width="8" height="60" rx="2" fill="rgba(236,72,153,0.13)"/>
      <rect class="bar bar-c8"  x="87"  y="0" width="8" height="60" rx="2" fill="rgba(244,114,182,0.12)"/>
      <rect class="bar bar-c9"  x="99"  y="0" width="8" height="60" rx="2" fill="rgba(236,72,153,0.13)"/>
      <rect class="bar bar-c10" x="111" y="0" width="8" height="60" rx="2" fill="rgba(244,114,182,0.11)"/>
      <rect class="bar bar-c11" x="123" y="0" width="8" height="60" rx="2" fill="rgba(236,72,153,0.12)"/>
      <rect class="bar bar-c12" x="135" y="0" width="8" height="60" rx="2" fill="rgba(244,114,182,0.11)"/>
      <rect class="bar bar-c13" x="147" y="0" width="8" height="60" rx="2" fill="rgba(236,72,153,0.11)"/>
      <rect class="bar bar-c14" x="159" y="0" width="8" height="60" rx="2" fill="rgba(244,114,182,0.10)"/>
      <rect class="bar bar-c15" x="171" y="0" width="8" height="60" rx="2" fill="rgba(236,72,153,0.10)"/>
      <rect class="bar bar-c16" x="183" y="0" width="8" height="60" rx="2" fill="rgba(244,114,182,0.09)"/>
    </svg>

    <div class="stat-line" />
  </div>
</template>

<script setup lang="ts">
defineProps<{
  color: 'cyan' | 'purple' | 'pink'
}>()
</script>

<style scoped>
.stat-bg { position: absolute; inset: 0; border-radius: inherit; overflow: hidden; pointer-events: none; }
.bg-svg  { position: absolute; bottom: 0; left: 0; width: 100%; height: 75%; }

/* Toutes les barres s'animent depuis le bas */
.bar { transform-origin: center bottom; }

/* ── CARD A (purple) : ease-in-out doux ── */
.bar-a1  { animation: viz-loop 2.4s 0.00s ease-in-out infinite; }
.bar-a2  { animation: viz-loop 2.4s 0.18s ease-in-out infinite; }
.bar-a3  { animation: viz-loop 2.4s 0.36s ease-in-out infinite; }
.bar-a4  { animation: viz-loop 2.4s 0.54s ease-in-out infinite; }
.bar-a5  { animation: viz-loop 2.4s 0.72s ease-in-out infinite; }
.bar-a6  { animation: viz-loop 2.4s 0.90s ease-in-out infinite; }
.bar-a7  { animation: viz-loop 2.4s 1.08s ease-in-out infinite; }
.bar-a8  { animation: viz-loop 2.4s 1.26s ease-in-out infinite; }
.bar-a9  { animation: viz-loop 2.4s 0.30s ease-in-out infinite; }
.bar-a10 { animation: viz-loop 2.4s 0.60s ease-in-out infinite; }
.bar-a11 { animation: viz-loop 2.4s 0.90s ease-in-out infinite; }
.bar-a12 { animation: viz-loop 2.4s 1.20s ease-in-out infinite; }
.bar-a13 { animation: viz-loop 2.4s 0.45s ease-in-out infinite; }
.bar-a14 { animation: viz-loop 2.4s 0.75s ease-in-out infinite; }

/* ── CARD B (cyan) : ease classique ── */
.bar-b1  { animation: viz-loop 2.4s 0.00s ease infinite; }
.bar-b2  { animation: viz-loop 2.4s 0.10s ease infinite; }
.bar-b3  { animation: viz-loop 2.4s 0.20s ease infinite; }
.bar-b4  { animation: viz-loop 2.4s 0.30s ease infinite; }
.bar-b5  { animation: viz-loop 2.4s 0.40s ease infinite; }
.bar-b6  { animation: viz-loop 2.4s 0.50s ease infinite; }
.bar-b7  { animation: viz-loop 2.4s 0.60s ease infinite; }
.bar-b8  { animation: viz-loop 2.4s 0.70s ease infinite; }
.bar-b9  { animation: viz-loop 2.4s 0.80s ease infinite; }
.bar-b10 { animation: viz-loop 2.4s 0.90s ease infinite; }
.bar-b11 { animation: viz-loop 2.4s 1.00s ease infinite; }
.bar-b12 { animation: viz-loop 2.4s 1.10s ease infinite; }
.bar-b13 { animation: viz-loop 2.4s 1.20s ease infinite; }
.bar-b14 { animation: viz-loop 2.4s 1.30s ease infinite; }
.bar-b15 { animation: viz-loop 2.4s 1.40s ease infinite; }
.bar-b16 { animation: viz-loop 2.4s 1.50s ease infinite; }
.bar-b17 { animation: viz-loop 2.4s 0.20s ease infinite; }
.bar-b18 { animation: viz-loop 2.4s 0.40s ease infinite; }
.bar-b19 { animation: viz-loop 2.4s 0.60s ease infinite; }
.bar-b20 { animation: viz-loop 2.4s 0.80s ease infinite; }
.bar-b21 { animation: viz-loop 2.4s 1.00s ease infinite; }
.bar-b22 { animation: viz-loop 2.4s 1.20s ease infinite; }
.bar-b23 { animation: viz-loop 2.4s 1.40s ease infinite; }
.bar-b24 { animation: viz-loop 2.4s 0.10s ease infinite; }
.bar-b25 { animation: viz-loop 2.4s 0.30s ease infinite; }

/* ── CARD C (pink) : steps — beat quantifié ── */
.bar-c1  { animation: viz-steps 2.4s 0.00s cubic-bezier(0.45,0,0.55,1) infinite; }
.bar-c2  { animation: viz-steps 2.4s 0.16s cubic-bezier(0.45,0,0.55,1) infinite; }
.bar-c3  { animation: viz-steps 2.4s 0.32s cubic-bezier(0.45,0,0.55,1) infinite; }
.bar-c4  { animation: viz-steps 2.4s 0.48s cubic-bezier(0.45,0,0.55,1) infinite; }
.bar-c5  { animation: viz-steps 2.4s 0.64s cubic-bezier(0.45,0,0.55,1) infinite; }
.bar-c6  { animation: viz-steps 2.4s 0.80s cubic-bezier(0.45,0,0.55,1) infinite; }
.bar-c7  { animation: viz-steps 2.4s 0.96s cubic-bezier(0.45,0,0.55,1) infinite; }
.bar-c8  { animation: viz-steps 2.4s 1.12s cubic-bezier(0.45,0,0.55,1) infinite; }
.bar-c9  { animation: viz-steps 2.4s 1.28s cubic-bezier(0.45,0,0.55,1) infinite; }
.bar-c10 { animation: viz-steps 2.4s 0.24s cubic-bezier(0.45,0,0.55,1) infinite; }
.bar-c11 { animation: viz-steps 2.4s 0.48s cubic-bezier(0.45,0,0.55,1) infinite; }
.bar-c12 { animation: viz-steps 2.4s 0.72s cubic-bezier(0.45,0,0.55,1) infinite; }
.bar-c13 { animation: viz-steps 2.4s 0.96s cubic-bezier(0.45,0,0.55,1) infinite; }
.bar-c14 { animation: viz-steps 2.4s 0.32s cubic-bezier(0.45,0,0.55,1) infinite; }
.bar-c15 { animation: viz-steps 2.4s 0.64s cubic-bezier(0.45,0,0.55,1) infinite; }
.bar-c16 { animation: viz-steps 2.4s 0.96s cubic-bezier(0.45,0,0.55,1) infinite; }

@keyframes viz-loop {
  0%   { transform: scaleY(0.25); }
  50%  { transform: scaleY(1); }
  100% { transform: scaleY(0.25); }
}

@keyframes viz-steps {
  0%   { transform: scaleY(0.25); }
  25%  { transform: scaleY(0.6); }
  50%  { transform: scaleY(1); }
  75%  { transform: scaleY(0.5); }
  100% { transform: scaleY(0.25); }
}
/* Ligne de bas */
.stat-line { position: absolute; bottom: 0; left: 0; right: 0; height: 1px; }
.stat-bg--cyan   .stat-line { background: linear-gradient(90deg, transparent, #22d3ee, transparent); opacity: .3; }
.stat-bg--purple .stat-line { background: linear-gradient(90deg, transparent, #a855f7, transparent); opacity: .3; }
.stat-bg--pink   .stat-line { background: linear-gradient(90deg, transparent, #ec4899, transparent); opacity: .3; }
</style>