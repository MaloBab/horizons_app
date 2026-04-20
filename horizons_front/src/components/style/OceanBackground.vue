<template>
  <div class="ocean-bg">

    <!-- ── Étoiles de fond (radial-gradient) ── -->
    <div class="stars" />

    <!-- ── Lune ── -->
    <div class="moon" />

    <!-- ── Scène SVG ── -->
    <svg class="scene-svg" viewBox="0 0 800 300" preserveAspectRatio="xMidYMid slice">
      <defs>
        <radialGradient id="neb1" cx="50%" cy="50%" r="50%">
          <stop offset="0%"   stop-color="#4f46e5" stop-opacity=".18"/>
          <stop offset="100%" stop-color="#4f46e5" stop-opacity="0"/>
        </radialGradient>
        <radialGradient id="neb2" cx="50%" cy="50%" r="50%">
          <stop offset="0%"   stop-color="#0e7490" stop-opacity=".14"/>
          <stop offset="100%" stop-color="#0e7490" stop-opacity="0"/>
        </radialGradient>
        <radialGradient id="neb3" cx="50%" cy="50%" r="50%">
          <stop offset="0%"   stop-color="#7c3aed" stop-opacity=".12"/>
          <stop offset="100%" stop-color="#7c3aed" stop-opacity="0"/>
        </radialGradient>
        <!-- Gradient du rayon : part du beacon, s'évase -->
        <linearGradient id="beamGrad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%"   stop-color="#ffd54f" stop-opacity=".35"/>
          <stop offset="100%" stop-color="#ffd54f" stop-opacity="0"/>
        </linearGradient>
      </defs>

      <!-- ── Étoiles éparses ── -->
      <circle cx="30"  cy="18"  r="1"   fill="#e0f2fe" opacity=".55" class="star-tw tw-b"/>
      <circle cx="85"  cy="10"  r=".8"  fill="#bfdbfe" opacity=".5"  class="star-tw tw-c"/>
      <circle cx="155" cy="28"  r="1.1" fill="#e0f2fe" opacity=".6"  class="star-tw tw-a"/>
      <circle cx="210" cy="12"  r=".9"  fill="#bfdbfe" opacity=".5"  class="star-tw tw-b"/>
      <circle cx="280" cy="22"  r="1.2" fill="#bfdbfe" opacity=".48" class="star-tw tw-a"/>
      <circle cx="340" cy="14"  r="1"   fill="#e0f2fe" opacity=".5"  class="star-tw tw-c"/>
      <circle cx="390" cy="32"  r=".8"  fill="#bfdbfe" opacity=".42" class="star-tw tw-a"/>
      <circle cx="430" cy="12"  r="1"   fill="#e0f2fe" opacity=".48" class="star-tw tw-b"/>
      <circle cx="460" cy="44"  r=".8"  fill="#e0f2fe" opacity=".35" class="star-tw tw-c"/>
      <circle cx="50"  cy="60"  r=".7"  fill="#e0f2fe" opacity=".32" class="star-tw tw-a"/>
      <circle cx="130" cy="72"  r=".8"  fill="#bfdbfe" opacity=".38" class="star-tw tw-b"/>
      <circle cx="240" cy="55"  r=".7"  fill="#e0f2fe" opacity=".3"  class="star-tw tw-c"/>
      <circle cx="320" cy="68"  r=".8"  fill="#bfdbfe" opacity=".35" class="star-tw tw-a"/>
      <circle cx="490" cy="28"  r=".7"  fill="#e0f2fe" opacity=".32" class="star-tw tw-b"/>

      <!-- ── Nébuleuse ── -->
      <ellipse class="nebula-pulse"      cx="310" cy="112" rx="148" ry="62" fill="url(#neb1)"/>
      <ellipse class="nebula-pulse nb-b" cx="344" cy="98"  rx="100" ry="48" fill="url(#neb2)"/>
      <ellipse class="nebula-pulse nb-c" cx="276" cy="128" rx="84"  ry="42" fill="url(#neb3)"/>

      <!-- Micro-étoiles nébuleuse -->
      <circle cx="228" cy="108" r=".9" fill="white" opacity=".55" class="star-tw tw-a"/>
      <circle cx="252" cy="94"  r=".7" fill="white" opacity=".45" class="star-tw tw-b"/>
      <circle cx="284" cy="104" r="1"  fill="white" opacity=".6"  class="star-tw tw-c"/>
      <circle cx="310" cy="118" r=".8" fill="white" opacity=".5"  class="star-tw tw-a"/>
      <circle cx="332" cy="94"  r=".7" fill="white" opacity=".45" class="star-tw tw-b"/>
      <circle cx="354" cy="110" r=".9" fill="white" opacity=".55" class="star-tw tw-c"/>
      <circle cx="374" cy="96"  r=".7" fill="white" opacity=".45" class="star-tw tw-a"/>
      <circle cx="392" cy="112" r=".8" fill="white" opacity=".5"  class="star-tw tw-b"/>
      <circle cx="265" cy="130" r=".6" fill="white" opacity=".4"  class="star-tw tw-c"/>
      <circle cx="320" cy="136" r=".7" fill="white" opacity=".45" class="star-tw tw-a"/>
      <circle cx="298" cy="84"  r=".8" fill="#c7d2fe" opacity=".6"  class="star-tw tw-b"/>
      <circle cx="340" cy="126" r=".7" fill="#c7d2fe" opacity=".55" class="star-tw tw-c"/>
      <circle cx="372" cy="124" r=".8" fill="#a5f3fc" opacity=".5"  class="star-tw tw-a"/>

      <!-- ════════════════════════════════
           PHARE
           Beacon (centre lanterne) = cx=530 cy=114
           Le rayon part de ce point exact
      ════════════════════════════════ -->


      <!-- Rocher / base -->
      <ellipse cx="530" cy="258" rx="44" ry="12" fill="rgba(20,44,72,0.95)"/>
      <path d="M490,260 Q498,242 510,236 Q518,230 530,230 Q542,230 550,236 Q562,242 570,260 Z"
            fill="rgba(16,38,65,0.98)"/>

      <!-- Corps du phare -->
      <polygon points="517,230 543,230 538,130 522,130" fill="rgba(12,28,52,0.94)"/>

      <!-- Rayures décoratives -->
      <polygon points="518,210 542,210 540,198 519,198" fill="rgba(180,60,60,0.5)"/>
      <polygon points="519,186 541,186 539,174 520,174" fill="rgba(180,60,60,0.4)"/>
      <polygon points="520,162 540,162 538,150 521,150" fill="rgba(180,60,60,0.28)"/>
    
      <!-- Galerie (balcon) -->
      <rect x="513" y="124" width="34" height="6" rx="2" fill="rgba(70,110,155,0.75)"/>
      <line x1="515" y1="124" x2="515" y2="130" stroke="rgba(80,120,160,0.6)" stroke-width="1"/>
      <line x1="522" y1="124" x2="522" y2="130" stroke="rgba(80,120,160,0.6)" stroke-width="1"/>
      <line x1="530" y1="124" x2="530" y2="130" stroke="rgba(80,120,160,0.6)" stroke-width="1"/>
      <line x1="538" y1="124" x2="538" y2="130" stroke="rgba(80,120,160,0.6)" stroke-width="1"/>
      <line x1="545" y1="124" x2="545" y2="130" stroke="rgba(80,120,160,0.6)" stroke-width="1"/>


        <!-- Rayon lumineux — triangle partant du beacon, rotation autour du beacon -->
      <g class="beam">
        <polygon
          points="530,114  250,50  250,178"
          fill="url(#beamGrad)"
        />
      </g>


      <!-- Lanterne -->
      <rect x="518" y="108" width="24" height="18" rx="3"
            fill="rgba(8,20,40,0.92)" stroke="rgba(80,130,180,0.5)" stroke-width=".8"/>
      <rect x="520" y="110" width="9"  height="14" rx="1" fill="rgba(255,213,79,0.28)"/>
      <rect x="531" y="110" width="9"  height="14" rx="1" fill="rgba(255,213,79,0.22)"/>

      <!-- Toit lanterne -->
      <polygon points="516,108 544,108 540,100 520,100" fill="rgba(44,80,124,0.85)"/>
      <line x1="530" y1="100" x2="530" y2="95" stroke="rgba(150,190,230,0.7)" stroke-width="1.2"/>
      <circle cx="530" cy="94" r="2.2" fill="rgba(200,220,240,0.85)"/>

      <!-- Beacon — dessiné EN DERNIER pour passer au-dessus du rayon -->
      <circle class="beacon" cx="530" cy="114" r="5.5" fill="rgba(255,213,79,0.88)"/>

      <!-- Reflet eau -->
      <ellipse cx="530" cy="266" rx="24" ry="5"
               fill="rgba(255,213,79,0.08)" class="nebula-pulse nb-b"/>

      <!-- ════════════════════════════════
           CONSTELLATION — bas gauche
      ════════════════════════════════ -->
      <circle cx="72"  cy="168" r="11" fill="#93c5fd" opacity=".05"/>
      <circle cx="122" cy="154" r="13" fill="#93c5fd" opacity=".06"/>

      <circle cx="26"  cy="188" r="1.8" fill="#93c5fd" opacity=".8"  class="star-tw tw-c"/>
      <circle cx="72"  cy="168" r="2.2" fill="#bfdbfe" opacity=".9"  class="star-tw tw-a"/>
      <circle cx="116" cy="157" r="1.9" fill="#bfdbfe" opacity=".88" class="star-tw tw-b"/>
      <circle cx="128" cy="149" r="2.8" fill="#dbeafe" opacity="1"   class="star-tw tw-a"/>
      <circle cx="175" cy="162" r="2"   fill="#bfdbfe" opacity=".88" class="star-tw tw-c"/>
      <circle cx="202" cy="178" r="1.7" fill="#93c5fd" opacity=".8"  class="star-tw tw-b"/>
      <circle cx="100" cy="190" r="1.5" fill="#7dd3fc" opacity=".72" class="star-tw tw-c"/>
      <circle cx="147" cy="184" r="1.5" fill="#7dd3fc" opacity=".72" class="star-tw tw-a"/>

      <line x1="26"  y1="188" x2="72"  y2="168" stroke="#bfdbfe" stroke-width=".65" opacity=".4"/>
      <line x1="72"  y1="168" x2="116" y2="157" stroke="#bfdbfe" stroke-width=".65" opacity=".42"/>
      <line x1="116" y1="157" x2="128" y2="149" stroke="#bfdbfe" stroke-width=".7"  opacity=".45"/>
      <line x1="128" y1="149" x2="175" y2="162" stroke="#bfdbfe" stroke-width=".65" opacity=".42"/>
      <line x1="175" y1="162" x2="202" y2="178" stroke="#bfdbfe" stroke-width=".6"  opacity=".38"/>
      <line x1="72"  y1="168" x2="100" y2="190" stroke="#93c5fd" stroke-width=".5"  opacity=".3"/>
      <line x1="175" y1="162" x2="147" y2="184" stroke="#93c5fd" stroke-width=".5"  opacity=".3"/>
      <line x1="100" y1="190" x2="147" y2="184" stroke="#7dd3fc" stroke-width=".45" opacity=".25"/>
    </svg>

    <!-- ── Particules ── -->
    <div
      v-for="p in particles"
      :key="p.id"
      class="particle"
      :style="p.style"
    />

    <!-- ── Vagues ── -->
    <svg class="wave wave-1" viewBox="0 0 1440 160" preserveAspectRatio="none">
      <path d="M0,80 C180,140 360,20 540,80 C720,140 900,20 1080,80 C1260,140 1380,40 1440,80 L1440,160 L0,160 Z" />
    </svg>
    <svg class="wave wave-2" viewBox="0 0 1440 160" preserveAspectRatio="none">
      <path d="M0,60 C120,120 300,10 480,70 C660,130 840,15 1020,65 C1200,115 1350,30 1440,60 L1440,160 L0,160 Z" />
    </svg>
    <svg class="wave wave-3" viewBox="0 0 1440 160" preserveAspectRatio="none">
      <path d="M0,100 C150,40 350,130 560,75 C750,25 950,120 1150,65 C1300,25 1400,90 1440,100 L1440,160 L0,160 Z" />
    </svg>

  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'

interface Particle { id: number; style: string }
const particles = ref<Particle[]>([])

onMounted(() => {
  particles.value = Array.from({ length: 30 }, (_, i) => ({
    id: i,
    style: [
      `left:${Math.random() * 100}%`,
      `top:${20 + Math.random() * 55}%`,
      `width:${2 + Math.random() * 3}px`,
      `height:${2 + Math.random() * 3}px`,
      `animation-delay:${(Math.random() * 6).toFixed(2)}s`,
      `animation-duration:${(4 + Math.random() * 5).toFixed(2)}s`,
      `opacity:${(0.3 + Math.random() * 0.6).toFixed(2)}`,
    ].join(';'),
  }))
})
</script>

<style scoped>
.ocean-bg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.stars {
  position: absolute; inset: 0;
  background-image:
    radial-gradient(1px 1px at 10% 15%, rgba(255,255,255,0.7) 0%, transparent 100%),
    radial-gradient(1px 1px at 25% 8%,  rgba(255,255,255,0.5) 0%, transparent 100%),
    radial-gradient(1.5px 1.5px at 40% 20%, rgba(255,255,255,0.6) 0%, transparent 100%),
    radial-gradient(1px 1px at 55% 5%,  rgba(255,255,255,0.4) 0%, transparent 100%),
    radial-gradient(1px 1px at 70% 12%, rgba(255,255,255,0.7) 0%, transparent 100%),
    radial-gradient(1.5px 1.5px at 85% 18%, rgba(255,255,255,0.5) 0%, transparent 100%),
    radial-gradient(1px 1px at 92% 7%,  rgba(255,255,255,0.6) 0%, transparent 100%),
    radial-gradient(1px 1px at 15% 30%, rgba(255,255,255,0.3) 0%, transparent 100%),
    radial-gradient(1px 1px at 60% 25%, rgba(255,255,255,0.4) 0%, transparent 100%),
    radial-gradient(1px 1px at 78% 30%, rgba(255,255,255,0.3) 0%, transparent 100%);
}

.moon {
  position: absolute;
  top: 8%;
  left: 55%;
  transform: translateX(-50%);
  width: clamp(36px, 4vw, 56px);
  height: clamp(36px, 4vw, 56px);
  background: radial-gradient(circle at 35% 35%, #fffde7, #ffd54f 60%, #ff8f00 100%);
  border-radius: 50%;
  box-shadow: 0 0 30px 10px rgba(255,213,79,0.15), 0 0 80px 20px rgba(255,213,79,0.06);
  animation: moonGlow 4s ease-in-out infinite;
}
@keyframes moonGlow {
  0%, 100% { box-shadow: 0 0 30px 10px rgba(255,213,79,0.15), 0 0 80px  20px rgba(255,213,79,0.06); }
  50%       { box-shadow: 0 0 40px 15px rgba(255,213,79,0.25), 0 0 100px 30px rgba(255,213,79,0.10); }
}

.scene-svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

/* ── Étoiles scintillantes ── */
.star-tw { animation: starTwinkle var(--tw-dur, 2.4s) var(--tw-delay, 0s) ease-in-out infinite; }
.tw-a { --tw-dur: 2.1s; --tw-delay: 0s; }
.tw-b { --tw-dur: 3.0s; --tw-delay: 0.6s; }
.tw-c { --tw-dur: 1.8s; --tw-delay: 1.1s; }
@keyframes starTwinkle {
  0%, 100% { opacity: var(--tw-op, 0.85); }
  50%       { opacity: 0.15; }
}

/* ── Nébuleuse ── */
.nebula-pulse { animation: nebPulse 6s ease-in-out infinite; }
.nebula-pulse.nb-b { animation-delay: 0.8s; }
.nebula-pulse.nb-c { animation-delay: 2s; }
@keyframes nebPulse {
  0%, 100% { opacity: .55; }
  50%       { opacity: .9; }
}

/* ── Rayon du phare
   transform-origin sur le beacon exact (530px, 114px dans le viewBox)
   L'animation fait pivoter le triangle autour de ce point
── */
.beam {
  animation: beamSweep 8s ease-in-out infinite;
  transform-origin: 525px 110px;
}
@keyframes beamSweep {
  0%, 100% { transform: rotate(-45deg); opacity: .6; }
  50%       { transform: rotate(-120deg);  opacity: .28; }
}

/* ── Beacon ── */
.beacon { animation: beaconPulse 5s ease-in-out infinite; }
@keyframes beaconPulse {
  0%, 100% { opacity: 1;  filter: drop-shadow(0 0 7px #ffd54f); }
  50%       { opacity: .6; filter: drop-shadow(0 0 2px #ffd54f); }
}

/* ── Particules ── */
.particle {
  position: absolute; border-radius: 50%;
  background: radial-gradient(circle, #67e8f9, #0891b2);
  animation: floatParticle linear infinite;
  pointer-events: none;
}
@keyframes floatParticle {
  0%   { transform: translateY(0)     translateX(0)    scale(1);   opacity: 0; }
  20%  { opacity: 1; }
  50%  { transform: translateY(-18px) translateX(8px)  scale(1.2); }
  80%  { opacity: 0.6; }
  100% { transform: translateY(-35px) translateX(-5px) scale(0.8); opacity: 0; }
}

/* ── Vagues ── */
.wave {
  position: absolute;
  bottom: 0;
  left: -5%;
  width: 110%;
  pointer-events: none;
}
.wave-1 {
  height: clamp(60px, 12%, 110px);
  fill: rgba(6,182,212,0.13);
  animation: waveMove 12s ease-in-out infinite;
  transform-origin: bottom center;
}
.wave-2 {
  height: clamp(48px, 9%, 90px);
  fill: rgba(8,145,178,0.09);
  animation: waveMoveAlt 9s ease-in-out infinite;
  transform-origin: bottom center;
}
.wave-3 {
  height: clamp(38px, 7%, 70px);
  fill: rgba(14,116,144,0.07);
  animation: waveMoveDeep 15s ease-in-out infinite;
  transform-origin: bottom center;
}
@keyframes waveMove {
  0%   { transform: translateX(0)     scaleY(1.0); }
  20%  { transform: translateX(-10px) scaleY(1.4); }
  40%  { transform: translateX(8px)   scaleY(0.6); }
  60%  { transform: translateX(-12px) scaleY(1.3); }
  80%  { transform: translateX(6px)   scaleY(0.7); }
  100% { transform: translateX(0)     scaleY(1.0); }
}
@keyframes waveMoveAlt {
  0%   { transform: translateX(0)    scaleY(0.7); }
  25%  { transform: translateX(10px) scaleY(1.4); }
  50%  { transform: translateX(-8px) scaleY(0.5); }
  75%  { transform: translateX(12px) scaleY(1.2); }
  100% { transform: translateX(0)    scaleY(0.7); }
}
@keyframes waveMoveDeep {
  0%   { transform: translateX(0)    scaleY(1.2); }
  30%  { transform: translateX(-9px) scaleY(0.5); }
  55%  { transform: translateX(11px) scaleY(1.5); }
  80%  { transform: translateX(-6px) scaleY(0.6); }
  100% { transform: translateX(0)    scaleY(1.2); }
}
</style>