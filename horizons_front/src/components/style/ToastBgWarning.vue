<template>
  <svg class="absolute inset-0 w-full h-full" viewBox="0 0 340 80" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
    <defs>
      <filter id="w-neon-b" x="-40%" y="-40%" width="180%" height="180%">
        <feGaussianBlur stdDeviation="2" result="blur"/>
        <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
      </filter>
      <filter id="w-neon-y" x="-40%" y="-40%" width="180%" height="180%">
        <feGaussianBlur stdDeviation="1.5" result="blur"/>
        <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
      </filter>
      <filter id="w-neon-p" x="-40%" y="-40%" width="180%" height="180%">
        <feGaussianBlur stdDeviation="2" result="blur"/>
        <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
      </filter>
    </defs>

    <!-- Fond mur de béton nocturne -->
    <rect width="340" height="80" fill="#020408"/>
    <line x1="0" y1="20" x2="340" y2="20" stroke="rgba(255,210,0,.015)" stroke-width="5"/>
    <line x1="0" y1="45" x2="340" y2="45" stroke="rgba(255,210,0,.012)" stroke-width="5"/>
    <line x1="0" y1="65" x2="340" y2="65" stroke="rgba(255,210,0,.015)" stroke-width="5"/>

    <!-- ══════════════════════════════════════
         NÉON 1 : méduse bleue  cx≈60 cy≈35
         cloche = demi-ellipse, tentacules tombants
    ══════════════════════════════════════ -->
    <g class="w-neon1" filter="url(#w-neon-b)">
      <!-- Cloche -->
      <path d="M58,44 C58,18 122,18 122,44" fill="none" stroke="rgba(255,210,0,.99)" stroke-width="2.4" stroke-linecap="round"/>
      <!-- Rebord bas -->
      <path d="M58,44 Q90,51 122,44"        fill="none" stroke="rgba(255,210,0,.96)" stroke-width="2"   stroke-linecap="round"/>
      <!-- Nervures internes -->
      <path d="M70,44 C70,28 110,28 110,44"  fill="none" stroke="rgba(255,210,0,.3)"  stroke-width="1"   stroke-linecap="round"/>
      <path d="M80,44 C80,33 100,33 100,44"  fill="none" stroke="rgba(255,210,0,.2)"  stroke-width="1"   stroke-linecap="round"/>
      <!-- Tentacules -->
      <path class="w-tent t1" d="M66,47 C63,57 61,64 63,72" fill="none" stroke="rgba(255,210,0,.88)"  stroke-width="1.5" stroke-linecap="round"/>
      <path class="w-tent t2" d="M76,50 C74,60 73,67 75,75" fill="none" stroke="rgba(255,210,0,.78)"  stroke-width="1.5" stroke-linecap="round"/>
      <path class="w-tent t3" d="M90,51 C90,62 89,69 91,77" fill="none" stroke="rgba(255,210,0,.95)" stroke-width="1.5" stroke-linecap="round"/>
      <path class="w-tent t4" d="M104,50 C106,60 107,67 105,75" fill="none" stroke="rgba(255,210,0,.78)"  stroke-width="1.5" stroke-linecap="round"/>
      <path class="w-tent t5" d="M114,47 C116,57 118,64 117,72" fill="none" stroke="rgba(255,210,0,.82)" stroke-width="1.5" stroke-linecap="round"/>
      <!-- Glow cloche -->
      <path d="M58,44 C58,18 122,18 122,44" fill="none" stroke="rgba(255,210,0,.35)" stroke-width="9" stroke-linecap="round"/>
      <path d="M58,44 Q90,51 122,44"        fill="none" stroke="rgba(255,210,0,.28)" stroke-width="7" stroke-linecap="round"/>
      <!-- Glow tentacules -->
      <path d="M66,47 C63,57 61,64 63,72" fill="none" stroke="rgba(255,210,0,.22)"  stroke-width="5" stroke-linecap="round"/>
      <path d="M76,50 C74,60 73,67 75,75" fill="none" stroke="rgba(255,210,0,.17)" stroke-width="5" stroke-linecap="round"/>
      <path d="M90,51 C90,62 89,69 91,77" fill="none" stroke="rgba(255,210,0,.24)" stroke-width="5" stroke-linecap="round"/>
      <path d="M104,50 C106,60 107,67 105,75" fill="none" stroke="rgba(255,210,0,.17)" stroke-width="5" stroke-linecap="round"/>
      <path d="M114,47 C116,57 118,64 117,72" fill="none" stroke="rgba(255,210,0,.22)"  stroke-width="5" stroke-linecap="round"/>
      <!-- Reflet sol -->
      <ellipse cx="90" cy="77" rx="28" ry="3" fill="rgba(255,210,0,.07)"/>
      <!-- Fil d'alim -->
      <line x1="90" y1="18" x2="90" y2="4" stroke="rgba(255,210,0,.22)" stroke-width=".6" stroke-dasharray="2 3"/>
    </g>

    <!-- ══════════════════════════════════════
         NÉON 2 : étoile de mer jaune  cx=220 cy=38
    ══════════════════════════════════════ -->
    <g class="w-neon2" filter="url(#w-neon-y)">
      <line x1="220" y1="38" x2="220" y2="20" stroke="rgba(255,140,0,.99)"  stroke-width="2.2" stroke-linecap="round"/>
      <line x1="220" y1="38" x2="236" y2="27" stroke="rgba(255,140,0,.99)"  stroke-width="2.2" stroke-linecap="round"/>
      <line x1="220" y1="38" x2="230" y2="54" stroke="rgba(255,140,0,.99)"  stroke-width="2.2" stroke-linecap="round"/>
      <line x1="220" y1="38" x2="210" y2="54" stroke="rgba(255,140,0,.99)"  stroke-width="2.2" stroke-linecap="round"/>
      <line x1="220" y1="38" x2="204" y2="27" stroke="rgba(255,140,0,.99)"  stroke-width="2.2" stroke-linecap="round"/>
      <line x1="220" y1="38" x2="220" y2="20" stroke="rgba(255,140,0,.38)"  stroke-width="7"   stroke-linecap="round"/>
      <line x1="220" y1="38" x2="236" y2="27" stroke="rgba(255,140,0,.38)"  stroke-width="7"   stroke-linecap="round"/>
      <line x1="220" y1="38" x2="230" y2="54" stroke="rgba(255,140,0,.38)"  stroke-width="7"   stroke-linecap="round"/>
      <line x1="220" y1="38" x2="210" y2="54" stroke="rgba(255,140,0,.38)"  stroke-width="7"   stroke-linecap="round"/>
      <line x1="220" y1="38" x2="204" y2="27" stroke="rgba(255,140,0,.38)"  stroke-width="7"   stroke-linecap="round"/>
      <circle cx="220" cy="38" r="3.5" fill="rgba(255,140,0,.95)" stroke="rgba(255,140,0,.3)" stroke-width="2"/>
      <ellipse cx="220" cy="74" rx="18" ry="3" fill="rgba(255,140,0,.06)"/>
      <line x1="220" y1="20" x2="220" y2="4" stroke="rgba(255,140,0,.1)" stroke-width=".6" stroke-dasharray="2 3"/>
    </g>

    <!-- ══════════════════════════════════════
         NÉON 3 : note de musique violette  cx≈290
    ══════════════════════════════════════ -->
    <g class="w-neon3" filter="url(#w-neon-p)">
      <ellipse cx="282" cy="58" rx="7" ry="5" fill="none" stroke="rgba(255,90,0,.99)" stroke-width="2.2" transform="rotate(-20,282,58)"/>
      <line x1="288" y1="55" x2="288" y2="28"  stroke="rgba(255,90,0,.99)"  stroke-width="2.2" stroke-linecap="round"/>
      <path d="M288,28 C304,26 310,36 304,44"   fill="none" stroke="rgba(255,90,0,.99)"  stroke-width="2.2" stroke-linecap="round"/>
      <ellipse cx="282" cy="58" rx="7" ry="5"   fill="none" stroke="rgba(255,90,0,.38)"  stroke-width="8"  transform="rotate(-20,282,58)"/>
      <line x1="288" y1="55" x2="288" y2="28"  stroke="rgba(255,90,0,.38)"  stroke-width="8"  stroke-linecap="round"/>
      <path d="M288,28 C304,26 310,36 304,44"   fill="none" stroke="rgba(255,90,0,.38)"  stroke-width="8"  stroke-linecap="round"/>
      <ellipse cx="290" cy="75" rx="16" ry="3" fill="rgba(255,90,0,.06)"/>
      <line x1="288" y1="28" x2="288" y2="4"   stroke="rgba(255,90,0,.1)" stroke-width=".6" stroke-dasharray="2 3"/>
    </g>
  </svg>
</template>

<style scoped>
/* Méduse — pulsation douce + flicker irrégulier */
.w-neon1 { animation: wJelly 4.3s ease-in-out infinite; }
@keyframes wJelly {
  0%   { opacity: 1; }
  7%   { opacity: .3; }
  9%   { opacity: 1; }
  11%  { opacity: .5; }
  13%  { opacity: 1; }
  58%  { opacity: 1; }
  59%  { opacity: 0; }
  60%  { opacity: .8; }
  61%  { opacity: 0; }
  63%  { opacity: 1; }
  100% { opacity: 1; }
}

/* Tentacules qui ondulent indépendamment */
.w-tent { animation: tentWave var(--td, 2s) var(--tdl, 0s) ease-in-out infinite alternate; }
.t1 { --td: 1.8s; --tdl: 0.0s; }
.t2 { --td: 2.2s; --tdl: 0.3s; }
.t3 { --td: 1.6s; --tdl: 0.6s; }
.t4 { --td: 2.0s; --tdl: 0.9s; }
.t5 { --td: 1.9s; --tdl: 0.4s; }
@keyframes tentWave {
  0%   { transform: translateX(0);   }
  100% { transform: translateX(3px); }
}

/* Étoile — deux micro-coupures rapides */
.w-neon2 { animation: wStar 4.1s ease-in-out infinite; }
@keyframes wStar {
  0%   { opacity: 1; }
  22%  { opacity: 1; }
  23%  { opacity: .1; }
  24%  { opacity: 1; }
  25%  { opacity: .1; }
  26%  { opacity: 1; }
  72%  { opacity: 1; }
  73%  { opacity: .4; }
  75%  { opacity: 1; }
  100% { opacity: 1; }
}

.w-neon3 { animation: wNote 5.2s ease-in-out infinite; }
@keyframes wNote {
  0%   { opacity: 1; }
  32%  { opacity: 1; }
  37%  { opacity: .12; }
  38%  { opacity: .9; }
  39%  { opacity: .12; }
  42%  { opacity: 1; }
  82%  { opacity: 1; }
  84%  { opacity: 0; }
  86%  { opacity: 1; }
  100% { opacity: 1; }
}
</style>