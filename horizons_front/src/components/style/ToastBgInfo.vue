<template>
  <svg class="absolute inset-0 w-full h-full" viewBox="0 0 320 72" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
    <defs>
      <radialGradient id="reel-l" cx="50%" cy="50%" r="50%">
        <stop offset="0%"   stop-color="#1e3a5f"/>
        <stop offset="50%"  stop-color="#0f2744"/>
        <stop offset="100%" stop-color="#071829"/>
      </radialGradient>
      <radialGradient id="reel-r" cx="50%" cy="50%" r="50%">
        <stop offset="0%"   stop-color="#1e3a5f"/>
        <stop offset="50%"  stop-color="#0f2744"/>
        <stop offset="100%" stop-color="#071829"/>
      </radialGradient>
      <radialGradient id="hub-glow" cx="50%" cy="50%" r="50%">
        <stop offset="0%"   stop-color="#38bdf8" stop-opacity=".6"/>
        <stop offset="100%" stop-color="#38bdf8" stop-opacity="0"/>
      </radialGradient>
    </defs>

    <!-- Fond bleu nuit électrique -->
    <rect width="320" height="72" fill="#020c18"/>

    <!-- Boîtier cassette -->
    <rect x="8"  y="6"  width="148" height="60" rx="5" fill="rgba(15,39,68,.9)" stroke="rgba(56,189,248,.2)" stroke-width=".8"/>
    <!-- Détails façade cassette -->
    <rect x="12" y="10" width="140" height="52" rx="3" fill="rgba(7,24,41,.8)"  stroke="rgba(56,189,248,.1)" stroke-width=".5"/>
    <!-- Fenêtre cassette -->
    <rect x="28" y="20" width="108" height="32" rx="6" fill="rgba(2,12,24,.95)" stroke="rgba(56,189,248,.25)" stroke-width=".7"/>

    <!-- Bobine gauche -->
    <g class="reel-spin-l" style="transform-origin: 60px 36px">
      <circle cx="60" cy="36" r="13" fill="url(#reel-l)" stroke="rgba(56,189,248,.3)" stroke-width=".6"/>
      <!-- Rayons de bobine -->
      <line x1="60" y1="23" x2="60" y2="28" stroke="rgba(56,189,248,.5)" stroke-width="1.2" stroke-linecap="round"/>
      <line x1="60" y1="44" x2="60" y2="49" stroke="rgba(56,189,248,.5)" stroke-width="1.2" stroke-linecap="round"/>
      <line x1="47" y1="36" x2="52" y2="36" stroke="rgba(56,189,248,.5)" stroke-width="1.2" stroke-linecap="round"/>
      <line x1="68" y1="36" x2="73" y2="36" stroke="rgba(56,189,248,.5)" stroke-width="1.2" stroke-linecap="round"/>
      <line x1="50" y1="26" x2="54" y2="30" stroke="rgba(56,189,248,.4)" stroke-width="1"   stroke-linecap="round"/>
      <line x1="70" y1="46" x2="66" y2="42" stroke="rgba(56,189,248,.4)" stroke-width="1"   stroke-linecap="round"/>
      <line x1="70" y1="26" x2="66" y2="30" stroke="rgba(56,189,248,.4)" stroke-width="1"   stroke-linecap="round"/>
      <line x1="50" y1="46" x2="54" y2="42" stroke="rgba(56,189,248,.4)" stroke-width="1"   stroke-linecap="round"/>
      <!-- Hub central -->
      <circle cx="60" cy="36" r="5"   fill="rgba(30,58,95,.9)"/>
      <circle cx="60" cy="36" r="2.5" fill="rgba(56,189,248,.3)" stroke="rgba(56,189,248,.5)" stroke-width=".5"/>
      <circle cx="60" cy="36" r="1"   fill="rgba(186,230,253,.7)"/>
    </g>
    <!-- Halo bobine gauche -->
    <circle cx="60" cy="36" r="13" fill="url(#hub-glow)" opacity=".4"/>

    <!-- Bobine droite (tourne à contre-sens, plus petite = moins de ruban) -->
    <g class="reel-spin-r" style="transform-origin: 104px 36px">
      <circle cx="104" cy="36" r="10" fill="url(#reel-r)" stroke="rgba(56,189,248,.3)" stroke-width=".6"/>
      <line x1="104" y1="26" x2="104" y2="30" stroke="rgba(56,189,248,.5)" stroke-width="1.2" stroke-linecap="round"/>
      <line x1="104" y1="42" x2="104" y2="46" stroke="rgba(56,189,248,.5)" stroke-width="1.2" stroke-linecap="round"/>
      <line x1="94"  y1="36" x2="98"  y2="36" stroke="rgba(56,189,248,.5)" stroke-width="1.2" stroke-linecap="round"/>
      <line x1="110" y1="36" x2="114" y2="36" stroke="rgba(56,189,248,.5)" stroke-width="1.2" stroke-linecap="round"/>
      <line x1="97"  y1="29" x2="100" y2="32" stroke="rgba(56,189,248,.4)" stroke-width="1"   stroke-linecap="round"/>
      <line x1="111" y1="43" x2="108" y2="40" stroke="rgba(56,189,248,.4)" stroke-width="1"   stroke-linecap="round"/>
      <circle cx="104" cy="36" r="4"   fill="rgba(30,58,95,.9)"/>
      <circle cx="104" cy="36" r="2"   fill="rgba(56,189,248,.3)" stroke="rgba(56,189,248,.5)" stroke-width=".5"/>
      <circle cx="104" cy="36" r=".8"  fill="rgba(186,230,253,.7)"/>
    </g>
    <circle cx="104" cy="36" r="10" fill="url(#hub-glow)" opacity=".35"/>

    <!-- Ruban magnétique entre les bobines -->
    <path d="M60,48 Q82,54 104,45" fill="none" stroke="rgba(15,118,110,.8)" stroke-width="1.8" stroke-linecap="round"/>
    <path d="M60,49 Q82,55.5 104,46" fill="none" stroke="rgba(20,184,166,.25)" stroke-width=".6"/>

    <!-- Vis de la cassette -->
    <circle cx="20"  cy="18" r="3.5" fill="rgba(15,39,68,.8)" stroke="rgba(56,189,248,.2)" stroke-width=".5"/>
    <circle cx="144" cy="18" r="3.5" fill="rgba(15,39,68,.8)" stroke="rgba(56,189,248,.2)" stroke-width=".5"/>
    <circle cx="20"  cy="54" r="3.5" fill="rgba(15,39,68,.8)" stroke="rgba(56,189,248,.2)" stroke-width=".5"/>
    <circle cx="144" cy="54" r="3.5" fill="rgba(15,39,68,.8)" stroke="rgba(56,189,248,.2)" stroke-width=".5"/>
    <!-- Rainures des vis -->
    <line x1="18" y1="18" x2="22" y2="18" stroke="rgba(56,189,248,.3)" stroke-width=".6"/>
    <line x1="20" y1="16" x2="20" y2="20" stroke="rgba(56,189,248,.3)" stroke-width=".6"/>
    <line x1="142" y1="18" x2="146" y2="18" stroke="rgba(56,189,248,.3)" stroke-width=".6"/>
    <line x1="144" y1="16" x2="144" y2="20" stroke="rgba(56,189,248,.3)" stroke-width=".6"/>

    <!-- Étiquette cassette (bas) -->
    <rect x="32" y="54" width="100" height="6" rx="1.5" fill="rgba(56,189,248,.06)" stroke="rgba(56,189,248,.12)" stroke-width=".4"/>
    <rect x="34" y="55.5" width="40" height="1.5" rx=".75" fill="rgba(56,189,248,.2)"/>
    <rect x="34" y="58"   width="28" height="1.5" rx=".75" fill="rgba(56,189,248,.15)"/>

    <!-- Zone droite : spectre de fréquences -->
    <line x1="172" y1="17" x2="308" y2="17" stroke="rgba(56,189,248,.1)" stroke-width=".5"/>

    <!-- Barres spectre -->
    <rect class="sp sp1"  x="172" y="26" width="5" height="36" rx="2" fill="rgba(56,189,248,.5)"  style="transform-origin:174px 62px"/>
    <rect class="sp sp2"  x="180" y="26" width="5" height="36" rx="2" fill="rgba(14,165,233,.45)" style="transform-origin:182px 62px"/>
    <rect class="sp sp3"  x="188" y="26" width="5" height="36" rx="2" fill="rgba(56,189,248,.55)" style="transform-origin:190px 62px"/>
    <rect class="sp sp4"  x="196" y="26" width="5" height="36" rx="2" fill="rgba(2,132,199,.4)"  style="transform-origin:198px 62px"/>
    <rect class="sp sp5"  x="204" y="26" width="5" height="36" rx="2" fill="rgba(56,189,248,.5)"  style="transform-origin:206px 62px"/>
    <rect class="sp sp6"  x="212" y="26" width="5" height="36" rx="2" fill="rgba(14,165,233,.45)" style="transform-origin:214px 62px"/>
    <rect class="sp sp7"  x="220" y="26" width="5" height="36" rx="2" fill="rgba(56,189,248,.5)"  style="transform-origin:222px 62px"/>
    <rect class="sp sp8"  x="228" y="26" width="5" height="36" rx="2" fill="rgba(2,132,199,.4)"  style="transform-origin:230px 62px"/>
    <rect class="sp sp9"  x="236" y="26" width="5" height="36" rx="2" fill="rgba(56,189,248,.45)" style="transform-origin:238px 62px"/>
    <rect class="sp sp10" x="244" y="26" width="5" height="36" rx="2" fill="rgba(14,165,233,.4)"  style="transform-origin:246px 62px"/>
    <rect class="sp sp11" x="252" y="26" width="5" height="36" rx="2" fill="rgba(56,189,248,.4)"  style="transform-origin:254px 62px"/>
    <rect class="sp sp12" x="260" y="26" width="5" height="36" rx="2" fill="rgba(2,132,199,.35)"  style="transform-origin:262px 62px"/>
    <rect class="sp sp13" x="268" y="26" width="5" height="36" rx="2" fill="rgba(56,189,248,.35)" style="transform-origin:270px 62px"/>
    <rect class="sp sp14" x="276" y="26" width="5" height="36" rx="2" fill="rgba(14,165,233,.3)"  style="transform-origin:278px 62px"/>
    <rect class="sp sp15" x="284" y="26" width="5" height="36" rx="2" fill="rgba(56,189,248,.3)"  style="transform-origin:286px 62px"/>
    <rect class="sp sp16" x="292" y="26" width="5" height="36" rx="2" fill="rgba(2,132,199,.25)"  style="transform-origin:294px 62px"/>
    <rect class="sp sp17" x="300" y="26" width="5" height="36" rx="2" fill="rgba(56,189,248,.25)" style="transform-origin:302px 62px"/>
  </svg>
</template>

<style scoped>
/* Bobines */
.reel-spin-l { animation: spinL 2.4s linear infinite; }
.reel-spin-r { animation: spinR 2.4s linear infinite; }
@keyframes spinL { to { transform: rotate(360deg);  } }
@keyframes spinR { to { transform: rotate(-360deg); } }

/* Barres spectre */
.sp { animation: specBar 1.6s ease-in-out infinite; }
.sp1  { animation-delay: 0.00s; }
.sp2  { animation-delay: 0.10s; }
.sp3  { animation-delay: 0.20s; }
.sp4  { animation-delay: 0.30s; }
.sp5  { animation-delay: 0.40s; }
.sp6  { animation-delay: 0.50s; }
.sp7  { animation-delay: 0.60s; }
.sp8  { animation-delay: 0.70s; }
.sp9  { animation-delay: 0.15s; }
.sp10 { animation-delay: 0.25s; }
.sp11 { animation-delay: 0.35s; }
.sp12 { animation-delay: 0.45s; }
.sp13 { animation-delay: 0.55s; }
.sp14 { animation-delay: 0.65s; }
.sp15 { animation-delay: 0.75s; }
.sp16 { animation-delay: 0.85s; }
.sp17 { animation-delay: 0.95s; }
@keyframes specBar {
  0%, 100% { transform: scaleY(0.15); }
  50%       { transform: scaleY(1);   }
}
</style>