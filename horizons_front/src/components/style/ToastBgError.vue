<template>
  <svg class="absolute inset-0 w-full h-full" viewBox="0 0 340 80" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
    <defs>
      <radialGradient id="e-platter-l" cx="50%" cy="50%" r="50%">
        <stop offset="0%"   stop-color="#3b0a1e"/>
        <stop offset="45%"  stop-color="#1f0510"/>
        <stop offset="100%" stop-color="#0d0008"/>
      </radialGradient>
      <radialGradient id="e-platter-r" cx="50%" cy="50%" r="50%">
        <stop offset="0%"   stop-color="#3b0a1e"/>
        <stop offset="45%"  stop-color="#1f0510"/>
        <stop offset="100%" stop-color="#0d0008"/>
      </radialGradient>
      <radialGradient id="e-label-l" cx="50%" cy="50%" r="50%">
        <stop offset="0%"   stop-color="#e11d48"/>
        <stop offset="70%"  stop-color="#9f1239"/>
        <stop offset="100%" stop-color="#4c0519"/>
      </radialGradient>
      <radialGradient id="e-label-r" cx="50%" cy="50%" r="50%">
        <stop offset="0%"   stop-color="#be123c"/>
        <stop offset="70%"  stop-color="#881337"/>
        <stop offset="100%" stop-color="#4c0519"/>
      </radialGradient>
    </defs>

    <!-- Fond table de mixage -->
    <rect width="340" height="80" fill="#0d0008"/>
    <!-- Texture surface table -->
    <rect width="340" height="80" fill="rgba(244,63,94,.02)" rx="0"/>

    <!-- ═══ PLATINE GAUCHE ═══ cx=56 -->
    <ellipse cx="56" cy="40" rx="36" ry="36" fill="url(#e-platter-l)" stroke="rgba(244,63,94,.22)" stroke-width=".8"/>
    <!-- Sillons -->
    <circle cx="56" cy="40" r="34" fill="none" stroke="rgba(244,63,94,.16)" stroke-width=".5"/>
    <circle cx="56" cy="40" r="29" fill="none" stroke="rgba(244,63,94,.13)" stroke-width=".5"/>
    <circle cx="56" cy="40" r="24" fill="none" stroke="rgba(200,20,60,.14)" stroke-width=".5"/>
    <circle cx="56" cy="40" r="19" fill="none" stroke="rgba(200,20,60,.13)" stroke-width=".5"/>
    <circle cx="56" cy="40" r="14" fill="none" stroke="rgba(156,16,58,.14)" stroke-width=".5"/>
    <circle cx="56" cy="40" r="9"  fill="none" stroke="rgba(156,16,58,.12)" stroke-width=".5"/>
    <!-- Stroboscope dots — tournent avec le scratch -->
    <g class="e-scratch-l" style="transform-origin:56px 40px">
      <circle cx="56" cy="6"  r="1.3" fill="rgba(244,63,94,.65)"/>
      <circle cx="90" cy="40" r="1.3" fill="rgba(244,63,94,.65)"/>
      <circle cx="56" cy="74" r="1.3" fill="rgba(244,63,94,.65)"/>
      <circle cx="22" cy="40" r="1.3" fill="rgba(244,63,94,.65)"/>
      <circle cx="80" cy="16" r="1"   fill="rgba(244,63,94,.45)"/>
      <circle cx="80" cy="64" r="1"   fill="rgba(244,63,94,.45)"/>
      <circle cx="32" cy="16" r="1"   fill="rgba(244,63,94,.45)"/>
      <circle cx="32" cy="64" r="1"   fill="rgba(244,63,94,.45)"/>
    </g>
    <!-- Étiquette centrale gauche -->
    <circle cx="56" cy="40" r="10"  fill="url(#e-label-l)"/>
    <circle cx="56" cy="40" r="2.8" fill="rgba(10,0,5,.9)"/>
    <circle cx="56" cy="40" r="1.1" fill="rgba(252,165,165,.6)"/>
    <!-- Halo scratch -->
    <circle class="e-halo" cx="56" cy="40" r="34" fill="none" stroke="rgba(244,63,94,.28)" stroke-width="1.5"/>
    <!-- Bras de lecture gauche -->
    <g class="e-arm-l" style=" transform-origin:95px 10px">
      <line x1="95" y1="10" x2="72" y2="48" stroke="rgba(252,165,165,.5)" stroke-width="1.2" stroke-linecap="round"/>
      <circle cx="95" cy="10" r="3.2" fill="rgba(244,63,94,.3)" stroke="rgba(252,165,165,.45)" stroke-width=".8"/>
      <rect x="68" y="46.5" width="8" height="3.5" rx="1" fill="rgba(244,63,94,.55)" stroke="rgba(252,165,165,.35)" stroke-width=".5"/>
    </g>

    <!-- ═══ MIXER CENTRAL ═══ x=112..228 -->
    <rect x="112" y="4" width="116" height="72" rx="3" fill="rgba(22,4,12,.95)" stroke="rgba(244,63,94,.18)" stroke-width=".7"/>

    <!-- Crossfader rail -->
    <rect x="120" y="62" width="100" height="6"  rx="3" fill="rgba(50,5,20,.9)"  stroke="rgba(244,63,94,.2)" stroke-width=".5"/>
    <rect class="e-xfader" x="122" y="63" width="20" height="4" rx="2" fill="rgba(244,63,94,.65)"/>

    <!-- 4 canaux de faders -->
    <!-- Canal 1 -->
    <rect x="124" y="12" width="4"  height="40" rx="2" fill="rgba(70,8,28,.8)"  stroke="rgba(244,63,94,.18)" stroke-width=".4"/>
    <rect class="e-fader ef1" x="122" y="28" width="8"  height="5"  rx="2" fill="rgba(244,63,94,.75)"/>
    <!-- Canal 2 -->
    <rect x="138" y="12" width="4"  height="40" rx="2" fill="rgba(70,8,28,.8)"  stroke="rgba(244,63,94,.18)" stroke-width=".4"/>
    <rect class="e-fader ef2" x="136" y="20" width="8"  height="5"  rx="2" fill="rgba(244,63,94,.7)"/>
    <!-- Canal 3 -->
    <rect x="152" y="12" width="4"  height="40" rx="2" fill="rgba(70,8,28,.8)"  stroke="rgba(244,63,94,.18)" stroke-width=".4"/>
    <rect class="e-fader ef3" x="150" y="36" width="8"  height="5"  rx="2" fill="rgba(190,18,60,.7)"/>
    <!-- Canal 4 -->
    <rect x="166" y="12" width="4"  height="40" rx="2" fill="rgba(70,8,28,.8)"  stroke="rgba(244,63,94,.18)" stroke-width=".4"/>
    <rect class="e-fader ef4" x="164" y="24" width="8"  height="5"  rx="2" fill="rgba(244,63,94,.65)"/>

    <!-- Boutons EQ (treble / mid / bass par canal) -->
    <!-- Col 1 -->
    <circle cx="126" cy="56" r="3" fill="rgba(60,5,22,.9)" stroke="rgba(244,63,94,.3)" stroke-width=".5"/>
    <!-- Col 2 -->
    <circle cx="140" cy="56" r="3" fill="rgba(60,5,22,.9)" stroke="rgba(244,63,94,.3)" stroke-width=".5"/>
    <!-- Col 3 -->
    <circle cx="154" cy="56" r="3" fill="rgba(60,5,22,.9)" stroke="rgba(244,63,94,.3)" stroke-width=".5"/>
    <!-- Col 4 -->
    <circle cx="168" cy="56" r="3" fill="rgba(60,5,22,.9)" stroke="rgba(244,63,94,.3)" stroke-width=".5"/>

    <!-- Gain knobs rangée haute -->
    <circle cx="126" cy="10" r="2.5" fill="rgba(60,5,22,.9)" stroke="rgba(244,63,94,.25)" stroke-width=".5"/>
    <line x1="126" y1="8" x2="126" y2="6.5" stroke="rgba(252,165,165,.5)" stroke-width=".8"/>
    <circle cx="140" cy="10" r="2.5" fill="rgba(60,5,22,.9)" stroke="rgba(244,63,94,.25)" stroke-width=".5"/>
    <line x1="141" y1="8" x2="142" y2="6.5" stroke="rgba(252,165,165,.5)" stroke-width=".8"/>
    <circle cx="154" cy="10" r="2.5" fill="rgba(60,5,22,.9)" stroke="rgba(244,63,94,.25)" stroke-width=".5"/>
    <line x1="154" y1="8" x2="154" y2="6.5" stroke="rgba(252,165,165,.5)" stroke-width=".8"/>
    <circle cx="168" cy="10" r="2.5" fill="rgba(60,5,22,.9)" stroke="rgba(244,63,94,.25)" stroke-width=".5"/>
    <line x1="167" y1="8" x2="166" y2="6.5" stroke="rgba(252,165,165,.5)" stroke-width=".8"/>

    <!-- VU stéréo (2 colonnes fines, pas de barres animées) -->
    <rect x="182" y="12" width="5" height="48" rx="2" fill="rgba(50,5,20,.8)" stroke="rgba(244,63,94,.15)" stroke-width=".4"/>
    <rect x="190" y="12" width="5" height="48" rx="2" fill="rgba(50,5,20,.8)" stroke="rgba(244,63,94,.15)" stroke-width=".4"/>
    <!-- Segments VU fixes (niveaux dessinés statiquement) -->
    <rect x="183" y="36" width="3" height="24" rx="1" fill="rgba(244,63,94,.3)"/>
    <rect x="191" y="30" width="3" height="30" rx="1" fill="rgba(244,63,94,.28)"/>
    <!-- Point rouge peak -->
    <rect class="e-peak" x="183" y="13" width="3" height="3" rx="1" fill="rgba(244,63,94,.0)"/>
    <rect class="e-peak2" x="191" y="13" width="3" height="3" rx="1" fill="rgba(244,63,94,.0)"/>

    <!-- Label mixer -->
    <text x="200" y="44" font-family="monospace" font-size="4.5" fill="rgba(244,63,94,.2)" text-anchor="middle" letter-spacing=".8" transform="rotate(-90,200,44)">DJ MIX</text>

    <!-- ═══ PLATINE DROITE ═══ cx=284 -->
    <ellipse cx="284" cy="40" rx="36" ry="36" fill="url(#e-platter-r)" stroke="rgba(190,18,60,.2)" stroke-width=".8"/>
    <circle cx="284" cy="40" r="34" fill="none" stroke="rgba(190,18,60,.16)" stroke-width=".5"/>
    <circle cx="284" cy="40" r="29" fill="none" stroke="rgba(190,18,60,.13)" stroke-width=".5"/>
    <circle cx="284" cy="40" r="24" fill="none" stroke="rgba(156,16,58,.14)" stroke-width=".5"/>
    <circle cx="284" cy="40" r="19" fill="none" stroke="rgba(156,16,58,.13)" stroke-width=".5"/>
    <circle cx="284" cy="40" r="14" fill="none" stroke="rgba(120,10,40,.14)" stroke-width=".5"/>
    <circle cx="284" cy="40" r="9"  fill="none" stroke="rgba(120,10,40,.12)" stroke-width=".5"/>
    <!-- Stroboscope droite — tourne normalement -->
    <g class="e-spin-r" style="transform-origin:284px 40px">
      <circle cx="284" cy="6"  r="1.3" fill="rgba(190,18,60,.6)"/>
      <circle cx="318" cy="40" r="1.3" fill="rgba(190,18,60,.6)"/>
      <circle cx="284" cy="74" r="1.3" fill="rgba(190,18,60,.6)"/>
      <circle cx="250" cy="40" r="1.3" fill="rgba(190,18,60,.6)"/>
      <circle cx="308" cy="16" r="1"   fill="rgba(190,18,60,.4)"/>
      <circle cx="308" cy="64" r="1"   fill="rgba(190,18,60,.4)"/>
      <circle cx="260" cy="16" r="1"   fill="rgba(190,18,60,.4)"/>
      <circle cx="260" cy="64" r="1"   fill="rgba(190,18,60,.4)"/>
    </g>
    <circle cx="284" cy="40" r="10"  fill="url(#e-label-r)"/>
    <circle cx="284" cy="40" r="2.8" fill="rgba(10,0,5,.9)"/>
    <circle cx="284" cy="40" r="1.1" fill="rgba(252,165,165,.5)"/>
    <!-- Bras droit -->
    <g class="e-arm-r" style="transform-origin:246px 10px">
      <line x1="246" y1="10" x2="268" y2="48" stroke="rgba(252,165,165,.4)" stroke-width="1.2" stroke-linecap="round"/>
      <circle cx="246" cy="10" r="3.2" fill="rgba(190,18,60,.28)" stroke="rgba(252,165,165,.38)" stroke-width=".8"/>
      <rect x="264" y="46.5" width="8" height="3.5" rx="1" fill="rgba(190,18,60,.45)" stroke="rgba(252,165,165,.28)" stroke-width=".5"/>
    </g>
  </svg>
</template>

<style scoped>
/* Platine gauche — scratch saccadé */
.e-scratch-l {
  animation: eScratch .65s ease-in-out infinite alternate;
}
@keyframes eScratch {
  0%   { transform: rotate(-28deg); }
  35%  { transform: rotate(10deg);  }
  65%  { transform: rotate(-20deg); }
  100% { transform: rotate(14deg);  }
}

/* Halo qui pulse au scratch */
.e-halo {
  animation: eHalo .65s ease-in-out infinite alternate;
}
@keyframes eHalo {
  0%   { opacity: .08; }
  100% { opacity: .55; }
}

/* Platine droite — tourne régulièrement */
.e-spin-r {
  animation: eSpinR 2.2s linear infinite;
}
@keyframes eSpinR {
  to { transform: rotate(360deg); }
}

/* Bras droit — légère oscillation de suivi */
.e-arm-l {
  animation: eArmL 0.65s ease-in-out infinite alternate;
}
@keyframes eArmL {
  0%   { transform: rotate(-7deg); }
  35%  { transform: rotate(1deg);  }
  65%  { transform: rotate(-3deg); }
  100% { transform: rotate(2deg);  }
}

/* Bras droit — légère oscillation de suivi */
.e-arm-r {
  animation: eArmR 6s ease-in-out infinite alternate;
}
@keyframes eArmR {
  0%   { transform: rotate(5deg); }
  100% { transform: rotate(0deg);  }
}

/* Pic VU peak */
.e-peak  { animation: ePeak 1.3s .0s ease-in-out infinite; }
.e-peak2 { animation: ePeak 1.3s .4s ease-in-out infinite; }
@keyframes ePeak {
  0%, 70%, 100% { fill: rgba(244,63,94,0);   }
  85%            { fill: rgba(244,63,94,.85); }
}
</style>