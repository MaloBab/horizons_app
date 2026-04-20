<template>
  <div ref="containerRef" class="music-bg">
    <svg ref="svgRef" class="scene-svg" :viewBox="`0 0 ${W} 64`" preserveAspectRatio="xMidYMid slice">
      <defs>
        <radialGradient id="sp1" cx="50%" cy="100%" r="100%" fx="50%" fy="100%">
          <stop offset="0%"   stop-color="#22d3ee" stop-opacity=".42"/>
          <stop offset="100%" stop-color="#22d3ee" stop-opacity="0"/>
        </radialGradient>
        <radialGradient id="sp2" cx="50%" cy="100%" r="100%" fx="50%" fy="100%">
          <stop offset="0%"   stop-color="#a855f7" stop-opacity=".36"/>
          <stop offset="100%" stop-color="#a855f7" stop-opacity="0"/>
        </radialGradient>
        <radialGradient id="sp3" cx="50%" cy="100%" r="100%" fx="50%" fy="100%">
          <stop offset="0%"   stop-color="#ec4899" stop-opacity=".34"/>
          <stop offset="100%" stop-color="#ec4899" stop-opacity="0"/>
        </radialGradient>
        <radialGradient id="sp4" cx="50%" cy="100%" r="100%" fx="50%" fy="100%">
          <stop offset="0%"   stop-color="#f59e0b" stop-opacity=".34"/>
          <stop offset="100%" stop-color="#f59e0b" stop-opacity="0"/>
        </radialGradient>
        <radialGradient id="sp5" cx="50%" cy="100%" r="100%" fx="50%" fy="100%">
          <stop offset="0%"   stop-color="#22d3ee" stop-opacity=".28"/>
          <stop offset="100%" stop-color="#22d3ee" stop-opacity="0"/>
        </radialGradient>
        <radialGradient id="smoke1" cx="50%" cy="50%" r="50%">
          <stop offset="0%"   stop-color="#94a3b8" stop-opacity=".07"/>
          <stop offset="100%" stop-color="#94a3b8" stop-opacity="0"/>
        </radialGradient>
        <radialGradient id="smoke2" cx="50%" cy="50%" r="50%">
          <stop offset="0%"   stop-color="#7c3aed" stop-opacity=".06"/>
          <stop offset="100%" stop-color="#7c3aed" stop-opacity="0"/>
        </radialGradient>
      </defs>

      <rect x="0" y="0" :width="W" height="64" fill="rgba(5,8,25,0.65)"/>

      <circle v-for="s in stars1" :key="s.id" :class="['star', s.cls]" :cx="s.x * W" :cy="s.cy" :r="s.r" :fill="s.fill" :opacity="s.op"/>
      <circle v-for="s in stars2" :key="s.id" :class="['star', s.cls]" :cx="s.x * W" :cy="s.cy" :r="s.r" :fill="s.fill" :opacity="s.op"/>
      <circle v-for="s in stars3" :key="s.id" :class="['star', s.cls]" :cx="s.x * W" :cy="s.cy" :r="s.r" :fill="s.fill" :opacity="s.op"/>

      <ellipse class="smoke smk-a" :cx="W * 0.222" cy="55" :rx="W * 0.2"  ry="16" fill="url(#smoke1)"/>
      <ellipse class="smoke smk-b" :cx="W * 0.555" cy="53" :rx="W * 0.244" ry="20" fill="url(#smoke2)"/>
      <ellipse class="smoke smk-a" :cx="W * 0.844" cy="56" :rx="W * 0.211" ry="14" fill="url(#smoke1)"/>

      <g v-for="sp in spots" :key="sp.id" :class="['spot', sp.cls]" :style="`transform-origin: ${sp.x * W}px 64px`">
        <polygon :points="`${sp.x*W},64 ${sp.x*W - sp.hw},0 ${sp.x*W + sp.hw},0`" :fill="`url(#${sp.grad})`"/>
        <circle  :cx="sp.x * W" cy="61" :r="sp.r1" :fill="sp.c1"/>
        <circle  :cx="sp.x * W" cy="61" :r="sp.r2" :fill="sp.c2"/>
      </g>

      <rect x="0" y="59" :width="W" height="5" fill="rgba(15,23,42,0.95)"/>
      <rect x="0" y="59" :width="W" height="1" fill="rgba(255,255,255,0.06)"/>

      <line v-for="sp in spots" :key="`foot-${sp.id}`"
        :x1="sp.x * W" y1="59" :x2="sp.x * W" y2="54"
        stroke="rgba(148,163,184,0.28)" stroke-width="1.5"/>

      <g ref="notesLayer"/>
    </svg>

    <svg class="eq-svg" viewBox="0 0 26 64">
      <rect class="eqb eb1" x="0"    y="22" width="1.5" height="20" rx=".75" fill="#22d3ee" opacity=".75"/>
      <rect class="eqb eb2" x="3.5"  y="26" width="1.5" height="12" rx=".75" fill="#a855f7" opacity=".72"/>
      <rect class="eqb eb3" x="7"    y="23" width="1.5" height="18" rx=".75" fill="#22d3ee" opacity=".68"/>
      <rect class="eqb eb4" x="10.5" y="28" width="1.5" height="8"  rx=".75" fill="#ec4899" opacity=".72"/>
      <rect class="eqb eb5" x="14"   y="24" width="1.5" height="16" rx=".75" fill="#a855f7" opacity=".68"/>
      <rect class="eqb eb6" x="17.5" y="22" width="1.5" height="20" rx=".75" fill="#22d3ee" opacity=".75"/>
      <rect class="eqb eb7" x="21"   y="26" width="1.5" height="12" rx=".75" fill="#ec4899" opacity=".68"/>
      <rect class="eqb eb8" x="24.5" y="28" width="1.5" height="8"  rx=".75" fill="#a855f7" opacity=".72"/>
    </svg>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const containerRef = ref<HTMLElement | null>(null)
const W            = ref(900)

let ro: ResizeObserver | null = null

const CLS  = ['sa', 'sb', 'sc'] as const
const FILL = ['#e0f2fe', '#bae6fd', '#bfdbfe']

function star(id: string, x: number, cy: number, r: number, ci: number, cls: typeof CLS[number], op: number) {
  return { id, x, cy, r, fill: FILL[ci % 3], cls, op }
}

const stars1 = [
  star('s1a', 0.024, 6,  .9, 0, 'sa', .75), star('s1b', 0.064, 11, .7, 1, 'sb', .65),
  star('s1c', 0.105, 4,  .8, 0, 'sc', .70), star('s1d', 0.153, 9,  .9, 2, 'sa', .65),
  star('s1e', 0.197, 5,  .7, 0, 'sb', .70), star('s1f', 0.239, 13, .8, 1, 'sc', .60),
  star('s1g', 0.286, 7,  .9, 0, 'sa', .70), star('s1h', 0.331, 11, .7, 2, 'sb', .60),
  star('s1i', 0.375, 4,  .8, 0, 'sc', .65), star('s1j', 0.416, 9,  .9, 1, 'sa', .70),
  star('s1k', 0.461, 5,  .7, 0, 'sb', .65), star('s1l', 0.502, 13, .8, 2, 'sc', .60),
  star('s1m', 0.546, 7,  .9, 0, 'sa', .70), star('s1n', 0.594, 10, .7, 1, 'sb', .65),
  star('s1o', 0.635, 4,  .8, 0, 'sc', .70), star('s1p', 0.68,  8,  .9, 2, 'sa', .65),
  star('s1q', 0.724, 12, .7, 0, 'sb', .60), star('s1r', 0.769, 5,  .8, 1, 'sc', .70),
  star('s1s', 0.813, 9,  .9, 0, 'sa', .65), star('s1t', 0.857, 6,  .7, 2, 'sb', .70),
  star('s1u', 0.902, 11, .8, 0, 'sc', .65), star('s1v', 0.947, 4,  .9, 1, 'sa', .70),
  star('s1w', 0.987, 8,  .7, 0, 'sb', .60),
]
const stars2 = [
  star('s2a', 0.044, 21, .5, 2, 'sc', .45), star('s2b', 0.084, 17, .5, 0, 'sa', .50),
  star('s2c', 0.131, 22, .5, 1, 'sb', .40), star('s2d', 0.175, 18, .5, 0, 'sc', .48),
  star('s2e', 0.22,  23, .5, 2, 'sa', .42), star('s2f', 0.266, 16, .5, 0, 'sb', .50),
  star('s2g', 0.309, 21, .5, 1, 'sc', .45), star('s2h', 0.353, 17, .5, 0, 'sa', .48),
  star('s2i', 0.397, 22, .5, 2, 'sb', .40), star('s2j', 0.439, 18, .5, 0, 'sc', .50),
  star('s2k', 0.483, 23, .5, 1, 'sa', .45), star('s2l', 0.525, 16, .5, 0, 'sb', .42),
  star('s2m', 0.569, 21, .5, 2, 'sc', .48), star('s2n', 0.614, 17, .5, 0, 'sa', .50),
  star('s2o', 0.658, 23, .5, 1, 'sb', .40), star('s2p', 0.702, 18, .5, 0, 'sc', .45),
  star('s2q', 0.747, 22, .5, 2, 'sa', .50), star('s2r', 0.791, 16, .5, 0, 'sb', .45),
  star('s2s', 0.836, 21, .5, 1, 'sc', .42), star('s2t', 0.880, 17, .5, 0, 'sa', .48),
  star('s2u', 0.924, 23, .5, 2, 'sb', .40), star('s2v', 0.967, 19, .5, 0, 'sc', .50),
]
const stars3 = [
  star('s3a', 0.033, 29, .4, 1, 'sb', .30), star('s3b', 0.098, 27, .4, 0, 'sc', .28),
  star('s3c', 0.167, 30, .4, 2, 'sa', .32), star('s3d', 0.247, 26, .4, 0, 'sb', .28),
  star('s3e', 0.339, 29, .4, 1, 'sc', .30), star('s3f', 0.431, 27, .4, 0, 'sa', .32),
  star('s3g', 0.513, 30, .4, 2, 'sb', .28), star('s3h', 0.602, 26, .4, 0, 'sc', .30),
  star('s3i', 0.687, 29, .4, 1, 'sa', .32), star('s3j', 0.778, 27, .4, 0, 'sb', .28),
  star('s3k', 0.867, 30, .4, 2, 'sc', .30), star('s3l', 0.953, 26, .4, 0, 'sa', .32),
]

const spots = [
  { id: 1, x: 0.144, hw: 14, cls: 'spot-1', grad: 'sp1', r1: 3.5, r2: 1.8, c1: 'rgba(34,211,238,0.45)',  c2: 'rgba(34,211,238,0.95)'  },
  { id: 2, x: 0.311, hw: 14, cls: 'spot-2', grad: 'sp2', r1: 3.5, r2: 1.8, c1: 'rgba(168,85,247,0.45)',  c2: 'rgba(168,85,247,0.95)'  },
  { id: 3, x: 0.500, hw: 16, cls: 'spot-3', grad: 'sp3', r1: 4.5, r2: 2.2, c1: 'rgba(236,72,153,0.45)',  c2: 'rgba(236,72,153,0.95)'  },
  { id: 4, x: 0.689, hw: 14, cls: 'spot-4', grad: 'sp4', r1: 3.5, r2: 1.8, c1: 'rgba(245,158,11,0.45)',  c2: 'rgba(245,158,11,0.95)'  },
  { id: 5, x: 0.867, hw: 14, cls: 'spot-5', grad: 'sp5', r1: 3.5, r2: 1.8, c1: 'rgba(34,211,238,0.45)',  c2: 'rgba(34,211,238,0.95)'  },
]

const notesLayer = ref<SVGGElement | null>(null)
const NS     = 'http://www.w3.org/2000/svg'
const GLYPHS: string[] = ['♪', '♫', '♩', '♬']
const COLORS: string[] = ['#22d3ee', '#22d3ee', '#a855f7', '#a855f7', '#ec4899', '#f59e0b']
const COUNT  = 14

const timers: ReturnType<typeof setTimeout>[] = []
const rafIds: number[] = []

function spawnNote() {
  const layer = notesLayer.value!
  if (!layer) return

  const w       = W.value
  const x       = w * 0.03 + Math.random() * w * 0.94
  const startY  = 50 + Math.random() * 8
  const dur     = 3000 + Math.random() * 2500
  const size    = 8 + Math.random() * 5
  const color   = COLORS[Math.floor(Math.random() * COLORS.length)] as string
  const glyph   = GLYPHS[Math.floor(Math.random() * GLYPHS.length)] as string
  const driftX  = (Math.random() - 0.5) * 30

  const el = document.createElementNS(NS, 'text')
  el.setAttribute('font-size',   String(size))
  el.setAttribute('fill',        color)
  el.setAttribute('opacity',     '0')
  el.setAttribute('font-family', 'serif')
  el.setAttribute('x',           String(x))
  el.setAttribute('y',           String(startY))
  el.textContent = glyph
  layer.appendChild(el)

  const start = performance.now()

  function frame(now: number) {
    const t = Math.min((now - start) / dur, 1)
    let op: number
    if      (t < 0.15) op = (t / 0.15) * 0.38
    else if (t < 0.70) op = 0.38
    else               op = ((1 - t) / 0.30) * 0.38

    el.setAttribute('opacity', String(op))
    el.setAttribute('y',       String(startY - t * 28))
    el.setAttribute('x',       String(x + driftX * t))

    if (t < 1) {
      rafIds.push(requestAnimationFrame(frame))
    } else {
      layer.contains(el) && layer.removeChild(el)
      timers.push(setTimeout(spawnNote, 200 + Math.random() * 1200))
    }
  }

  rafIds.push(requestAnimationFrame(frame))
}

onMounted(() => {
  ro = new ResizeObserver((entries) => {
    const w = entries[0]?.contentRect.width
    if (w && w > 0) W.value = Math.round(w)
  })
  if (containerRef.value) {
    ro.observe(containerRef.value)
    W.value = Math.round(containerRef.value.offsetWidth) || 900
  }

  for (let i = 0; i < COUNT; i++) {
    timers.push(setTimeout(spawnNote, i * (4000 / COUNT) * Math.random() * 1.5))
  }
})

onUnmounted(() => {
  ro?.disconnect()
  timers.forEach(clearTimeout)
  rafIds.forEach(cancelAnimationFrame)
})
</script>

<style scoped>
.music-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
  border-radius: inherit;
}
.scene-svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}
.eq-svg {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%); 
  height: 100%; 
  width: auto;
  pointer-events: none;
}

.star { animation: twinkle var(--td, 2.5s) var(--dd, 0s) ease-in-out infinite; }
.sa { --td: 2.1s; --dd: 0.0s; }
.sb { --td: 3.0s; --dd: 0.7s; }
.sc { --td: 1.9s; --dd: 1.3s; }
@keyframes twinkle {
  0%, 100% { opacity: .7; }
  50%       { opacity: .08; }
}
.smoke { animation: smokeDrift var(--sd, 9s) var(--sdd, 0s) ease-in-out infinite; }
.smk-a { --sd: 9s;  --sdd: 0s; }
.smk-b { --sd: 11s; --sdd: 2s; }
@keyframes smokeDrift {
  0%, 100% { transform: translateX(0)     scaleX(1);    opacity: .7; }
  33%       { transform: translateX(10px) scaleX(1.06); opacity: .9; }
  66%       { transform: translateX(-7px) scaleX(.95);  opacity: .5; }
}
.spot-1 { animation: spotSwing 7s   0.0s ease-in-out infinite alternate; }
.spot-2 { animation: spotSwing 5s   1.2s ease-in-out infinite alternate; }
.spot-3 { animation: spotSwing 8s   0.5s ease-in-out infinite alternate; }
.spot-4 { animation: spotSwing 6s   2.0s ease-in-out infinite alternate; }
.spot-5 { animation: spotSwing 5.5s 1.5s ease-in-out infinite alternate; }
@keyframes spotSwing {
  0%   { transform: rotate(-20deg); opacity: .9; }
  50%  { opacity: .45; }
  100% { transform: rotate(20deg);  opacity: .9; }
}
.eqb { transform-box: fill-box; transform-origin: center; }
.eb1 { animation: eq 2.4s 0.00s ease-in-out infinite; }
.eb2 { animation: eq 2.4s 0.30s ease-in-out infinite; }
.eb3 { animation: eq 2.4s 0.60s ease-in-out infinite; }
.eb4 { animation: eq 2.4s 0.90s ease-in-out infinite; }
.eb5 { animation: eq 2.4s 0.15s ease-in-out infinite; }
.eb6 { animation: eq 2.4s 0.45s ease-in-out infinite; }
.eb7 { animation: eq 2.4s 0.75s ease-in-out infinite; }
.eb8 { animation: eq 2.4s 1.05s ease-in-out infinite; }
@keyframes eq {
  0%, 100% { transform: scaleY(0.35); }
  50%       { transform: scaleY(1); }
}
</style>